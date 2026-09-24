"""Unmasked same-coordinate RN response curves with shared scales across noise."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_diagnostics import response_curves,peaks_and_primary
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=OUT/'end_to_end/boundary_curves.json';data=json.loads(source.read_text())
dest=OUT/'end_to_end/figures';dest.mkdir(exist_ok=True)
styles=[('B3','raw','#276FBF','-'),('H6','raw','#CC6B32','-'),('B3','zne_quadratic','#276FBF','--'),('H6','zne_quadratic','#CC6B32','--')]
plotdata=[]
fig,axs=plt.subplots(3,3,figsize=(12,9),sharey='row',layout='constrained')
for i,k in enumerate([.45,.55,.8]):
    name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh'
    base=data[f'{k}_B3_pure'];h=np.array(base['h']);hm=(h[:-1]+h[1:])/2
    ey=response_curves(h,np.array(base['reference']),8)[name];reference=peaks_and_primary(h,ey)
    for j,p in enumerate([0,.01,.05]):
        ax=axs[i,j];ax.plot(hm,ey,'k.-',label='same-N ED',lw=1.3)
        peak=reference['primary']
        if peak:ax.axvspan(peak['interval_low'],peak['interval_high'],color='grey',alpha=.16,label='ED grid interval')
        for method,est,color,ls in styles:
            v=data[f'{k}_{method}_{p}_{est}'];y=response_curves(h,np.array(v['values']),8)[name]
            ax.plot(hm,y,ls,color=color,marker='.',markersize=3,lw=1,label=f'{method} '+('raw' if est=='raw' else 'quadratic ZNE'))
            plotdata.append(dict(kappa=k,p=p,method=method,estimator=est,h_mid=hm,response=y,ED_response=ey))
        ax.set(title=f'kappa={k}, p={p}',xlabel='h midpoint',ylabel='-d m0 squared / dh' if k<.5 else '-d m(pi/2) squared / dh')
handles,labels=axs[0,0].get_legend_handles_labels()
fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=9)
fig.suptitle('Exact expectation curves; same frozen difference/peak rule, no quality mask\nFinite-size response intervals, not thermodynamic boundaries')
fig.savefig(dest/'RN_noisy_response_curves.png',dpi=170);plt.close(fig)
fig,axs=plt.subplots(2,3,figsize=(12,6.8),layout='constrained')
for ax,k in zip(axs.flat,[0.,.3,.45,.5,.55,.8]):
    base=data[f'{k}_B3_pure'];h=np.array(base['h']);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';hm=(h[:-1]+h[1:])/2
    ax.plot(hm,response_curves(h,np.array(base['reference']),8)[name],'k.-',label='ED')
    for method,color in [('B3','#276FBF'),('H6','#CC6B32')]:ax.plot(hm,response_curves(h,np.array(data[f'{k}_{method}_pure']['values']),8)[name],'.-',color=color,label=method)
    ax.set(title=f'kappa={k}',xlabel='h midpoint',ylabel='named order response');ax.legend(fontsize=8)
fig.suptitle('All six requested p0 windows; kappa=.5 reference remains unresolved')
fig.savefig(dest/'RN_pure_response_curves.png',dpi=170);plt.close(fig)
dump(OUT/'end_to_end/RN_response_plot_data.json',dict(source=str(source.relative_to(ROOT)),sha256=sha(source),rows=plotdata,scope='Exact simulated expectations. ZNE fit uses p>0 folded data only; no ED or p0 truth inserted. No new measurements, interpolation or smoothing.'))
print('RN boundary figures saved')
