"""Regenerate all numerical summaries and eight main figure families from archives."""
import sys,json,csv,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from annni.upgrade_adapt import *
from annni.upgrade_detection import *
from annni.upgrade_accounting import search_cost
S=OUT/'submission';F=S/'figures';F.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':10,'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False})
def read(p):return json.loads((ROOT/p).read_text())
def save(name):plt.savefig(F/(name+'.png'),dpi=160,bbox_inches='tight');plt.close()
def csvwrite(path,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with open(path,'w') as f:
  w=csv.DictWriter(f,keys);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
stats={};allruns=[];checkpoints=[]
for p in sorted((OUT/'adaptive/cache').glob('*.json')):
 r=json.loads(p.read_text());allruns.append({k:r[k] for k in ['n','kappa','h','ref','seed','method','group_first','energy','delta_e','fidelity','epsilon_c','epsilon_sf','epsilon_mx','joint_pass','state_pass','observable_pass','seconds','nfev','nit','stop','archive']}|dict(cnots=r['selected']['cnots'],optimizer_success=r['selected']['optimizer_success'],raw_append_round_counter=r['pool_gradient_evaluations'],**search_cost(r)))
 for c in r['checkpoints']:checkpoints.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],ref=r['ref'],seed=r['seed'],method=r['method'],cnots=c['cnots'],delta_e=c['delta_e'],fidelity=c['fidelity'],joint_pass=c['joint_pass']))
csvwrite(OUT/'all_optimization_runs.csv',allruns);csvwrite(OUT/'all_checkpoints.csv',checkpoints)
for task in ['development','validation','heldout','map','n12']:
 p=OUT/task/'index.json'
 if not p.exists():continue
 rows=json.loads(p.read_text());summary={}
 for method in rows[0]['methods']:
  a=[r['methods'][method] for r in rows];summary[method]=dict(points=len(a),passed=sum(r['joint_pass'] for r in a),median_cnots=float(np.median([r['selected']['cnots'] for r in a])),min_cnots=min(r['selected']['cnots'] for r in a),max_cnots=max(r['selected']['cnots'] for r in a),median_delta_e=float(np.median([r['delta_e'] for r in a])),failures=[dict(kappa=r['kappa'],h=r['h'],delta_e=r['delta_e'],fidelity=r['fidelity'],epsilon_c=r['epsilon_c'],epsilon_sf=r['epsilon_sf'],epsilon_mx=r['epsilon_mx']) for r in a if not r['joint_pass']])
 stats[task]=summary
# Seed stability across each reference and selected seed within fixed reference set.
dev=json.loads((OUT/'development/index.json').read_text());stability=[]
for point in dev:
 for ref in PLAN['refs']:
  a=[r for r in point['candidates'] if r['method']=='cost' and r['ref']==ref];stability.append(dict(kappa=point['kappa'],h=point['h'],ref=ref,passes=sum(r['joint_pass'] for r in a),seeds=len(a),best_energy=min(r['energy'] for r in a),median_delta_e=float(np.median([r['delta_e'] for r in a])),best_fidelity=max(r['fidelity'] for r in a)))
csvwrite(OUT/'seed_stability.csv',stability)
seed_selected=[]
for point in dev:
 winners=[select([r for r in point['candidates'] if r['method']=='cost' and r['seed']==seed]) for seed in PLAN['development_seeds']]
 seed_selected.append(dict(kappa=point['kappa'],h=point['h'],seeds=len(winners),joint_passes=sum(r['joint_pass'] for r in winners),observable_passes=sum(r['observable_pass'] for r in winners),state_passes=sum(r['state_pass'] for r in winners),best_energy=min(r['energy'] for r in winners),median_delta_e=float(np.median([r['delta_e'] for r in winners])),median_fidelity=float(np.median([r['fidelity'] for r in winners])),median_epsilon_c=float(np.median([r['epsilon_c'] for r in winners])),median_epsilon_sf=float(np.median([r['epsilon_sf'] for r in winners])),median_epsilon_mx=float(np.median([r['epsilon_mx'] for r in winners])),archives=[r['archive'] for r in winners]))
csvwrite(OUT/'seed_selected_stability.csv',seed_selected)
stats['development_stability']=seed_selected

fig,ax=plt.subplots(1,2,figsize=(10,3.8));a=[r for r in checkpoints if r['n']==8 and r['method']=='cost'];ax[0].scatter([r['cnots'] for r in a],[max(r['delta_e'],1e-10) for r in a],s=5,alpha=.2);ax[0].axhline(.001,c='black',ls='--');ax[0].set(xlabel='Literal CNOT count',ylabel='Energy error per spin',yscale='log',title='All saved ADAPT checkpoints')
ax[1].hist([r['passes']/r['seeds'] for r in stability],bins=[-.05,.16,.5,.84,1.05]);ax[1].set(xlabel='Passing seed fraction within a reference',ylabel='Development point/reference groups',title='Three independent starts');save('calibration_stability')
# matched map and B0 historic data
if (OUT/'map/noise_index.json').exists():
 grid=json.loads((OUT/'map/index.json').read_text());noise=json.loads((OUT/'map/noise_index.json').read_text());old=read('results/stage3_v1/grid/observations.json');oldsel=read('results/stage3_v1/grid/selection_frozen.json')['rows'];lookup={(round(r['kappa'],6),round(r['h'],6),r['p']):r for r in old};oldstates={(round(r['kappa'],6),round(r['h'],6)):r for r in oldsel};cfg=json.loads((OUT/'detection/frozen.json').read_text())
 matched=[];arrays={};ed=np.load(ROOT/'results/baseline/grid_n8.npz');labels=cfg['labels'];colors=['#2a788e','#a65b9a','#e9c46a','#555555','#dddddd'];cmap=ListedColormap(colors);norm=BoundaryNorm(np.arange(-.5,5),5)
 for method in ['B0','B3','B4']:
  for p in [0,.01,.05]:
   field=np.full((21,20),np.nan);sf0=field.copy();mx=field.copy();failed=field.copy()
   for point in noise:
    k,h=point['kappa'],point['h'];i=round(k/.05);j=round(h/.1)-1;new=next(r for r in point['methods'][method if method!='B0' else 'B3'] if r['p']==p);r=lookup[round(k,6),round(h,6),p] if method=='B0' else new;a=np.load(ROOT/r['archive']);v=vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx'])));diag=predict(v,cfg);field[i,j]=labels.index(diag['D1']);sf0[i,j]=a['structure_factor'][0];mx[i,j]=float(a['mx']);fail=r['preparation_failed'] if method=='B0' else not r['prep_joint_pass'];failed[i,j]=fail
    if method in ['B3','B4']:
     b=lookup[round(k,6),round(h,6),p];matched.append(dict(method=method,kappa=k,h=h,p=p,new_pass=not fail,old_pass=not b['preparation_failed'],common_pass=not fail and not b['preparation_failed'],new_cnots=r['cnots'],old_cnots=192,epsilon_c_new=r['epsilon_c_total'],epsilon_c_old=b['epsilon_c_total'],epsilon_sf_new=r['epsilon_sf_total'],epsilon_sf_old=b['epsilon_sf_total'],epsilon_mx_new=r['epsilon_mx_total'],epsilon_mx_old=b['epsilon_mx_total']))
   arrays[method,p]=(field,sf0,mx,failed)
 csvwrite(OUT/'matched_grid.csv',matched);stats['matched']={}
 for method in ['B3','B4']:
  for p in [0,.01,.05]:
   for mask in ['all','common_pass']:
    a=[r for r in matched if r['method']==method and r['p']==p and (mask=='all' or r['common_pass'])];stats['matched'][f'{method}_p{p}_{mask}']=dict(points=len(a),c_error_mean_new=float(np.mean([r['epsilon_c_new'] for r in a])),c_error_mean_old=float(np.mean([r['epsilon_c_old'] for r in a])),c_improved=sum(r['epsilon_c_new']<r['epsilon_c_old'] for r in a),sf_error_mean_new=float(np.mean([r['epsilon_sf_new'] for r in a])),sf_error_mean_old=float(np.mean([r['epsilon_sf_old'] for r in a])),mx_error_mean_new=float(np.mean([r['epsilon_mx_new'] for r in a])),mx_error_mean_old=float(np.mean([r['epsilon_mx_old'] for r in a])))
 # Same-size ED finite-grid diagnostic: strongest interior |dMx/dh| peak.
 from scipy.signal import find_peaks
 edline=[]
 for ki,k in enumerate(ed['kappa']):
  y=abs(np.diff(ed['mx'][ki,1:]))/np.diff(ed['h'][1:]);ids=find_peaks(y)[0]
  if len(ids):
   jj=max(ids,key=lambda t:y[t]);edline.append(dict(kappa=float(k),h=float((ed['h'][jj+1]+ed['h'][jj+2])/2),support=[float(ed['h'][jj+1]),float(ed['h'][jj+2])],value=float(y[jj]),step=.1,smoothing=None,interpretation='N8 ED finite-grid maximum response; not a thermodynamic boundary'))
 dump(OUT/'detection/ed_response_line.json',edline)
 fig,axs=plt.subplots(3,3,figsize=(12,10),sharex=True,sharey=True)
 for i,method in enumerate(['B0','B3','B4']):
  for j,p in enumerate([0,.01,.05]):
   a=arrays[method,p];ax=axs[i,j];ax.imshow(a[0],origin='lower',extent=[.05,2.05,-.025,1.025],aspect='auto',cmap=cmap,norm=norm);ii,jj=np.where(a[3]);ax.scatter((jj+1)*.1,ii*.05,marker='x',c='red',s=10,linewidths=.7);ax.set(title=f'{method}, p={p}',xlabel='h',ylabel='kappa')
   ax.plot([r['h'] for r in edline],[r['kappa'] for r in edline],color='white',marker='.',lw=.8,ms=2)
   # External qualitative curves only, transposed for h-horizontal coordinate.
   kk=np.linspace(.001,.499,80);hi=(1-kk)/kk*(1-np.sqrt((1-3*kk+4*kk**2)/(1-kk)));ax.plot(hi,kk,'k--',lw=.65)
   kk=np.linspace(.501,1,80);ax.plot(1.05*(kk-.5),kk,'k:',lw=.65);ax.plot(1.05*np.sqrt((kk-.5)*(kk-.1)),kk,'k:',lw=.65)
 fig.legend([plt.Line2D([0],[0],color=c,lw=8) for c in colors],labels,loc='lower center',ncol=5,bbox_to_anchor=(.5,-.01));fig.suptitle('Frozen full-observable reference resemblance; red x = preparation failure\nWhite: N8 ED response maximum; dashed/dotted: external literature approximations');fig.tight_layout(rect=[0,.03,1,.94]);save('matched_phase_maps')
 fig,axs=plt.subplots(1,3,figsize=(12,3.7),sharex=True,sharey=True)
 for ax,(title,a) in zip(axs,[('ED',ed['structure_factor'][:,1:,0]),('B0',arrays['B0',0][1]),('B3',arrays['B3',0][1])]):
  im=ax.imshow(a,origin='lower',extent=[.05,2.05,-.025,1.025],aspect='auto',vmin=0,vmax=1,cmap='viridis');ax.set(title=title+' clean m0 squared',xlabel='h',ylabel='kappa')
 fig.colorbar(im,ax=axs.tolist(),label='m0 squared');save('clean_ed_comparison')
 fig,axs=plt.subplots(1,2,figsize=(10,4));a=[r for r in matched if r['method']=='B3' and r['p']==.01];
 for eligible,color,label in [(True,'#2878b5','Both preparations pass'),(False,'#c43b40','At least one fails')]:
  group=[r for r in a if r['common_pass']==eligible];axs[0].scatter([r['new_cnots'] for r in group],[r['epsilon_c_new'] for r in group],c=color,s=12,label=label)
 axs[0].legend(fontsize=8)
 axs[0].set(xlabel='B3 CNOT count',ylabel='Total C error, p=.01',title='All grid points; quality mask retained')
 for p in [.01,.05]:
  a=[r for r in matched if r['method']=='B3' and r['p']==p];axs[1].scatter([r['epsilon_c_old'] for r in a],[r['epsilon_c_new'] for r in a],s=10,alpha=.45,label=f'p={p}')
 axs[1].plot([0,1],[0,1],'k--');axs[1].set(xlabel='B0 total C error',ylabel='B3 total C error',title='Matched-coordinate comparison');axs[1].legend();save('pareto_noise')
 # Reference choice is a preparation-protocol diagnostic, never a classifier input.
 refgrid=np.full((21,20),np.nan);cnotgrid=refgrid.copy();quality=refgrid.copy()
 for point in grid:
  i=round(point['kappa']/.05);j=round(point['h']/.1)-1;r=point['methods']['B3'];refgrid[i,j]=PLAN['refs'].index(r['ref']);cnotgrid[i,j]=r['selected']['cnots'];quality[i,j]=r['joint_pass']
 fig,axs=plt.subplots(1,2,figsize=(11,4))
 for ax,title,a,cm,vmax in zip(axs,['Selected inference CNOTs','Selected reference (not phase label)'],[cnotgrid,refgrid],['viridis',ListedColormap(['#636363','#bdbdbd','#f0f0f0'])],[128,2]):
  im=ax.imshow(a,origin='lower',extent=[.05,2.05,-.025,1.025],aspect='auto',vmin=0,vmax=vmax,cmap=cm);ii,jj=np.where(quality==0);ax.scatter((jj+1)*.1,ii*.05,c='red',marker='x',s=9);ax.set(title=title,xlabel='h',ylabel='kappa');bar=fig.colorbar(im,ax=ax)
  if title.startswith('Selected reference'):bar.set_ticks([0,1,2],labels=['plus','GHZ','period-4 cat'])
 fig.tight_layout();save('resources_references')
 # Full SF comparison at 3 representatives.
 fig,axs=plt.subplots(1,3,figsize=(11,3.5))
 for ax,(k,h) in zip(axs,[(0,.2),(.3,.4),(.8,.5)]):
  point=next(r for r in grid if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12);a=np.load(ROOT/point['methods']['B3']['archive']);oldstate=np.load(ROOT/oldstates[round(k,6),round(h,6)]['archive'])['state']
  for label,state in [('ED',a['ed_state']),('B0',oldstate),('B3',a['state'])]:ax.plot(np.arange(8)/4,observations(state,8)['structure_factor'],'o-',label=label)
  ax.set(title=f'kappa={k}, h={h}',xlabel='q / pi',ylabel='m_q squared',ylim=(-.02,1.02));ax.legend()
 save('full_sf')
# Three-detector same-data comparison and uncertainty accounting.
if (OUT/'detection/predictions.json').exists():
 pred=json.loads((OUT/'detection/predictions.json').read_text());table=[]
 for task in ['development','heldout','map']:
  for method in ['B1','B2','B3','B4']:
   for p in [0,.01,.05]:
    a=[r for r in pred if r['task']==task and r['method']==method and r['p']==p]
    if not a:continue
    table.append(dict(task=task,method=method,p=p,points=len(a),prep_pass=sum(r['prep_pass'] for r in a),D1_rejected=sum(r['D1'] in ['uncertain','degraded'] for r in a),D3_rejected=sum(r['D3'] in ['uncertain','degraded'] for r in a),D1_D3_agreement=sum(r['D1']==r['D3'] for r in a),independent_error_rate=None,reason='No independent finite-grid phase labels; agreement is not accuracy'))
 csvwrite(OUT/'detection/comparison.csv',table);stats['detection']=table
 curves=json.loads((OUT/'detection/fidelity_curves.json').read_text());fig,axs=plt.subplots(2,3,figsize=(12,6),sharex=True)
 for j,k in enumerate([0,.3,.8]):
  for r in curves:
   if r['kappa']!=k:continue
   axs[0,j].plot(r['h_mid'],r['full_observable_change_rate'],label=f"p={r['p']}");axs[1,j].plot(r['h_mid'],r['chi_f'],label=f"p={r['p']}")
  axs[0,j].set(title=f'kappa={k}',ylabel='D1 full-feature change rate');axs[1,j].set(xlabel='h midpoint',ylabel='D2 Uhlmann susceptibility');axs[0,j].legend()
 fig.suptitle('Pointwise selected circuits: structure switches require separate branch audit');fig.tight_layout();save('detectors')
# N12 genuine VQE plus noise
if (OUT/'n12/noise_index.json').exists():
 a=json.loads((OUT/'n12/noise_index.json').read_text());stats['n12_noise']=dict(points=len(a),configs=sum(len(r['noise']) for r in a),prep_pass=sum(r['row']['joint_pass'] for r in a),backend='exact density')
 fig,axs=plt.subplots(1,2,figsize=(10,4));n12=json.loads((OUT/'n12/index.json').read_text())
 for k in [0,.3,.8]:
  r=sorted([p['methods']['B3'] for p in n12 if p['kappa']==k],key=lambda p:p['h']);axs[0].plot([p['h'] for p in r],[max(p['delta_e'],1e-10) for p in r],'o-',label=f'kappa={k}')
 failed=[p['methods']['B3'] for p in n12 if not p['methods']['B3']['joint_pass']];axs[0].scatter([r['h'] for r in failed],[max(r['delta_e'],1e-10) for r in failed],c='red',marker='x',s=30,label='Joint preparation failure')
 axs[0].axhline(.001,c='k',ls='--');axs[0].set(yscale='log',xlabel='h',ylabel='N12 energy error per spin');axs[0].legend()
 for p in [0,.01,.05]:
  vals=[next(x for x in r['noise'] if x['p']==p)['epsilon_c_total'] for r in a];axs[1].plot(range(len(a)),vals,'o-',label=f'p={p}')
 
 for j,r in enumerate(a):
  if not r['row']['joint_pass']:axs[1].axvspan(j-.15,j+.15,color='red',alpha=.15)
 axs[1].set(xlabel='Representative index (red band: prep failure)',ylabel='N12 total C error');axs[1].legend();save('n12')
# mitigation bias/variance at equal total circuit shots
mit=json.loads((OUT/'mitigation/index.json').read_text());stats['mitigation']={}
fig,axs=plt.subplots(1,2,figsize=(10,4))
for ax,p in zip(axs,[.01,.05]):
 a=[r for r in mit if r['p']==p]
 for method in ['raw','zne','sv']:
  vals=[np.mean([r['statistics'][f'{method}_{b}']['mean_mse'] for r in a]) for b in [10000,100000]];ax.plot([10000,100000],vals,'o-',label=method)
  stats['mitigation'][f'{method}_p{p}']=dict(mean_mse_10k=float(vals[0]),mean_mse_100k=float(vals[1]),points=len(a),bias_improved=int(sum(np.mean(np.array(r['bias'][method])**2)<np.mean(np.array(r['bias']['raw'])**2) for r in a)))
 ax.set(xscale='log',yscale='linear',ylim=(0,.15),xlabel='Total circuit shots per point',ylabel='Mean component MSE vs own clean circuit',title=f'p={p}; shared absolute error scale');ax.legend()
fig.tight_layout();save('mitigation_equal_shots')
# large N evidence
if (OUT/'floating/refine_index.json').exists():
 fl=json.loads((OUT/'floating/refine_index.json').read_text());sel=json.loads((OUT/'floating/candidate_windows.json').read_text());fig,axs=plt.subplots(2,3,figsize=(12,6),sharey='row');evidence=[]
 for j,(k,h) in enumerate(sel['centers']):
  a=[r for r in fl if r['kappa']==k and r['h']==h and r['init']=='plus']
  for chi in [64,128,256]:
   b=sorted([r for r in a if r['chi_max']==chi],key=lambda r:r['n']);axs[0,j].plot([r['n'] for r in b],[r['entropy_fits'][-1]['c'] for r in b],'o-',label=f'chi={chi}');axs[1,j].plot([r['n'] for r in b],[r['fit_raw'][0]['q'] for r in b],'o-',label=f'chi={chi}')
  axs[0,j].set(title=f'OBC kappa={k}, h={h}',ylabel='Fitted c (not fixed to 1)');axs[1,j].set(xlabel='N',ylabel='Fitted oscillation q');axs[0,j].legend()
  evidence.append(dict(kappa=k,h=h,runs=len(a),evidence_grade='candidate',reason='Multi-N/chi comparisons executed; oscillatory finite-OBC fits and controls require convergence review before support claim'))
 fig.tight_layout();save('floating_convergence')
 if (OUT/'floating/evidence_grading.json').exists():evidence=json.loads((OUT/'floating/evidence_grading.json').read_text())['rows']
 stats['floating']=evidence;dump(OUT/'floating/evidence.json',evidence)
# dynamics actual errors
rows=json.loads((OUT/'dynamics/index.json').read_text());stats['dynamics']=dict(configs=len(rows),parameter_initial_pairs=len(set((r['kappa'],r['h'],r['initial']) for r in rows)),times=11,max_error_at_dt={})
fig,axs=plt.subplots(1,2,figsize=(10,4))
for p in [0,.01,.05]:
 vals=[np.mean([r['max_total_error'] for r in rows if r['p']==p and r['dt']==dt]) for dt in [.05,.1,.2]];axs[0].plot([.05,.1,.2],vals,'o-',label=f'p={p}');stats['dynamics']['max_error_at_dt'][str(p)]=vals
axs[0].set(xlabel='Trotter time step',ylabel='Mean max observable error vs exact evolution');axs[0].legend()
for initial in ['zero','0011']:
 a=sorted([r for r in rows if r['p']==0 and r['dt']==.05 and r['kappa']==.8 and r['initial']==initial],key=lambda r:r['h']);axs[1].plot([r['h'] for r in a],[r['features']['mean_return'] for r in a],'o-',label=initial)
axs[1].set(xlabel='Quench h',ylabel='Time-averaged return probability',title='Same fixed initial states across all h');axs[1].legend();save('dynamics_tradeoff')
stats['cost']=dict(unique_adaptive_runs=len(allruns),adaptive_seconds=sum(r['seconds'] for r in allruns),noise_unique_records=len(list((OUT/'noise/cache').glob('*.json'))),wall_elapsed_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(PLAN['started_utc'])).total_seconds())
noise_records=[json.loads(p.read_text()) for p in (OUT/'noise/cache').glob('*.json')]
float_records=[json.loads(p.read_text()) for p in (OUT/'floating').glob('n*_chi*.json')]
stats['cost'].update(noise_seconds_sum=sum(r['seconds'] for r in noise_records),mps_seconds_sum=sum(r['seconds'] for r in float_records),dynamics_seconds_sum=sum(r['seconds'] for r in rows),timing_note='Sums of measured call durations, potentially overlapping; not wall time. No double-counting cache aliases. Includes partial script retries only where their original logs provide evidence.')
factor=json.loads((OUT/'ablation/factor_ablation.json').read_text());stats['factor_ablation']={}
for task in ['development','heldout']:
 a=[r for r in factor if r['task']==task];stats['factor_ablation'][task]=dict(points=len(a),single_plus_cost_pass=sum(r['single_plus_cost']['joint_pass'] for r in a),median_cnots=float(np.median([r['single_plus_cost']['selected']['cnots'] for r in a])))
dump(S/'statistics.json',stats);print(json.dumps({k:v for k,v in stats.items() if k not in ['matched','detection']},indent=2)[:4000])
