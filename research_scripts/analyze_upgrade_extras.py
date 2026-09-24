import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.upgrade_adapt import *
from annni.upgrade_detection import predict
O=OUT/'submission';F=O/'figures';F.mkdir(exist_ok=True)
# Finite shot diagnostic variation comes from actual mitigation samples, no retraining.
cfg=json.loads((OUT/'detection/frozen.json').read_text());rows=[]
for r in json.loads((OUT/'mitigation/index.json').read_text()):
 a=np.load(ROOT/r['archive']);clean=predict(a['ideal'],cfg)
 for method in ['raw','zne','sv']:
  for budget in [10000,100000]:
   preds=[predict(v,cfg) for v in a[f'{method}_{budget}']]
   rows.append(dict(kappa=r['kappa'],h=r['h'],p=r['p'],method=method,total_shots=budget,replicates=len(preds),D1_clean_reference=clean['D1'],D3_clean_reference=clean['D3'],D1_agree=sum(x['D1']==clean['D1'] for x in preds),D3_agree=sum(x['D3']==clean['D3'] for x in preds),D1_rejected=sum(x['D1'] in ['uncertain','degraded'] for x in preds),interpretation='agreement with own circuit clean diagnostic, not independent physical classification accuracy'))
dump(OUT/'detection/shot_sensitivity.json',rows)
if (OUT/'fixed_branches/curves.json').exists():
 curves=json.loads((OUT/'fixed_branches/curves.json').read_text());fig,axs=plt.subplots(2,3,figsize=(12,6))
 for j,k in enumerate([0,.3,.8]):
  for row in curves:
   if row['kappa']!=k or row['anchor_h']!=1 or row['stride']!=1:continue
   axs[0,j].plot(row['h_mid'],row['change'],label=f"p={row['p']}");axs[1,j].plot(row['h_mid'],row['chi'],label=f"p={row['p']}")
  axs[0,j].set(title=f'Fixed structure, kappa={k}',ylabel='D1 change');axs[1,j].set(xlabel='h midpoint',ylabel='D2 susceptibility');axs[0,j].legend()
 fig.tight_layout();fig.savefig(F/'fixed_branch_diagnostics.png',dpi=160);plt.close(fig)
 # No fabricated exact boundaries: all local peaks, nested-grid support, eligibility retained.
 peaks=json.loads((OUT/'fixed_branches/peaks.json').read_text());matches=[]
 from annni.upgrade_detection import peak_support_mask
 for peak in peaks:
  curve=next(c for c in curves if all(c[key]==peak[key] for key in ['kappa','anchor_h','p','stride']))
  j=int(np.argmin(abs(np.array(curve['h_mid'])-peak['h'])))
  peak['support_preparation_pass']=bool(peak_support_mask(curve['quality'])[j])
  peak['validation_support']=[curve['h'][max(0,j-1)],curve['h'][min(len(curve['h'])-1,j+2)]]
 dump(OUT/'fixed_branches/peaks_with_support.json',peaks)
 for k in [0,.3,.8]:
  for anchor in [.5,1.]:
   for p in [.01,.05]:
    for metric in ['change','mx','chi']:
     clean=[r for r in peaks if r['kappa']==k and r['anchor_h']==anchor and r['p']==0 and r['metric']==metric and r['stride']==1 and r['support_preparation_pass']];noisy=[r for r in peaks if r['kappa']==k and r['anchor_h']==anchor and r['p']==p and r['metric']==metric and r['stride']==1 and r['support_preparation_pass']]
     if not clean or not noisy:continue
     a=max(clean,key=lambda x:x['value']);b=min(noisy,key=lambda x:abs(x['h']-a['h']));interval=[b['support'][0]-a['support'][1],b['support'][1]-a['support'][0]]
     coarse=[r for r in peaks if r['kappa']==k and r['anchor_h']==anchor and r['p']==p and r['metric']==metric and r['stride']==2 and r['support_preparation_pass']];stable=any(abs(r['h']-b['h'])<=.2 for r in coarse)
     matches.append(dict(kappa=k,anchor_h=anchor,p=p,metric=metric,clean_peak=a,noisy_peak=b,shift=b['h']-a['h'],grid_resolution_interval=interval,coarse_support=stable,statistical_confidence_interval=False,nonzero_single_metric=bool(stable and (interval[0]>0 or interval[1]<0))))
 dump(OUT/'fixed_branches/shift_candidates.json',matches)
# Spatial fits and truncation evidence for each N/chi with both raw/connected data.
if (OUT/'floating/refine_index.json').exists():
 a=json.loads((OUT/'floating/refine_index.json').read_text());pairs=[]
 for r in a:
  for s in a:
   if (r['n'],r['kappa'],r['h'],r['init'])==(s['n'],s['kappa'],s['h'],s['init']) and s['chi_max']==2*r['chi_max']:
    x=np.load(ROOT/r['archive']);y=np.load(ROOT/s['archive']);pairs.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],chi_low=r['chi_max'],chi_high=s['chi_max'],energy_per_site_difference=abs(r['energy']-s['energy'])/r['n'],max_correlation_change=float(max(abs(x['central_raw']-y['central_raw']))),max_entropy_change=float(max(abs(x['entropy']-y['entropy']))),c_fit_difference=abs(r['entropy_fits'][-1]['c']-s['entropy_fits'][-1]['c']),actual_chi=s['actual_chi'],max_discarded_weight=s['max_discarded_weight']))
 dump(OUT/'floating/convergence_comparison.json',pairs)
 centers=json.loads((OUT/'floating/candidate_windows.json').read_text())['centers'];fig,axs=plt.subplots(2,3,figsize=(12,6),sharey='row')
 for j,(k,h) in enumerate(centers):
  sel=sorted([r for r in a if r['kappa']==k and r['h']==h and r['init']=='plus'],key=lambda r:(r['n'],r['chi_max']))
  for n in [32,64,96]:
   cand=[r for r in sel if r['n']==n]
   if not cand:continue
   row=cand[-1];z=np.load(ROOT/row['archive']);axs[0,j].plot(np.arange(len(z['central_raw'])),z['central_raw'],label=f"N={n}, chi={row['chi_max']}");axs[1,j].plot(np.arange(1,n)/n,z['entropy'],label=f'N={n}')
  axs[0,j].set(title=f'kappa={k}, h={h}, OBC',xlabel='Separation r',ylabel='Central raw C(r)');axs[1,j].set(xlabel='Cut / N',ylabel='Entanglement entropy');axs[0,j].legend(fontsize=8)
 fig.tight_layout();fig.savefig(F/'floating_correlations_entropy.png',dpi=160);plt.close(fig)
print('Extra diagnostics regenerated')
# Repeated-sampling uncertainty of local-window diagnostic peaks, retaining endpoints.
from scipy.signal import find_peaks
mit=json.loads((OUT/'mitigation/index.json').read_text());window_rows=[]
for k,hs in PLAN['mitigation_windows']:
 for p in [.01,.05]:
  entries=[next(r for r in mit if r['kappa']==k and r['h']==h and r['p']==p) for h in hs];data=[np.load(ROOT/r['archive']) for r in entries]
  for method in ['raw','zne','sv']:
   for budget in [10000,100000]:
    positions=[];rep_rows=[]
    for rep in range(PLAN['mitigation_replicates']):
     mx=np.array([d[f'{method}_{budget}'][rep,-1] for d in data]);dy=abs(np.diff(mx))/np.diff(hs);mid=(np.array(hs[:-1])+hs[1:])/2;local=list(find_peaks(dy)[0]);global_peak=int(np.argmax(dy));value=float(mid[global_peak]);positions.append(value);rep_rows.append(dict(rep=rep,h=value,support=[hs[global_peak],hs[global_peak+1]],endpoint=global_peak in [0,len(dy)-1],interior_local_peaks=[float(mid[j]) for j in local]))
    window_rows.append(dict(kappa=k,p=p,method=method,total_shots=budget,fields=hs,replicates=rep_rows,location_quantiles=np.quantile(positions,[.025,.5,.975]).tolist(),interpretation='Empirical repeated-shot quantiles on a fixed finite grid, not a thermodynamic or guaranteed statistical confidence interval',grid_step=np.diff(hs).tolist(),feature='absolute transverse-magnetization difference rate',smoothing=None))
dump(OUT/'mitigation/window_peak_sampling.json',window_rows)
# Same-coordinate N8/N12 comparison; each error is against ED of its own size.
if (OUT/'map/noise_index.json').exists() and (OUT/'n12/noise_index.json').exists():
 n8=json.loads((OUT/'map/noise_index.json').read_text());n12=json.loads((OUT/'n12/noise_index.json').read_text());fig,axs=plt.subplots(2,3,figsize=(12,6),sharex=True,sharey=True)
 for i,p in enumerate([.01,.05]):
  for j,k in enumerate([0,.3,.8]):
   points=sorted([r for r in n12 if r['kappa']==k],key=lambda r:r['h']);hs=[r['h'] for r in points];y12=[next(s for s in r['noise'] if s['p']==p)['epsilon_c_total'] for r in points];y8=[]
   for h in hs:
    row=next(r for r in n8 if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12);y8.append(next(s for s in row['methods']['B3'] if s['p']==p)['epsilon_c_total'])
   ax=axs[i,j];ax.plot(hs,y8,'o-',label='N8');ax.plot(hs,y12,'s--',label='N12');
   for x,r in enumerate(points):
    if not r['row']['joint_pass']:ax.scatter(hs[x],y12[x],c='red',marker='x',s=40,zorder=4)
   ax.set(title=f'kappa={k}, p={p}',xlabel='h',ylabel='Total correlation error');ax.legend()
 fig.suptitle('Same-coordinate total errors; red x marks N12 preparation failure');fig.tight_layout();fig.savefig(F/'size_comparison.png',dpi=160);plt.close(fig)

# A qualified local case, fixed structure and four-node preparation support.
curves=json.loads((OUT/'fixed_branches/curves.json').read_text())
fig,axs=plt.subplots(1,3,figsize=(12,3.7))
for ax,metric,title in zip(axs,['change','mx','chi'],['Full observable change','Absolute dMx/dh','Squared Uhlmann susceptibility']):
 for row in curves:
  if row['kappa']==.3 and row['anchor_h']==.5 and row['stride']==1:
   ax.plot(row['h_mid'],row[metric],label=f"p={row['p']}")
 ax.axvspan(.4,.5,color='grey',alpha=.2);ax.set(xlim=(.25,.75),xlabel='h midpoint',ylabel=title);ax.legend()
fig.suptitle('N8, kappa=.3, fixed structure: matched local peak in [0.4,0.5]; no resolved shift')
fig.tight_layout();fig.savefig(F/'qualified_local_case.png',dpi=160);plt.close(fig)
