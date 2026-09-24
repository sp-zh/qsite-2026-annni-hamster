"""Three-p maps on identical coordinates, with no preparation-quality masking."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch
p=argparse.ArgumentParser();p.add_argument('--task',default='map');task=p.parse_args().task;rows=json.loads((OUT/f'n8_maps/{task}_analysis.json').read_text());baseline=np.load(ROOT/'results/baseline/grid_n8.npz');ks=np.array(baseline['kappa'] if task=='map' else PLAN['atlas']['low_kappa']);hs=np.array([h for h in baseline['h'] if h>0] if task=='map' else PLAN['atlas']['low_h']);new=json.loads((OUT/'confirmation/method_frozen.json').read_text())['physical_method'];methods=['B3',new];ps=[0,.01,.05];F=OUT/'n8_maps/figures';F.mkdir(exist_ok=True);dumpdata=dict(kappa=ks,h=hs)
def grid(method,p,field,extract,est='raw'):
 result=np.full((len(ks),len(hs)),np.nan)
 for r in rows:
  entry=next((x for x in r['entries'] if (x['method'],x['p'],x['estimator'])==(method,p,est)),None)
  if entry is not None:result[np.where(ks==r['kappa'])[0][0],np.where(hs==r['h'])[0][0]]=extract(entry[field])
 return result
for name,index,limits in [('m0_squared',8,(0,1)),('m_pi2_squared',10,(0,.5)),('Mx',16,(-1,1))]:
 fig,axs=plt.subplots(2,3,figsize=(12,7),sharex=True,sharey=True,layout='constrained')
 for i,method in enumerate(methods):
  for j,p in enumerate(ps):
   values=grid(method,p,'exact',lambda v:v[index]);dumpdata[f'{method}_p{p}_{name}_raw_exact']=values;im=axs[i,j].pcolormesh(ks,hs,values.T,shading='nearest',vmin=limits[0],vmax=limits[1],cmap='viridis');axs[i,j].set(title=f'{method}, p={p}',xlabel='kappa',ylabel='h',xlim=(ks[0],ks[-1]),ylim=(hs[0],hs[-1]))
 fig.colorbar(im,ax=axs,label=name);fig.suptitle(f'{task}: raw exact expectations; all executed preparations retained');fig.savefig(F/f'{task}_{name}_raw_three_p.png',dpi=170);plt.close(fig)
labels=['ferro-like','antiphase-like','paramagnetic-like','degraded','uncertain','unmeasured'];colors=['#276FBF','#CC6B32','#4C8265','#8B6BB1','#B8B8B8','#EEEEEE'];cmap=ListedColormap(colors);norm=BoundaryNorm(np.arange(len(labels)+1)-.5,len(labels))
for detector in ['D4','D5']:
 for source,cost in [('predictions_exact','analytic expectations'),('predictions_single','one rep:100k total shots per point/p'),('predictions_mean32','mean of32 reps:3.2M total shots per point/p')]:
  fig,axs=plt.subplots(2,3,figsize=(12,7),sharex=True,sharey=True,layout='constrained')
  for i,method in enumerate(methods):
   for j,p in enumerate(ps):
    values=grid(method,p,source,lambda d:labels.index(d[detector]));dumpdata[f'{method}_p{p}_{detector}_{source}']=values;axs[i,j].pcolormesh(ks,hs,values.T,shading='nearest',cmap=cmap,norm=norm);axs[i,j].set(title=f'{method}, p={p}',xlabel='kappa',ylabel='h',xlim=(ks[0],ks[-1]),ylim=(hs[0],hs[-1]))
  fig.legend(handles=[Patch(color=color,label=label) for color,label in zip(colors,labels)]+[Patch(facecolor='white',edgecolor='black',label='not executed')],loc='outside lower center',ncol=3);fig.suptitle(f'{task}: frozen {detector} pattern outputs; {cost}\nNot independent four-phase truth; no quality mask or spatial smoothing');fig.savefig(F/f'{task}_{detector}_{source}.png',dpi=170);plt.close(fig)
frozen=json.loads((OUT/'end_to_end/mitigation_frozen.json').read_text())['selected']
fig,axs=plt.subplots(2,3,figsize=(12,7),sharex=True,sharey=True,layout='constrained')
for i,method in enumerate(methods):
 for j,p in enumerate(ps):
  estimator=frozen[method];values=grid(method,p,'predictions_single',lambda d:labels.index(d['D4']),estimator);dumpdata[f'{method}_p{p}_D4_frozen_estimator_rep0_100k']=values;axs[i,j].pcolormesh(ks,hs,values.T,shading='nearest',cmap=cmap,norm=norm);axs[i,j].set(title=f'{method}, {estimator}, p={p}',xlabel='kappa',ylabel='h',xlim=(ks[0],ks[-1]),ylim=(hs[0],hs[-1]));axs[i,j].title.set_fontsize(10)
fig.legend(handles=[Patch(color=color,label=label) for color,label in zip(colors,labels)]+[Patch(facecolor='white',edgecolor='black',label='not executed')],loc='outside lower center',ncol=4);fig.suptitle(f'{task}: validation-frozen estimator, D4, single100k-total-shot repeat\nPattern outputs, not truth labels; all settings/scales share budget; no quality mask');fig.savefig(F/f'{task}_D4_frozen_estimator_single.png',dpi=170);plt.close(fig)
np.savez_compressed(OUT/f'n8_maps/{task}_plot_data.npz',**dumpdata)
print('plotted',task,len(rows),'coordinates')
