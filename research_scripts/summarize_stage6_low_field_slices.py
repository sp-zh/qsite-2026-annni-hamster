"""Descriptive per-kappa low-field comparison, separate from confirmation/area."""
import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=OUT/'failure_mechanisms/low_map_paired_summary.json'
data=json.loads(source.read_text())['rows'];rows=[]
for k in sorted({r['kappa'] for r in data}):
    for method in ['B3','C0','H6']:
        rr=[r for r in data if r['method']==method and r['kappa']==k]
        rows.append(dict(kappa=k,method=method,coordinates=len(rr),joint_pass=sum(r['joint_pass'] for r in rr),observable_pass=sum(r['observable_pass'] for r in rr),state_pass=sum(r['state_pass'] for r in rr),candidate_exists=sum(r['candidate_pool_exists'] for r in rr),median_CNOT=float(np.median([r['cnots'] for r in rr])),search_nfev=sum(r['search_nfev'] for r in rr)))
O=OUT/'n8_maps';dump(O/'low_field_slice_accuracy.json',dict(rows=rows,source=str(source.relative_to(ROOT)),source_sha=sha(source),scope='Descriptive108-point grid,12 nonuniform h samples per kappa. These point counts are not area-weighted phase accuracy or a new blind test. Confirmation is separate; no post-test selector alteration.'))
with (O/'low_field_slice_accuracy.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
fig,axs=plt.subplots(1,2,figsize=(11,4),sharex=True,sharey=True,layout='constrained')
for method,col in [('B3','#277DA1'),('C0','#888888'),('H6','#CC6B32')]:
    rr=[r for r in rows if r['method']==method]
    for ax,key in zip(axs,['joint_pass','observable_pass']):
        ax.plot([r['kappa'] for r in rr],[r[key]/r['coordinates'] for r in rr],'.-',color=col,label=method)
for ax,title in zip(axs,['Joint preparation acceptance','Observable acceptance']):
    ax.axvline(.5,color='black',ls=':',lw=.8);ax.set(xlabel='kappa',ylabel='Passed /12 requested h samples',ylim=(-.03,1.03),title=title);ax.grid(alpha=.15);ax.legend()
fig.suptitle('Descriptive low-field grid: gains and regressions retained; dotted line is classical kappa=.5')
(O/'figures').mkdir(exist_ok=True);fig.savefig(O/'figures/low_field_slice_accuracy.png',dpi=170);plt.close(fig)
print('Low-field kappa slices',len(rows))
