"""Raw full-state susceptibility curves, separately costed from local-shot detectors."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
source=OUT/'end_to_end/D2_full_state_windows.json';rows=json.loads(source.read_text())
assert len(rows)==18,'Complete3-window/2-preparation/3-p D2 result required'
methods=['B3','H6'];ks=[.45,.55,.8];fig,axs=plt.subplots(2,3,figsize=(13,7),layout='constrained',sharey=True)
for i,method in enumerate(methods):
    for j,k in enumerate(ks):
        ax=axs[i,j];group=[r for r in rows if r['method']==method and r['kappa']==k]
        first=group[0];ax.plot(first['h_mid'],first['ED_chi'],'k--',lw=1.3,label='Same-N ED reference')
        for p,color in zip([0,.01,.05],['#277DA1','#4D9568','#CC6B32']):
            r=next(r for r in group if r['p']==p);ax.plot(r['h_mid'],r['chi'],'.-',color=color,ms=3,lw=1,label=f'p={p:g}')
        ax.set(title=f'{method}, κ={k:g}',xlabel='h midpoint',yscale='symlog');ax.set_yscale('symlog',linthresh=1)
        if j==0:ax.set_ylabel('D2 squared-Uhlmann susceptibility\nsymlog scale, no curve masking')
        ax.grid(alpha=.15)
axs[0,0].legend(fontsize=8)
fig.suptitle('D2 full density-matrix access; not a10k/100k-local-shot estimator\nLiteral circuit/parameter changes retained; a fidelity-response peak is not automatically a phase boundary')
dest=OUT/'end_to_end/figures/D2_full_state_response_curves.png';fig.savefig(dest,dpi=170);plt.close(fig)
dump(OUT/'end_to_end/D2_plot_source.json',dict(source=str(source.relative_to(ROOT)),sha256=sha(source),figure=str(dest.relative_to(ROOT)),scope='All18actualfull-state curves, common yscale; raw ED/circuit susceptibilities. No finite-shot errorbars or local-measurement resource equivalence implied.'))
print(dest)
