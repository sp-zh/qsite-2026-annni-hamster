"""Expose preparation-dependent noise fingerprints at identical Hamiltonians."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
path=OUT/'noise_diagnosability/same_coordinate_cross_structure.json'
data=json.loads(path.read_text());rows=data['rows'];clean=[r for r in rows if r['both_clean_state_pass']]
summary=[]
for p in [0,.01,.05]:
    rr=[r for r in clean if r['p']==p]
    summary.append(dict(p=p,coordinates=len(rr),median_DQ=float(np.median([r['trace_distance'] for r in rr])),
        median_XZ_TV=float(np.median([r['xz_joint_total_variation'] for r in rr])),
        D4_output_disagreements=sum(r['predictions']['B3']['D4']['label']!=r['predictions']['H6']['D4']['label'] for r in rr),
        D5_output_disagreements=sum(r['predictions']['B3']['D5']['label']!=r['predictions']['H6']['D5']['label'] for r in rr)))
dump(OUT/'noise_diagnosability/cross_structure_summary.json',dict(source=str(path.relative_to(ROOT)),sha256=sha(path),summary=summary,
    scope='Same coordinate, B3 versus H6, restricted explicitly to both p0 fidelities >= .99; all26 coordinates remain in the source. Different output is not necessarily a wrong physical label.'))
fig,axs=plt.subplots(1,3,figsize=(12,4),sharex=True,sharey=True,layout='constrained')
for ax,p in zip(axs,[0,.01,.05]):
    for passed,marker,label in [(True,'o','both p0 state-pass'),(False,'x','one/both p0 state-fail')]:
        rr=[r for r in rows if r['p']==p and r['both_clean_state_pass']==passed]
        ax.scatter([r['trace_distance'] for r in rr],[r['xz_joint_total_variation'] for r in rr],marker=marker,label=label,s=26)
    ax.plot([0,1],[0,1],'k:',lw=.7)
    ax.set(title=f'p={p}',xlabel='same-coordinate B3/H6 trace distance',ylabel='same-coordinate XZ total variation',xlim=(-.02,1.02),ylim=(-.02,1.02))
axs[0].legend(fontsize=7)
fig.suptitle('Same physical target, different circuit: noise fingerprints are not phase evidence')
dest=OUT/'noise_diagnosability/figures';dest.mkdir(exist_ok=True)
fig.savefig(dest/'same_coordinate_cross_structure.png',dpi=170);plt.close(fig)
print(summary)
