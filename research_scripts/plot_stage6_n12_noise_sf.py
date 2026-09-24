"""All twelve preselected N12 coordinates, all discrete q, shared colour scale."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import measurement_rows
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
points=measurement_rows((OUT/'end_to_end').glob('n12_*_index.json'))
assert len(points)==12
analysis=json.loads((OUT/'end_to_end/n12_analysis.json').read_text())
ed={(r['kappa'],r['h']):np.load(ROOT/r['ed_archive'])['exact'][12:24] for r in analysis}
target=np.array([ed[r['kappa'],r['h']] for r in points])
fig,axs=plt.subplots(2,4,figsize=(15,8),layout='constrained',sharex=True,sharey=True)
saved={'ED':target};sources=[]
for i,method in enumerate(['B3','H6']):
    values=[target]
    for p in [0,.01,.05]:
        entries=[next(e['record'] for e in r['entries'] if e['method']==method and e['record']['p']==p and e['estimator']=='raw') for r in points]
        v=np.array([np.load(ROOT/r['archive'])['exact'][12:24] for r in entries]);values.append(v);saved[f'{method}_p{p}']=v
        sources.extend(dict(archive=r['archive'],sha256=r['sha256']) for r in entries)
    for j,(value,title) in enumerate(zip(values,['Same ED target','p=0','p=.01','p=.05'])):
        im=axs[i,j].imshow(value,vmin=0,vmax=1,aspect='auto',origin='lower',cmap='viridis')
        axs[i,j].set_title(f'{method}: {title}');axs[i,j].set_xticks([0,3,6,9,11],['0','π/2','π','3π/2','11π/6'])
        if i==1:axs[i,j].set_xlabel('q (all 12 wavevectors retained)')
    labels=[f"({r['kappa']:.4g}, {r['h']:.4g})" for r in points]
    axs[i,0].set_yticks(range(12),labels,fontsize=8);axs[i,0].set_ylabel('Fixed coordinate list (κ,h); not a uniform h axis')
fig.colorbar(im,ax=axs,shrink=.8,label='m_q², including 1/N self-correlation background')
fig.suptitle('N12 exact-density structure factors: identical coordinates and colour scales\nED is an ideal-information reference; both rows repeat the same ED target')
O=OUT/'n12_transfer';fig.savefig(O/'figures/n12_all_q_noise.png',dpi=170);plt.close(fig)
np.savez_compressed(O/'all_q_noise_plotdata.npz',coordinates=np.array([[r['kappa'],r['h']] for r in points]),q=2*np.pi*np.arange(12)/12,**saved)
dump(O/'all_q_noise_sources.json',dict(sources=sources,scope='Exact simulated observables, no measurement shot uncertainty in this figure. No per-panel normalization or omitted failed preparations. Coordinate rows are an explicitly labelled list, not a spatially uniform phase grid.'))
print('N12 all-q noise plot complete')
