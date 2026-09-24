import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
S=OUT/'submission';F=S/'figures';F.mkdir(exist_ok=True);plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
def read(p):return json.loads(p.read_text())
def save(fig,name):fig.tight_layout();fig.savefig(F/name,dpi=180);plt.close(fig)
st=read(S/'statistics.json');sel=st['selection'];fig,ax=plt.subplots(1,2,figsize=(10,4))
for i,task in enumerate(['map','test']):
 a=[r for r in sel if r['task']==task];ax[i].bar([r['rule'] for r in a],[r['joint_pass'] for r in a],color=['#85929e','#2e86c1','#17a589','#e67e22']);ax[i].set_ylim(0,a[0]['total']);ax[i].set_title(('Old descriptive grid' if task=='map' else 'New frozen test')+f" (denominator {a[0]['total']})");ax[i].set_ylabel('Joint preparation passes');ax[i].set_xlabel('Annotations: passes / total; median CNOTs')
 for j,r in enumerate(a):ax[i].text(j,r['joint_pass'],f"{r['joint_pass']}/{r['total']}\n{r['cnots_quantiles'][2]:g} CNOT",ha='center',va='bottom',fontsize=9)
save(fig,'selection.png')
a=read(OUT/'n8_maps/comparison.json');fig,axes=plt.subplots(1,3,figsize=(12,3.5))
for ax,p in zip(axes,[0,.01,.05]):
 rr=[r for r in a['summary'] if r['p']==p];ax.bar([r['method'] for r in rr],[r['error_mean'] for r in rr],color=['#85929e','#2e86c1','#e67e22']);ax.set_title(f'p={p}; all 420 points');ax.set_ylabel('Mean max |C - C_ED|');ax.set_ylim(0,.5)
save(fig,'noise_comparison.png')
fig,axes=plt.subplots(1,3,figsize=(12,3.5));names={'ferro-like':0,'antiphase-like':1,'paramagnetic-like':2,'uncertain':3,'degraded':4}
from matplotlib.colors import ListedColormap
cm=ListedColormap(['#1f77b4','#ff7f0e','#2ca02c','#bbbbbb','#555555'])
for ax,p in zip(axes,[0,.01,.05]):
 rr=[r for r in a['rows'] if r['p']==p];ks=sorted(set(r['kappa'] for r in rr));hs=sorted(set(r['h'] for r in rr));A=np.array([[names[next(r for r in rr if r['kappa']==k and r['h']==h)['D1']] for h in hs] for k in ks]);im=ax.pcolormesh(hs,ks,A,cmap=cm,vmin=-.5,vmax=4.5,shading='nearest');bad=[r for r in rr if not r['B5_pass']];ax.scatter([r['h'] for r in bad],[r['kappa'] for r in bad],s=10,c='red',marker='x');ax.set_title(f'B5 raw D1, p={p}');ax.set_xlabel('h');ax.set_ylabel('kappa')
fig.colorbar(im,ax=axes.ravel().tolist(),ticks=range(5),shrink=.8).ax.set_yticklabels(list(names));fig.subplots_adjust(right=.8,wspace=.35);fig.savefig(F/'maps.png',dpi=180);plt.close(fig)
if st['end_to_end']:
 fig,axes=plt.subplots(1,2,figsize=(11,4));methods=['B0_raw','B3_raw','B5_raw','B5_zne','B5_sv']
 for ax,p in zip(axes,[.01,.05]):
  rr=[next(r for r in st['end_to_end'] if r['method']==m and r['p']==p and r['shots']==100000 and r['detector']=='D1') for m in methods];x=np.arange(5);correct=[r['anchor_correct_rate'] for r in rr];wrong=[r['anchor_wrong_rate'] for r in rr];reject=[1-c-w for c,w in zip(correct,wrong)];ax.bar(x,correct,label='Correct',color='#148f77');ax.bar(x,wrong,bottom=correct,label='Wrong accepted',color='#c0392b');ax.bar(x,reject,bottom=np.array(correct)+wrong,label='Rejected',color='#bdc3c7');ax.set_xticks(x,methods,rotation=25);ax.set_ylim(0,1);ax.set_title(f'D1, p={p}; {rr[0]["anchor_coordinates"]} anchors × 32');ax.set_ylabel('Fraction of all anchor trials')
 axes[1].legend(fontsize=10);save(fig,'end_to_end.png')
 fig,axes=plt.subplots(1,2,figsize=(11,4))
 for ax,p in zip(axes,[.01,.05]):
  for budget in [10000,100000]:
   rr=[next(r for r in st['end_to_end'] if r['method']==m and r['p']==p and r['shots']==budget and r['detector']=='D1') for m in methods];ax.plot(methods,[r['mse_own_clean'] for r in rr],'-o',label=f'{budget:,} total shots')
  ax.set_title(f'p={p}; MSE to own clean circuit');ax.tick_params(axis='x',rotation=25);ax.legend()
 save(fig,'mitigation.png')
if st['end_to_end']:
 fig,axes=plt.subplots(1,2,figsize=(11,4));methods=['B0_raw','B3_raw','B5_raw','B5_zne','B5_sv']
 for ax,detector in zip(axes,['D1','D3']):
  rr=[next(r for r in st['end_to_end'] if r['method']==m and r['p']==.05 and r['shots']==100000 and r['detector']==detector) for m in methods];x=np.arange(5);correct=np.array([r['anchor_correct_rate'] for r in rr]);wrong=np.array([r['anchor_wrong_rate'] for r in rr]);ax.bar(x,correct,label='Correct',color='#148f77');ax.bar(x,wrong,bottom=correct,label='Wrong accepted',color='#c0392b');ax.bar(x,1-correct-wrong,bottom=correct+wrong,label='Rejected',color='#bdc3c7');ax.set_xticks(x,['B0 raw','B3 raw','B5 raw','B5 ZNE','B5 SV'],rotation=20);ax.set_ylim(0,1.03);ax.set_title(f'{detector}, p=.05; 100k total shots');ax.set_ylabel('Fraction of all 12 anchors × 32 trials')
 axes[0].legend(fontsize=10);save(fig,'strong_noise_detectors.png')
mp=OUT/'floating_validation/index.json'
if mp.exists():
 rows=read(mp);fig,axes=plt.subplots(2,3,figsize=(12,7))
 for j,(k,h) in enumerate([( .6,.2),(.8,.5),(1,.7)]):
  for row in [r for r in rows if r['kappa']==k and r['h']==h and r['init']=='plus']:
   ar=np.load(ROOT/row['archive']);axes[0,j].plot(ar['central_raw'],label=f"N={row['n']}, chi={row['chi_max']}");axes[1,j].plot(np.arange(1,row['n']),ar['entropy'],label=f"chi={row['chi_max']}")
  axes[0,j].set_title(f'kappa={k}, h={h}');axes[0,j].set_xlabel('r');axes[0,j].set_ylabel('Signed bulk C(r)');axes[1,j].set_xlabel('Cut position');axes[1,j].set_ylabel('Entanglement entropy');axes[0,j].legend(fontsize=8)
 save(fig,'floating.png')
d=read(OUT/'dynamics_validation/analysis.json')['new_summary'];fig,ax=plt.subplots(figsize=(7,4))
for p in [0,.01,.05]:
 rr=sorted([r for r in d if r['p']==p],key=lambda r:r['dt']);ax.plot([r['cnots'] for r in rr],[r['error_quantiles'][2] for r in rr],'-o',label=f'p={p}')
ax.set_xlabel('Executed CNOTs through t=2');ax.set_ylabel('Median maximum observable error');ax.legend();save(fig,'dynamics.png')
# Same-coordinate N12 comparison, completed rows only.
p=OUT/'selector_benchmark/n12_192/index.json'
if p.exists():
 large=read(p);old=read(OUT/'selector_benchmark/audit/index.json');test=read(OUT/'selector_benchmark/n12test/index.json');cfg=read(OUT/'selector_frozen.json')['selector'];from annni.stage5_selection import choose
 pairs=[]
 for r in large:
  small=next((a for a in old+test if a['n']==12 and abs(a['kappa']-r['kappa'])<1e-10 and abs(a['h']-r['h'])<1e-10),None)
  if small:pairs.append((choose(small['candidates'],'S2',cfg)['candidate'],r['B5_selection']['candidate']))
 fig,ax=plt.subplots(figsize=(6,4));ax.scatter([a['delta_e'] for a,b in pairs],[b['delta_e'] for a,b in pairs],s=12);ax.set(xscale='log',yscale='log',xlabel='N12 S2 128-cap energy error/site',ylabel='N12 B5 192-cap energy error/site',title=f'{len(pairs)} paired coordinates');ax.axhline(.001,color='gray',ls=':');ax.axvline(.001,color='gray',ls=':');save(fig,'n12.png')
print(F)
if (OUT/'end_to_end/fixed_curves.json').exists():
 cc=read(OUT/'end_to_end/fixed_curves.json');fig,axes=plt.subplots(1,3,figsize=(12,3.7))
 for ax,metric in zip(axes,['full_observable_change','mx_derivative','state_access_chi']):
  for p in [0,.01,.05]:
   row=next(r for r in cc if r['version']=='branches_refined' and r['kappa']==.3 and r['p']==p and r['metric']==metric);ax.plot(row['h_mid'],row['values'],label=f'p={p}')
  ax.set_title(metric.replace('_',' '));ax.set_xlabel('h midpoint');ax.legend(fontsize=8)
 fig.suptitle('Fixed structure, kappa=.3; exact density, step .0125 (not shot-resolved boundary)');save(fig,'local_fixed.png')
if (OUT/'floating_validation/neighbor_checks.json').exists():
 nn=read(OUT/'floating_validation/neighbor_checks.json');fig,axes=plt.subplots(1,3,figsize=(12,3.7))
 for ax,(k,h) in zip(axes,[(.6,.2),(.8,.5),(1,.7)]):
  for n in [96,128]:
   rr=sorted([r for r in nn if r['kappa']==k and r['n']==n],key=lambda r:r['h']);ax.plot([r['h'] for r in rr],[np.mean(r['c']) for r in rr],'o',label=f'new neighbors N{n}')
  for r in read(OUT/'floating_validation/evidence_update.json')['rows']:
   if r['kappa']==k:ax.scatter([h],[np.mean(r['entropy_c'])],marker='s',color='black',label='new center N128')
  old=read(ROOT/'results/stage4_upgrade_v1/floating/evidence_grading.json')['rows']
  for r in old:
   if r['kappa']==k:ax.scatter([r['h']],[np.mean(r['entropy_c'][-2:])],marker='x',color='gray')
  ax.axhline(1,color='gray',ls=':');ax.set_title(f'kappa={k}; old sides gray x');ax.set_xlabel('h (actual sampled points)');ax.set_ylabel('Mean of two entropy-window c fits');ax.legend(fontsize=7)
 save(fig,'floating_neighbors.png')
import csv
riskpath=S/'risk_coverage.csv'
if riskpath.exists():
 rr=list(csv.DictReader(riskpath.open()));fig,axes=plt.subplots(1,2,figsize=(10,3.7))
 for ax,p in zip(axes,[.01,.05]):
  for method in ['B0_raw','B3_raw','B5_raw','B5_zne','B5_sv']:
   points=[r for r in rr if r['method']==method and float(r['p'])==p and r['shots']=='100000' and r['detector']=='D1' and r['risk']];ax.plot([float(r['coverage']) for r in points],[float(r['risk']) for r in points],'-o',label=method,alpha=.65)
  ax.set(xlabel='Accepted / all anchor trials',ylabel='Wrong / accepted',title=f'12 anchors only; observed risk=0, p={p}',xlim=(-.02,1.02),ylim=(-.01,.1));ax.legend(fontsize=7)
 save(fig,'risk_coverage.png')
if (OUT/'n8_maps/maps.npz').exists():
 a=np.load(OUT/'n8_maps/maps.npz');fig,axes=plt.subplots(2,3,figsize=(12,7))
 for i in range(2):
  for j,p in enumerate(a['p']):
   ax=axes[i,j];im=ax.pcolormesh(a['h'],a['kappa'],a['D1_labels'][i,j],cmap=cm,vmin=-.5,vmax=4.5,shading='nearest');ki,hi=np.where(a['preparation_failed']);ax.scatter(a['h'][hi],a['kappa'][ki],s=8,c='red',marker='x');ki,hi=np.where(a['branch_sensitive'][j]);ax.scatter(a['h'][hi],a['kappa'][ki],s=24,facecolors='none',edgecolors='#ffd700',linewidths=.8);ax.set(xlabel='h',ylabel='kappa',title=('B5 raw' if i==0 else 'B5 ZNE')+f', p={p}')
 fig.suptitle('D1: 100k total shots, modal label over32 trials\nRed x: preparation failed | Gold ring: branch sensitive (checked subset)',fontsize=11,y=.98);fig.subplots_adjust(right=.82,hspace=.45,wspace=.35,top=.88);fig.colorbar(im,ax=axes.ravel().tolist(),ticks=range(5),shrink=.6).ax.set_yticklabels(list(names));fig.savefig(F/'full_mitigated_maps.png',dpi=180);plt.close(fig)
# Presentation views keep lettering legible at the deck's actual image size.
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
fig,ax=plt.subplots(figsize=(10,3.5));ax.set(xlim=(0,10),ylim=(0,3.5));ax.axis('off')
for x,title,detail in [(0.2,'Select a circuit','Energy + sector audit'),(3.6,'Execute noisy gates','Every CNOT target'),(7.0,'Diagnose features','Frozen D1 / D3')]:
 box=FancyBboxPatch((x,1.1),2.8,1.5,boxstyle='round,pad=.08',facecolor='#edf4f7',edgecolor='#2471a3',linewidth=1.5);ax.add_patch(box);ax.text(x+1.4,2.1,title,ha='center',fontsize=15,weight='bold');ax.text(x+1.4,1.55,detail,ha='center',fontsize=12)
for x in [3.05,6.45]:ax.add_patch(FancyArrowPatch((x,1.85),(x+.45,1.85),arrowstyle='-|>',mutation_scale=18,color='#2471a3'))
ax.text(5,.4,'Keep preparation bias, gate noise and sampling uncertainty separate',ha='center',fontsize=13);save(fig,'pipeline.png')
if (OUT/'floating_validation/evidence_update.json').exists():
 history=read(OUT/'floating_validation/size_extension_analysis.json')['size_history'] if (OUT/'floating_validation/size_extension_analysis.json').exists() else read(OUT/'floating_validation/center_size_history.json');fig,ax=plt.subplots(figsize=(10,4))
 for k,h in [(.6,.2),(.8,.5),(1,.7)]:
  rows=sorted([r for r in history if r['kappa']==k and r['h']==h],key=lambda r:r['n'])
  ax.errorbar([r['n'] for r in rows],[np.mean(r['c_windows']) for r in rows],yerr=[np.ptp(r['c_windows'])/2 for r in rows],marker='o',capsize=5,label=f'kappa={k}, h={h}')
 ax.axhline(1,color='gray',ls=':');ax.set_xlabel('OBC system size N',fontsize=13);ax.set_ylabel('Freely fitted entropy coefficient c',fontsize=13);ax.tick_params(labelsize=12);ax.legend(fontsize=12);ax.set_title('Bars span the two fit windows; they are not confidence intervals',fontsize=12);save(fig,'floating_size.png')

# N12 actual execution cost contrast; no missing coordinates are imputed.
if (OUT/'n12_scaling/analysis.json').exists():
 nn=read(OUT/'n12_scaling/analysis.json');noise=nn['noise'];mit=nn['mitigation']
 if noise and mit:
  fig,axes=plt.subplots(1,3,figsize=(12,3.8));arms=['S0_128','S2_128','S2_192'];x=np.arange(len(arms))
  for ax,p in zip(axes[:2],[.01,.05]):
   rows=[next(r for r in noise if r['p']==p and r['arm']==arm) for arm in arms];ax.bar(x,[r['mean'] for r in rows]);ax.set_xticks(x,arms,rotation=20);ax.set_ylabel('Mean maximum C(r) error to ED');ax.set_title(f'N12, p={p}, {rows[0]["count"]} paired points')
  upper=max(ax.get_ylim()[1] for ax in axes[:2]);[ax.set_ylim(0,upper) for ax in axes[:2]]
  for method in ['raw','sv']:
   rows=[r for r in mit if r['shots']==100000 and r['method']==method];axes[2].plot([r['p'] for r in rows],[r['MSE_own_clean'] for r in rows],marker='o',label=method)
  axes[2].set(xlabel='CNOT target noise p',ylabel='MSE to own clean circuit',title='6 coordinates; 100k total shots');axes[2].legend();save(fig,'n12_noise.png')
