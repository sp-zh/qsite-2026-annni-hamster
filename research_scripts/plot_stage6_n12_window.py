"""Full N12 p0 window and separately costed sparse noise window; no masking."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_diagnostics import response_curves
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=OUT/'n12_transfer';F=O/'figures';F.mkdir(exist_ok=True)
a=np.load(O/'window_curves.npz');h=a['h'];n=12
methods=['B3','C0','C1','H6'];colors=dict(ED='black',B3='#277DA1',C0='#888888',C1='#679436',H6='#CC6B32')
rows=json.loads((O/'n12_window_paired_summary.json').read_text())['rows']
fig,axs=plt.subplots(3,2,figsize=(12,11),layout='constrained')
for method in ['ED',*methods]:
    values=a[method]
    axs[0,0].plot(h,values[:,n+n//4],'.-',label=method,color=colors[method],ms=3,lw=1)
    axs[0,1].plot((h[:-1]+h[1:])/2,response_curves(h,values,n)['minus_dmap_dh'],'.-',label=method,color=colors[method],ms=3,lw=1)
axs[0,0].set(ylabel='m(pi/2) squared',title='Full16-point p0 curves; every failed point retained')
axs[0,1].set(ylabel='-d m(pi/2) squared / dh',title='Same-coordinate finite-size response; no smoothing')
for ax,method in zip(axs[1],['ED','H6']):
    im=ax.pcolormesh(h,2*np.arange(n)/n,a[method][:,n:2*n].T,vmin=0,vmax=.5,cmap='viridis',shading='nearest')
    ax.set(ylabel='all discrete q / pi',title=method+' full structure factor')
    fig.colorbar(im,ax=ax,label='m_q squared, including self terms')
for method in methods:
    rr=sorted([r for r in rows if r['method']==method],key=lambda r:r['h'])
    for ax,key in zip(axs[2],['fidelity','cnots']):
        ax.plot([r['h'] for r in rr],[r[key] for r in rr],'.-',label=method,color=colors[method],ms=3,lw=1)
axs[2,0].axhline(.99,color='black',ls='--',lw=.7);axs[2,0].set(ylabel='Squared same-N ED fidelity',ylim=(-.03,1.03))
axs[2,1].set(ylabel='Actual CNOT count',ylim=(0,135))
for ax in axs.flat:ax.set(xlabel='h at kappa=.55, N12 PBC',xlim=(h.min(),h.max()));ax.grid(alpha=.15)
axs[0,0].legend(fontsize=8,ncol=5);axs[2,1].legend(fontsize=8,ncol=4)
fig.suptitle('N12 transfer: state failures and physical response are separate diagnostics')
fig.savefig(F/'n12_full_window.png',dpi=170);plt.close(fig)
sources=[O/'window_curves.npz',O/'n12_window_paired_summary.json']
p=O/'window_noise_curves.npz'
if p.exists():
    a=np.load(p);nh=a['h'];fig,axs=plt.subplots(1,3,figsize=(13,4),sharex=True,sharey=True,layout='constrained')
    for ax,pval in zip(axs,[0,.01,.05]):
        ax.plot(nh,a['ED'][:,n+n//4],'k.--',label='Same sparse ED')
        for method in ['B3','H6']:ax.plot(nh,a[f'{method}_p{pval}'][:,n+n//4],'.-',color=colors[method],label=method)
        ax.set(xlabel='h at kappa=.55',title=f'p={pval}; {len(nh)} preselected coordinates');ax.grid(alpha=.15)
    axs[0].set(ylabel='m(pi/2) squared');axs[0].legend(fontsize=8)
    fig.suptitle('N12 exact-density expectations: sparse noisy window, not the full16-point curve')
    fig.savefig(F/'n12_sparse_noise_window.png',dpi=170);plt.close(fig);sources.append(p)
dump(F/'n12_window_plot_sources.json',dict(sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],code_sha=sha(__file__),scope='Unmasked values and actual selected circuits. All-q ED/H6 color scales are identical. Connecting lines are visual guides, not interpolation-based extra precision.'))
print('N12 window plots saved')
