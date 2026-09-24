"""Replot candidate resource, accuracy, seed stability and full-SF comparisons."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.stage6_io import candidate_rows
from annni.upgrade_gates import observations,vector
parser=argparse.ArgumentParser();parser.add_argument('--task',default='confirmation');task=parser.parse_args().task
folder=OUT/('confirmation' if task in ['confirmation','stability'] else 'n12_transfer' if task.startswith('n12') else 'failure_mechanisms');data=json.loads((folder/f'{task}_paired_summary.json').read_text());rows=data['rows'];methods=sorted({r['method'] for r in rows});dest=folder/'figures';dest.mkdir(exist_ok=True)
fig,axs=plt.subplots(2,len(methods),figsize=(3.6*len(methods),6.4),squeeze=False,sharex='row',sharey='row')
for i,m in enumerate(methods):
 rr=[r for r in rows if r['method']==m]
 for passed,marker,color,label in [(True,'o','#276FBF','joint pass'),(False,'x','#CC6B32','joint fail')]:
  subset=[r for r in rr if r['joint_pass']==passed];axs[0,i].scatter([r['kappa'] for r in subset],[r['h'] for r in subset],marker=marker,color=color,s=25,label=label)
 axs[0,i].set(title=f"{m}: {sum(r['joint_pass'] for r in rr)}/{len(rr)} joint pass",xlabel='kappa',ylabel='h');axs[0,i].legend(fontsize=7)
 scatter=axs[1,i].scatter([r['cnots'] for r in rr],[max(r['delta_e'],1e-12) for r in rr],c=[r['fidelity'] for r in rr],cmap='viridis',vmin=0,vmax=1,s=24);axs[1,i].axhline(.001,c='red',ls='--',lw=.8);axs[1,i].set(yscale='log',xlabel='actual CNOT count',ylabel='energy error per spin')
fig.suptitle(f'{task}: state acceptance is distinct from phase identification');fig.tight_layout(rect=[0,0,.92,1])
fig.colorbar(scatter,cax=fig.add_axes([.94,.12,.012,.30]),label='ED squared fidelity');fig.savefig(dest/f'{task}_accuracy_resources.png',dpi=160);plt.close(fig)
# No ED-based selection change: show already-selected circuits at fixed benchmark coordinates.
source=candidate_rows(task);chosen=source[:min(6,len(source))];fig,axs=plt.subplots(2,3,figsize=(12,6.8),squeeze=False);sfdata=[]
for ax,point in zip(axs.flat,chosen):
 n=point['n'];q=np.arange(n)*2*np.pi/n;first=True;stored=dict(n=n,kappa=point['kappa'],h=point['h'],q=q,curves={})
 for name,value in point['methods'].items():
  r=next(r for r in rows if r['method']==name and r['source']==value['selected']['archive']);v=vector(observations(np.load(ROOT/r['source'])['state'],n));e=vector(observations(np.load(ROOT/r['ed_source'])['state'],n));ax.plot(q/np.pi,v[n:2*n],'.-',label=name);stored['curves'][name]=v[n:2*n]
  if first:ax.plot(q/np.pi,e[n:2*n],'k--',label='same-N ED');stored['ED']=e[n:2*n];first=False
 ax.set(title=f"k={point['kappa']}, h={point['h']}",xlabel='q / pi',ylabel='m_q squared',ylim=(-.02,1.02));ax.legend(fontsize=7);sfdata.append(stored)
fig.suptitle('All discrete wavevectors; self-correlation 1/N retained');fig.tight_layout();fig.savefig(dest/f'{task}_full_structure_factor.png',dpi=160);plt.close(fig);dump(folder/f'{task}_structure_factor_plot_data.json',sfdata)
if task=='stability':
 groups={}
 for r in rows:groups.setdefault((r['kappa'],r['h'],r['method']),[]).append(r)
 fig,ax=plt.subplots(figsize=(10,4))
 for i,m in enumerate(methods):
  vals=[sum(r['joint_pass'] for r in v)/len(v) for (k,h,name),v in groups.items() if name==m];ax.plot(range(len(vals)),vals,'.-',label=m)
 ax.set(xlabel='fixed coordinate index',ylabel='independent seed pass fraction',ylim=(-.05,1.05));ax.legend();fig.tight_layout();fig.savefig(dest/'independent_seed_stability.png',dpi=160);plt.close(fig)
print('plotted',task)
