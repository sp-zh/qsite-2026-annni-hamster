import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from annni.upgrade_adapt import *
from annni.upgrade_detection import predict
from annni.upgrade_gates import vector
cfg=json.loads((OUT/'detection/frozen.json').read_text());old=json.loads((ROOT/'results/stage3_v1/grid/observations.json').read_text());new=json.loads((OUT/'map/noise_index.json').read_text());fig,axs=plt.subplots(1,2,figsize=(11,4.3));colors=['#2a788e','#a65b9a','#e9c46a','#555555','#dddddd'];labels=cfg['labels']
for ax,method in zip(axs,['B0','B3']):
 records=[r for r in old if r['p']==.01] if method=='B0' else [next(r for r in p['methods']['B3'] if r['p']==.01) for p in new];v=np.zeros((21,20));fails=[]
 for r in records:
  a=np.load(ROOT/r['archive']);i=round(r['kappa']/.05);j=round(r['h']/.1)-1;d=predict(vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx']))),cfg);v[i,j]=labels.index(d['D1'])
  if r['preparation_failed'] if method=='B0' else not r['prep_joint_pass']:fails.append((r['h'],r['kappa']))
 ax.imshow(v,origin='lower',extent=[.05,2.05,-.025,1.025],aspect='auto',cmap=ListedColormap(colors),norm=BoundaryNorm(np.arange(-.5,5),5));ax.scatter(*np.array(fails).T,c='red',marker='x',s=14);ax.set(title=method+(' historical HVA' if method=='B0' else ' multireference ADAPT'),xlabel='h',ylabel='kappa')
fig.legend([plt.Line2D([0],[0],color=c,lw=8) for c in colors],labels,loc='lower center',ncol=5,fontsize=9);fig.suptitle('p=0.01, frozen D1: red crosses mark failed preparation');fig.tight_layout(rect=[0,.08,1,.94]);fig.savefig(OUT/'submission/figures/presentation_maps.png',dpi=160)
