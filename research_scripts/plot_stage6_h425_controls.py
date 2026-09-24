"""Actual directed size controls; no fitted exponent chosen for proximity to theory."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=OUT/'floating_boundary_scan';assert (O/'h425_size_index.json').exists(),'Directed size jobs not executed'
allrows=[];friedel={};sources=[]
for task in ['coarse','bounded','followup','controls','final_continuation','h425_size']:
    p=O/f'{task}_analysis.json'
    if p.exists():allrows.extend(r for r in json.loads(p.read_text()) if r['h']==.425);sources.append(p)
    p=O/f'{task}_friedel.json'
    if p.exists():friedel.update({r['source_archive']:r for r in json.loads(p.read_text())});sources.append(p)
latest={}
for r in allrows:latest[(r['n'],r['chi'],r['initial'])]=r
fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained');records=[]
colors={'plus':'#277DA1','antiphase':'#CC6B32'}
for key,r in sorted(latest.items()):
    n,chi,initial=key;color=colors[initial];shift=(-1 if initial=='plus' else 1)+(0 if chi==256 else -2)
    f=friedel[r['archive']]['fits'];x=n+shift;mark='o' if r['solver_stopping_pass'] else 'x'
    ks=[v['K'] for v in f];cs=[v['c'] for v in r['analysis']['entropy'] if not v['oscillation_correction']]
    axs[0,0].plot([x]*len(ks),ks,color=color,lw=1)
    for fit in f:
        valid=fit.get('status')=='finite_size_fit_only' and not fit.get('parameters_at_bound') and fit.get('relative_rmse',1)<=.03
        axs[0,0].plot(x,fit['K'],marker=mark if valid else 'x',color=color if valid else 'crimson',ms=7,ls='none')
    axs[0,1].plot([x]*len(cs),cs,marker=mark,color=color,ms=6,lw=1)
    a=np.load(ROOT/r['archive']);raw=a['central_raw'];rr=np.arange(len(raw))
    if chi==256:
        axs[1,0].plot(rr,raw,'.-',color=color,alpha=.55,ms=2,lw=.7,label=f'N{n},{initial}')
    stats=r['sweeps'];sweeps=np.asarray(stats['sweep']);de=np.maximum(abs(np.asarray(stats['Delta_E'])),1e-18);ds=np.maximum(abs(np.asarray(stats['Delta_S'])),1e-18)
    axs[1,1].plot(sweeps,ds,'.-',label=f'N{n},chi{chi},{initial}',lw=.8,ms=2)
    records.append(dict(n=n,chi=chi,initial=initial,solver_stopping_pass=r['solver_stopping_pass'],source=r['archive'],K_fits=f,entropy_fits=r['analysis']['entropy'],signed_raw_correlation=raw,r=rr,Delta_E=de,Delta_S=ds,pairs=r['pairs']))
axs[0,0].axhspan(.25,.5,color='gray',alpha=.13);axs[0,0].set(xlabel='N (small offsets distinguish chains / chi)',ylabel='Friedel-profile K',title='Both frozen edge windows; no fit selection')
axs[0,0].plot([],[],'x',color='crimson',label='invalid / at-bound fit, not a physical K')
axs[0,1].axhline(1,color='gray',ls=':',lw=.8);axs[0,1].set(xlabel='N (small offsets distinguish chains / chi)',ylabel='Free OBC central-charge fit c',title='Different cuts retained; c alone is insufficient')
for ax in axs[0]:
    for name,col in colors.items():ax.plot([],[],color=col,marker='o',label=name)
    ax.plot([],[],'kx',label='stopping tolerance failed');ax.legend(fontsize=8);ax.grid(alpha=.15)
axs[1,0].set(xlabel='r (each N uses its recorded central pair sets)',ylabel='Signed C(r)',title='Latest chi256 chains, including all oscillation nodes');axs[1,0].legend(fontsize=7,ncol=2);axs[1,0].grid(alpha=.15)
axs[1,1].axhline(1e-6,color='black',ls='--',lw=.8);axs[1,1].set(xlabel='Recorded sweep index',ylabel='Absolute entropy change',yscale='log',title='Entropy stopping check; energy check separately in data');axs[1,1].legend(fontsize=6,ncol=2);axs[1,1].grid(alpha=.15)
fig.suptitle('kappa=.8, h=.425: registered continuation and independent N160 size checks')
fig.savefig(O/'figures/h425_directed_controls.png',dpi=170);plt.close(fig)
dump(O/'h425_directed_controls_plotdata.json',dict(rows=records,sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],scope='Latest chronological actual chain per(N,chi,initial), not best fit. Earlier failed chains retained in all source indices. Different r values use the saved fixed-midpoint pair rules; no absolute-value log envelope or node deletion. K/c window spread is sensitivity, not a statistical confidence interval.'))
print('Directed size plot rows',len(records))
