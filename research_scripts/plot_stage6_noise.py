"""Core same-point noise, mitigation and state-discrimination figures."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=OUT/'end_to_end';F=O/'figures';F.mkdir(exist_ok=True);summary=json.loads((O/'core_summary.json').read_text());methods=['B3',json.loads((OUT/'confirmation/method_frozen.json').read_text())['physical_method']];estimators=['raw','zne','zne_quadratic','sv'];colors={'raw':'#276FBF','zne':'#CC6B32','zne_quadratic':'#4C8265','sv':'#8B6BB1'}
fig,axs=plt.subplots(1,2,figsize=(11,4),sharey=True,layout='constrained')
for ax,method in zip(axs,methods):
 for est in estimators:
  values=[summary[f'{method}_{est}_p{p}_100000']['MSE_ED_mean'] for p in [0,.01,.05]];ax.plot([0,.01,.05],values,'o-',color=colors[est],label=est)
 ax.set(title=method,xlabel='target depolarization p',ylabel='mean MSE against ED',yscale='log');ax.legend()
fig.suptitle('Same core coordinates,100k total shots per repeat;32 repeats, all failures included');fig.savefig(F/'core_equal_shots_mse.png',dpi=170);plt.close(fig)
rows=json.loads((O/'core_analysis.json').read_text());coords=[(.45,.15),(.5,.15),(.55,.15),(.8,.6),(.8,.8),(0.,1.8)];fig,axs=plt.subplots(2,3,figsize=(12,7),sharey=True,layout='constrained');plotdata=[]
for ax,(k,h) in zip(axs.flat,coords):
 r=next((r for r in rows if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12),None)
 if r is None:ax.set_title(f'k={k},h={h}: not in fixed core');continue
 a=np.load(ROOT/r['ed_archive']);q=np.arange(8)*np.pi/4;ax.plot(q/np.pi,a['exact'][8:16],'k--',label='ED');d=dict(kappa=k,h=h,q=q,ED=a['exact'][8:16],curves={})
 for method,style in zip(methods,['-','--']):
  for p,color in zip([0,.01,.05],['#276FBF','#CC6B32','#4C8265']):
   entry=next(e for e in r['entries'] if e['method']==method and e['p']==p and e['estimator']=='raw');v=np.load(ROOT/entry['archive'])['exact'][8:16];ax.plot(q/np.pi,v,style,color=color,label=f'{method} p={p}',lw=1);d['curves'][f'{method}_{p}']=v
 ax.set(title=f'k={k},h={h}',xlabel='all q / pi',ylabel='m_q squared',ylim=(-.01,1.01));plotdata.append(d)
axs.flat[0].legend(fontsize=6,ncol=2);fig.suptitle('Raw exact full structure factors: preparation bias and gate noise both visible');fig.savefig(F/'core_full_sf_noise.png',dpi=170);plt.close(fig);dump(O/'core_full_sf_noise_plot_data.json',plotdata)
p=OUT/'noise_diagnosability/identifiability.json'
if p.exists():
 rr=json.loads(p.read_text());fig,axs=plt.subplots(1,3,figsize=(12,4),sharex=True,sharey=True,layout='constrained')
 for ax,p in zip(axs,[0,.01,.05]):
  for method,marker in zip(methods,['o','x']):
   subset=[r for r in rr if r['method']==method and r['p']==p];ax.scatter([r['trace_distance'] for r in subset],[r['xz_joint_total_variation'] for r in subset],label=method,marker=marker)
  ax.plot([0,1],[0,1],'k:',lw=.7);ax.set(title=f'p={p}',xlabel='quantum trace distance DQ',ylabel='XZ setting+bitstring TV',xlim=(-.02,1.02),ylim=(-.02,1.02));ax.legend()
 fig.suptitle('Fixed binary pairs; TV<=DQ check, not whole-phase classification accuracy');fig.savefig(F/'binary_quantum_measurement_distances.png',dpi=170);plt.close(fig)
print('Noise figures complete')
