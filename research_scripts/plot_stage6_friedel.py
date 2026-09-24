"""Show the retained size disagreement rather than selecting the best-looking fit."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_friedel import extract
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=OUT/'floating_boundary_scan';rows=json.loads((O/'friedel_sensitivity.json').read_text())['rows']
latest={}
for r in rows:
    key=(r['n'],r['h'])
    if r['initial']=='plus' and (key not in latest or r['chi']>=latest[key]['chi']):latest[key]=r
fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained');plotdata=[]
for column,h in enumerate([.4,.425,.5]):
    group=sorted([r for r in latest.values() if r['h']==h],key=lambda r:r['n'])
    for r in group:
        x=np.load(ROOT/r['archive'])['x'];j,y,_=extract(x);f=r['original'][0];n=r['n'];mask=np.isin(j,f['sites']);sites=j[mask]
        predicted=(f['coefficients'][0]*np.cos(f['q']*sites)+f['coefficients'][1]*np.sin(f['q']*sites))/(n/np.pi*np.sin(np.pi*sites/n))**f['K']
        scale=max(abs(y[mask]));line=axes[0,column].plot(sites/n,y[mask]/scale,'.',ms=2,label=f'N={n}')[0];axes[0,column].plot(sites/n,predicted/scale,color=line.get_color(),lw=.7)
        for model,marker,key in [('Eq8/B2','o','original'),('Raw + quadratic','x','raw_quadratic_background')]:
            kval=[f['K'] for f in r[key]];axes[1,column].plot([n,n],kval,marker=marker,label=model if n==group[0]['n'] else None,color='C0' if model=='Eq8/B2' else 'C1')
        plotdata.append(dict(n=n,h=h,source_archive=r['archive'],sites=sites,oscillatory=y[mask],predicted=predicted,original=r['original'],raw_quadratic_background=r['raw_quadratic_background']))
    axes[0,column].set(title=f'kappa=.8, h={h}; signed profile',xlabel='j/N',ylabel='Oscillation / maximum magnitude');axes[0,column].legend(fontsize=8)
    axes[1,column].axhspan(.25,.5,color='gray',alpha=.15,label='Paper floating K convention');axes[1,column].set(xlabel='N (OBC)',ylabel='Fitted K; two edge windows',ylim=(0,2.1));axes[1,column].legend(fontsize=7)
fig.suptitle('Friedel fits: good local residuals do not imply size-stable K')
fig.savefig(O/'friedel_size_sensitivity.png',dpi=170);fig.savefig(O/'friedel_size_sensitivity.pdf');plt.close(fig)
dump(O/'friedel_size_sensitivity_plotdata.json',plotdata)
