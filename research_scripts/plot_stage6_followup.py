"""Replot only archived followup numerical results; no hidden simulation."""
import sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.stage6_followup import *
from annni.stage6_diagnostics import response_curves,peaks_and_primary
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130})
F=OUT/'figures';F.mkdir(exist_ok=True);curves=read(OUT/'window_completion/curves.json');coverage=read(OUT/'window_completion/coverage.json');summary=read(OUT/'equal_gate_budget/summary.json');matches=read(OUT/'window_completion/matches.json');colors={'raw':'#2864ad','zne_quadratic':'#d27822','sv':'#31846b'}
for response in [False,True]:
 fig,axes=plt.subplots(6,3,figsize=(14,19))
 for i,(ktext,c) in enumerate(curves.items()):
  k=float(ktext);h=np.array(c['h']);mid=(h[:-1]+h[1:])/2;col=8 if k<.5 else 10;name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';ed=np.array(c['ED']);clean=np.array(c['clean']);limits=[]
  for j,p in enumerate([0,.01,.05]):
   ax=axes[i,j];x=mid if response else h;get=lambda v:response_curves(h,v,8)[name] if response else np.asarray(v)[:,col]
   ax.plot(x,get(ed),'k-',label='same-N ED');ax.plot(x,get(clean),color='.5',ls='--',label='B3 clean exact');limits.extend(get(ed));limits.extend(get(clean))
   for m in ['raw','zne_quadratic']:
    a=c['arms'].get(f'equal_shots_100000_{p}_{m}')
    if a is None:continue
    vv=np.array([get(v) for v in a['samples']]);mean=vv.mean(0);lo,hi=np.quantile(vv,[.05,.95],axis=0);ax.plot(x,mean,color=colors[m],label=m);ax.fill_between(x,lo,hi,color=colors[m],alpha=.17);limits.extend(lo);limits.extend(hi)
    if response:
     peaks=peaks_and_primary(h,mean)
     for peak in peaks['peaks']:ax.scatter(peak['coordinate'],peak['value'],marker='s' if peak['endpoint'] else 'o',s=15,color=colors[m])
   for b in c['branches']:ax.axvline((b['left_h']+b['right_h'])/2,color='.8',lw=.6,ls=':')
   fail=[hh for hh,quality in zip(h,c['preparation']) if not quality['joint_pass']]
   ax.scatter(fail,[.025]*len(fail),transform=ax.get_xaxis_transform(),marker='x',s=15,c='red')
   ax.set_title(f'κ={k:g}, p={p:g}'+(' — reference unresolved' if k==.5 else ''));ax.set_xlabel('h');ax.set_ylabel('−d(order)/dh' if response else ('m₀²' if k<.5 else 'mπ/2²'))
  low,high=min(limits),max(limits);pad=.06*max(high-low,.05)
  for ax in axes[i]:ax.set_ylim((low-pad,high+pad) if response else (min(0,low-pad),max(1.05 if k<.5 else .525,high+pad)))
 handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=4,bbox_to_anchor=(.5,.976));fig.suptitle('B3 registered windows: 100k total shots per point ×32 repeats\nBands: empirical 5–95% repeats, not confidence intervals; red ×: preparation failure; dotted: branch switches',y=.998,fontsize=12);fig.tight_layout(rect=[0,0,1,.95]);fig.savefig(F/('six_window_responses.png' if response else 'six_window_orders.png'));plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(14,4.5),sharey=True)
for ax,p in zip(axes,[0,.01,.05]):
 rr=[r for r in coverage if r['mode']=='equal_shots' and r['budget']==100000 and r['p']==p]
 for i,r in enumerate(rr):
  clean=r['frozen_matching_window_equivalents']-r['matched_problem_window_equivalents'];problem=r['matched_problem_window_equivalents'];ax.bar(i,clean,color='#31846b');ax.bar(i,problem,bottom=clean,color='#db9f42');ax.scatter(i,r['executed_complete_windows'],marker='_',s=200,c='black')
 ax.axhline(5,color='.5',ls='--');ax.set_xticks(range(len(rr)),[r['method'] for r in rr],rotation=15);ax.set_title(f'p={p:g}');ax.set_ylim(0,6.4)
axes[0].set_ylabel('Window equivalents (repeat-normalized)');fig.suptitle('Execution: black ticks /6; resolvable reference: dashed /5\nGreen: matched without audit flags; amber: numerical match with curve issues');fig.tight_layout(rect=[0,0,1,.87]);fig.savefig(F/'coverage_and_issues.png');plt.close(fig)
fig,axes=plt.subplots(2,3,figsize=(14,8),sharey='row')
for j,p in enumerate([0,.01,.05]):
 for m in colors:
  rr=[next(r for r in summary if r['cohort']=='all_B' and r['mode']==mode and r['budget']==b and r['method']==m and r['p']==p) for mode,b in [('equal_shots',100000),('equal_gate',100000),('equal_gate',300000)]]
  axes[0,j].plot(range(3),[r['MSE_ED_mean'] for r in rr],'-o',label=m,color=colors[m]);axes[1,j].plot(range(3),[r['CNOT_shots_all32']/1e9 for r in rr],'-o',label=m,color=colors[m])
 axes[0,j].set_title(f'p={p:g}');axes[0,j].set_yscale('log')
 for ax in axes[:,j]:ax.set_xticks(range(3),['equal shots\n100k','equal G\n100k×C','equal G\n300k×C']);ax.grid(alpha=.2)
axes[1,0].set_ylim(bottom=0)
axes[0,0].set_ylabel('MSE to ED (shared log scale)');axes[1,0].set_ylabel('Total CNOT-shots /10⁹, all32 repeats');axes[0,0].legend();fig.suptitle('Same fixed B3 coordinates, unchanged estimators; equal G does not equal all costs');fig.tight_layout(rect=[0,0,1,.96]);fig.savefig(F/'equal_resource_MSE_cost.png');plt.close(fig)
fig,axes=plt.subplots(2,3,figsize=(14,8),sharey='row')
for i,k in enumerate(cfg()['equal_gate_windows']):
 for j,p in enumerate([0,.01,.05]):
  ax=axes[i,j]
  for mindex,m in enumerate(colors):
   rr=[r for r in matches if r['kappa']==k and r['p']==p and r['method']==m and r['mode']=='equal_gate' and r['budget']==100000 and r['repeat']>=0];good=[r for r in rr if r['frozen_result']['result']['primary'] is not None];ax.scatter([mindex+(r['repeat']-15.5)*.006 for r in good],[r['frozen_result']['result']['primary']['coordinate'] for r in good],s=16,color=colors[m],alpha=.6)
   ax.text(mindex,.99,f"match {sum(r['frozen_rule_match'] for r in rr)}/32\nissues {sum(bool(r['curve_audit_status']) for r in rr)}/32\nmissing {len(rr)-len(good)}",transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
  ref=next(w for w in read(OUT/'window_reference.json') if w['kappa']==k)['frozen_reference'];ax.axhspan(ref['primary']['interval_low'],ref['primary']['interval_high'],color='grey',alpha=.15);ax.set_xticks(range(3),list(colors));ax.set_title(f'κ={k:g}, p={p:g}');ax.set_ylabel('Frozen interior peak h');ax.set_xlim(-.5,2.5)
 wh=next(w['h'] for w in read(OUT/'window_reference.json') if w['kappa']==k)
 axes[i,0].set_ylim(min(wh)-.01,max(wh)+.25*(max(wh)-min(wh)))
fig.suptitle('Equal CNOT-shots window: target100k×base CNOTs / point / repeat\nShading: ED grid support, not confidence interval; all32repeats and issues retained');fig.tight_layout(rect=[0,0,1,.92]);fig.savefig(F/'equal_resource_window_features.png');plt.close(fig)
print('Rendered five figures from saved numerical data')
