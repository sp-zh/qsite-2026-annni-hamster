"""All requested ideal-information windows, including the unresolved reference."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=OUT/'end_to_end/ideal_ED_detector_boundaries.json';data=json.loads(source.read_text());rows=data['rows'];ks=sorted({r['kappa'] for r in rows})
fig,axs=plt.subplots(3,len(ks),figsize=(18,8),layout='constrained')
for col,k in enumerate(ks):
    d4=next(r for r in rows if r['kappa']==k and r['detector']=='D4');d5=next(r for r in rows if r['kappa']==k and r['detector']=='D5');ref=d4['reference']['primary']
    curves=[d4['ED_named_response'],d4['response'],d5['response']]
    for i,(curve,label) in enumerate(zip(curves,['ED order response','Frozen D4 contrast response','Frozen D5 contrast response'])):
        ax=axs[i,col];ax.plot(d4['h_mid'],curve,'.-',lw=1,ms=3,color=['#444444','#277DA1','#CC6B32'][i]);ax.grid(alpha=.15)
        if ref and d4['reference_resolvable']:
            ax.axvspan(ref['interval_low'],ref['interval_high'],color='grey',alpha=.2)
            ax.axvline(ref['coordinate'],color='black',ls=':',lw=.8)
        if i:
            r=d4 if i==1 else d5;p=r['result']['primary']
            if p:ax.axvline(p['coordinate'],color='#AD375B',ls='--',lw=.9)
        if col==0:ax.set_ylabel(label+'\n(each row has its own units)')
        if i==0:ax.set_title(f'κ={k:g}'+(' (reference unresolved)' if not d4['reference_resolvable'] else ''))
        if i==2:ax.set_xlabel('h midpoint')
        ax.tick_params(labelsize=8)
fig.suptitle('Perfect same-N ED information supplied to frozen detectors; no circuit / gate-noise / shots\nGrey band: named physical-observable RN grid interval; dashed red: detector primary response (not thermodynamic phase truth)')
dest=OUT/'end_to_end/figures/ideal_ED_detector_response_controls.png';fig.savefig(dest,dpi=160);plt.close(fig)
dump(OUT/'end_to_end/ideal_ED_detector_plot_source.json',dict(source=str(source.relative_to(ROOT)),sha256=sha(source),figure=str(dest.relative_to(ROOT)),scope='All six requested windows. Separate response units, all raw grid values, no smoothing or amplitude normalization.'))
print(dest)
