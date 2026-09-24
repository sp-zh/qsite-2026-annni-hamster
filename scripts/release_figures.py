"""Deterministic redraws from immutable archived numbers. No fit, selection or smoothing."""
from release import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch
COLORS=['#286A9D','#D18439','#39836F','#9375AD','#C6CCD1']
LABELS=['ferro-like','antiphase-like','paramagnetic-like','degraded','uncertain']
DISPLAY_LABELS=['ferro-like','antiphase-like','paramagnetic-like','degraded','unassigned']
METHODS=['raw','zne_quadratic','sv'];MC=['#286A9D','#C46140','#39836F'];NAMES=['Raw','Quadratic ZNE','SV']
def draw(out,stats):
 out.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
 made=[]
 def save(fig,name):
  for ext in ['png','pdf']:fig.savefig(out/(name+'.'+ext),dpi=180,bbox_inches='tight')
  plt.close(fig);made.append(name)
 rows=read('results/stage6_v1/n8_maps/map_analysis.json');ks=np.unique([r['kappa'] for r in rows]);hs=np.unique([r['h'] for r in rows]);cmap=ListedColormap(COLORS);norm=BoundaryNorm(np.arange(6)-.5,5)
 from annni.upgrade_detection import predict
 cfg=read(F+'/detector_frozen.json')
 def ent(r,p,est='raw'):return next(e for e in r['entries'] if e['method']=='B3' and e['p']==p and e['estimator']==est)
 def phase(ax,p,source='predictions_exact',est='raw',ed=False,quality=True):
  g=np.empty((len(ks),len(hs)));fails=[];unknown=[]
  for r in rows:
   e=ent(r,p,est);label=predict(r['target'],cfg)['D3'] if ed else e[source]['D3'];g[np.where(ks==r['kappa'])[0][0],np.where(hs==r['h'])[0][0]]=LABELS.index(label)
   if not e['preparation_quality']['joint_pass']:fails.append((r['kappa'],r['h']))
   if r['reference_label'] is None:unknown.append((r['kappa'],r['h']))
  ax.pcolormesh(ks,hs,g.T,cmap=cmap,norm=norm,shading='nearest',rasterized=True)
  if quality and not ed and fails:
   f=np.array(fails);ax.scatter(f[:,0],f[:,1],s=10,marker='x',c='black',linewidths=.6,label='preparation_failed')
  ax.set(xlabel=r'$\kappa$',ylabel='$h$',xlim=(-.025,1.025),ylim=(.05,2.05),title='ED + frozen D3' if ed else f'B3 / {est.replace("zne_quadratic","quadratic ZNE")} / p={p:g}')
  return g
 legend=[Patch(color=c,label=l) for c,l in zip(COLORS,DISPLAY_LABELS)]
 for p,suffix in [(0,'0'),(.01,'001'),(.05,'005')]:
  fig,ax=plt.subplots(figsize=(6,4.8));phase(ax,p);fig.legend(handles=legend,loc='lower center',ncol=3,bbox_to_anchor=(.5,-.02),frameon=False);fig.subplots_adjust(bottom=.19);ax.text(0,1.025,'N=8, PBC | 420 points | exact expectations | x: ideal preparation failed',transform=ax.transAxes,fontsize=8);save(fig,'phase_p'+suffix)
 fig,axs=plt.subplots(1,4,figsize=(15,4.3),sharey=True)
 phase(axs[0],0,ed=True)
 for ax,p in zip(axs[1:],[0,.01,.05]):phase(ax,p)
 fig.legend(handles=legend,loc='lower center',ncol=5,frameon=False);fig.subplots_adjust(bottom=.22,wspace=.25);fig.suptitle('Frozen D3 diagnostic labels; colors are not independent phase truth.  x: failed ideal preparation',fontsize=11);save(fig,'phase_comparison')
 for est in ['raw','zne_quadratic']:
  fig,axs=plt.subplots(1,3,figsize=(12,4.2),sharey=True)
  for ax,p in zip(axs,[0,.01,.05]):phase(ax,p,source='predictions_single',est=est)
  fig.legend(handles=legend,loc='lower center',ncol=5,frameon=False);fig.subplots_adjust(bottom=.23);fig.suptitle(f'One archived 100k-total-shot repeat per point / {est} / equal shots, NOT equal CNOT-shots');save(fig,'phase_single_'+est)
 fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained');mask=np.array([int(r['reference_label'] is not None) for r in rows]).reshape(len(ks),len(hs));axs[0].pcolormesh(ks,hs,mask.T,shading='nearest',cmap=ListedColormap(['#E4E6E9','#39836F']),vmin=0,vmax=1);axs[0].set(title='Independent region labels: green\nGray: continuous/RN evidence only',xlabel=r'$\kappa$',ylabel='$h$')
 for j,name in enumerate(['m0 squared','m(pi/2) squared','Mx']):
  pass
 # No branch status is silently inferred from the main grid. Window statuses have own coordinates.
 axs[1].axis('off');axs[1].text(0,.95,'Three distinct layers\n\n1. ED continuous observables / reference regions\n2. Circuit preparation quality (x overlay)\n3. Frozen detector resemblance labels\n\nBranch-sensitive flags apply to audited windows.\nMain-grid branch status: not audited here.\nNo interpolation, no spatial voting, no new masks.',va='top',fontsize=11);save(fig,'reference_scope')
 b=stats['b0_b3'];fig,axs=plt.subplots(1,3,figsize=(11,3.2),layout='constrained')
 axs[0].bar(['B0','B3'],[b[0]['B0_median_CNOT'],b[0]['B3_median_CNOT']],color=MC[:2]);axs[0].set(title='Median CNOTs',ylim=(0,220))
 vals=[b[0]['B0_joint_pass'],b[0]['B3_joint_pass']];axs[1].bar(['B0','B3'],vals,color=MC[:2]);axs[1].set(title='Ideal joint pass / 420',ylim=(0,440))
 for i,v in enumerate(vals):axs[1].text(i,v+5,str(v),ha='center')
 x=np.arange(3)
 for off,m,c in [(-.18,'B0',MC[0]),(.18,'B3',MC[1])]:axs[2].bar(x+off,[r[m+'_mean_max_C_error'] for r in b],width=.35,label=m,color=c)
 axs[2].set(xticks=x,xticklabels=['0','.01','.05'],xlabel='p',title='Mean of pointwise max |C error|');axs[2].legend(frameon=False);save(fig,'resource_tradeoff')
 fig,axs=plt.subplots(1,3,figsize=(11,3.7),layout='constrained')
 for ax,p in zip(axs,[0,.01,.05]):
  for i,(m,c) in enumerate(zip(METHODS,MC)):
   values=[next(r for r in stats['equal_resource'] if (r['mode'],r['budget'],r['p'],r['method'])==(mode,100000,p,m))['MSE_ED'] for mode in ['equal_shots','equal_gate']]
   ax.bar(np.arange(2)+(i-1)*.24,values,width=.23,color=c,label=NAMES[i])
  ax.set(xticks=[0,1],xticklabels=['Equal shots','Equal CNOT-shots'],title=f'p={p:g}',ylabel='17-component ED-target MSE');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
 axs[0].legend(fontsize=8,frameon=False);fig.suptitle('45 coordinates; mean over 32 repeats. Each arm shares its budget across all settings/scales.',fontsize=10);save(fig,'equal_resource')
 fig,axs=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
 for ax,p in zip(axs,[.01,.05]):
  for i,(m,c) in enumerate(zip(METHODS,MC)):
   v=next(r for r in stats['equal_resource'] if (r['mode'],r['budget'],r['p'],r['method'])==('equal_gate',100000,p,m));ax.bar(i-.17,v['bias_squared'],width=.32,color=c);ax.bar(i+.17,v['sampling_MSE'],width=.32,color=c,hatch='///',alpha=.65)
  ax.set(xticks=range(3),xticklabels=NAMES,yscale='log',title=f'Equal CNOT-shots / p={p:g}',ylabel='Bias squared / sampling MSE')
 fig.suptitle('Solid: squared bias vs ED. Hatched: sampling MSE. Finite cross term remains in total MSE.',fontsize=10);save(fig,'bias_sampling')
 cov=stats['windows'];fig,axs=plt.subplots(1,3,figsize=(11,3.5),sharey=True,layout='constrained')
 for ax,p in zip(axs,[0,.01,.05]):
  for i,(m,c) in enumerate(zip(METHODS,MC)):
   rr=next(x for x in cov if (x['mode'],x['budget'],x['p'],x['method'])==('equal_shots',100000,p,m));a=rr['frozen_matching_window_equivalents'];q=rr['quality_supported_match_window_equivalents'];ax.bar(i,a,color=c,alpha=.35);ax.bar(i,q,color=c);ax.text(i,a+.09,f'{a:.2f}',ha='center',fontsize=9)
  ax.set(xticks=range(3),xticklabels=['Raw','Q-ZNE','SV'],title=f'p={p:g}',ylim=(0,5.45));ax.axhline(5,color='gray',ls=':')
 axs[0].set_ylabel('Matched window equivalents / 5 resolvable');fig.suptitle('6/6 windows executed; kappa=.5 fails peak selection. Dark: no listed curve-audit problem (not a phase certificate).',fontsize=10);save(fig,'window_coverage')
 curves=read(F+'/window_completion/curves.json');fig,axs=plt.subplots(2,3,figsize=(11,6),layout='constrained')
 for ax,(k,r) in zip(axs.flat,curves.items()):
  h=np.array(r['h']);idx=8 if float(k)<.5 else 10;mid=(h[:-1]+h[1:])/2
  ax.plot(mid,-np.diff(np.array(r['ED'])[:,idx])/np.diff(h),'k-',label='ED')
  for m,c,nm in zip(METHODS,MC,NAMES):
   arm=r['arms']['equal_shots_100000_0.05_'+m];ax.plot(mid,-np.diff(np.array(arm['exact'])[:,idx])/np.diff(h),color=c,label=nm)
  ax.set(title=f'kappa={k} / p=.05',xlabel='h midpoint',ylabel='- d(order score)/dh');ax.axhline(0,color='gray',lw=.5)
 axs[0,0].legend(fontsize=8,frameon=False);fig.suptitle('All 17-point windows retained; exact expectations isolate preparation/noise from shots',fontsize=11);save(fig,'six_windows')
 # Representative fixed example: .8 was requested before followup, shows branch/preparation limitations.
 r=curves['0.8'];h=np.array(r['h']);mid=(h[:-1]+h[1:])/2;fig,axs=plt.subplots(1,2,figsize=(10,3.4),layout='constrained')
 for ax,idx,derivative in [(axs[0],10,False),(axs[1],10,True)]:
  transform=lambda v:-np.diff(np.array(v)[:,idx])/np.diff(h) if derivative else np.array(v)[:,idx]
  xx=mid if derivative else h;ax.plot(xx,transform(r['ED']),'k-',label='ED')
  for m,c,nm in zip(METHODS,MC,NAMES):
   a=r['arms']['equal_shots_100000_0.05_'+m];ax.plot(xx,transform(a['exact']),color=c,label=nm)
  ax.set_xlabel('h midpoint' if derivative else 'h');ax.set_ylabel('- d m(pi/2)^2 / dh' if derivative else 'm(pi/2)^2')
 axs[0].legend(fontsize=8);fig.suptitle('Fixed kappa=.8 window, p=.05: observable reconstruction and response-peak failure',fontsize=11);save(fig,'window_example')
 ex=stats['extensions'];fig,axs=plt.subplots(1,2,figsize=(9,3.4),layout='constrained')
 for ax,cohort,title in zip(axs,['low_field_confirmation','n12'],['New N8 low-field confirmation','N12 difficult/control transfer']):
  rr=[next(r for r in ex if r['cohort']==cohort and r['method']==m) for m in ['B3','H6']];ax.bar(['B3','H6'],[r['joint_pass'] for r in rr],color=MC[:2]);ax.set(title=title,ylabel='Selected joint pass',ylim=(0,rr[0]['n']*1.2));
  for i,r in enumerate(rr):ax.text(i,r['joint_pass']+1,f"{r['joint_pass']}/{r['n']}\nmedian {r['median_CNOT']:g} CNOT",ha='center',fontsize=9)
 save(fig,'extensions')
 fl=stats['floating'];fig,ax=plt.subplots(figsize=(10,2.8),layout='constrained')
 for name,vals,y,color in [('Antiphase control',fl['supported_samples']['supported_antiphase_sample'],2,MC[0]),('Screened samples',fl['candidate_floating_samples'],1,MC[1]),('PM-side control',fl['supported_samples']['supported_paramagnetic_side_sample'],0,MC[2]),('No phase label',fl['unresolved_samples'],1,'#BEC4CC')]:ax.scatter(vals,[y]*len(vals),s=70,c=color,label=name)
 ax.set(xlabel='h at kappa=.8 (OBC)',yticks=[0,1,2],yticklabels=['PM side','no phase label / screened','antiphase'],xlim=(.25,.75),ylim=(-.5,2.6),title='Floating scan: zero supported samples and zero transition brackets');ax.legend(loc='upper right',fontsize=8,ncol=2);save(fig,'floating_evidence')
 fig,axs=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
 for p,c in zip([0,.01,.05],MC):
  a=np.load(path(f'results/stage4_upgrade_v1/dynamics/k0.80_h0.80_zero_dt0.10_p{p:.2f}.npz'));axs[0].plot(a['times'],a['observables'][:,16],color=c,label=f'p={p:g}');axs[1].plot(a['times'],a['return_probability'],color=c,label=f'p={p:g}')
 axs[0].plot(a['times'],a['exact_observables'][:,16],'k--',label='Exact unitary');axs[1].plot(a['times'],a['exact_return'],'k--',label='Exact unitary');axs[0].set(xlabel='time',ylabel='Mx');axs[1].set(xlabel='time',ylabel='Return probability');axs[0].legend(fontsize=8);fig.suptitle('Archived dynamics control: kappa=.8, h=.8, zero product state, dt=.1 (not ground-state classification)',fontsize=10);save(fig,'dynamics')
 # Archived fit parameters only: no new fits or windows.
 fitrows=read('results/stage6_v1/floating_boundary_scan/friedel_size_sensitivity_plotdata.json')
 fig,axs=plt.subplots(1,3,figsize=(10,3.3),sharey=True,layout='constrained')
 for ax,h in zip(axs,[.4,.425,.5]):
  rr=sorted([r for r in fitrows if r['h']==h],key=lambda r:r['n'])
  for j,r in enumerate(rr):
   for field,marker,color,label in [('original','o',MC[0],'Original background'),('raw_quadratic_background','x',MC[1],'Quadratic background')]:
    values=[f['K'] for f in r[field]];ax.plot([r['n']]*len(values),values,marker=marker,color=color,label=label if j==0 else None)
  if h==.425:
   latest=read('results/stage6_v1/floating_boundary_scan/h425_size_friedel.json')
   for rr in latest:ax.scatter([rr['n']]*len(rr['fits']),[f['K'] for f in rr['fits']],marker='+' if rr['initial']=='plus' else 'x',c='black',s=60)
   ax.text(.98,.88,'N160: both starts at bound',transform=ax.transAxes,ha='right',fontsize=8)
  ax.set(xlabel='N (OBC)',title=f'h={h:g}',ylim=(0,2.1));ax.axhline(2,ls=':',color='gray');ax.legend(fontsize=7)
 axs[0].set_ylabel('Archived Friedel K fit / two windows');fig.suptitle('kappa=.8: sensitivity to size/background; reaching the bound is not a reliable K estimate',fontsize=10);save(fig,'floating_fit_sensitivity')
 # Slide-specific layout: identical data, larger type, no new scientific operation.
 with plt.rc_context({'font.size':16}):
  fig,axs=plt.subplots(1,3,figsize=(12,4.3),sharey=True)
  for ax,p in zip(axs,[0,.01,.05]):
   phase(ax,p);ax.set_title(f'p={p:g}',fontsize=20);ax.set_xticks([0,.5,1]);ax.set_yticks([.5,1,1.5,2])
  fig.legend(handles=legend,loc='lower center',ncol=3,fontsize=14,frameon=False);fig.subplots_adjust(bottom=.30,wspace=.22);save(fig,'slide_phases')
  fig,ax=plt.subplots(figsize=(6,3.3),layout='constrained');ax.pcolormesh(ks,hs,mask.T,shading='nearest',cmap=ListedColormap(['#E4E6E9','#39836F']),vmin=0,vmax=1);ax.set(xlabel='$\\kappa$',ylabel='$h$',title='Green: independent interior labels');save(fig,'slide_reference')
 dump(out/'figure_inventory.json',dict(figures=made,source='scripts/release_figures.py',main_detector='frozen Stage4 D3, retained baseline not chosen by test accuracy',main_measurement='exact expectations; single-shot-repeat and mitigated panels separately labelled'))
 return dict(figures=made)
