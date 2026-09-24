"""Every plotted curve traces an actual saved OBC calculation and analysis."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=OUT/'floating_boundary_scan';rows=[]
for name in ['coarse','bounded','followup','controls']:
 p=O/f'{name}_analysis.json'
 if p.exists():rows.extend(json.loads(p.read_text()))
# Repeated state references are one physical calculation; latest continuation retained separately.
rows=list({r['archive']:r for r in rows}.values());fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained');colors={64:'tab:gray',96:'tab:orange',128:'tab:blue',160:'tab:green',192:'tab:red'}
for r in rows:
 if r['initial']!='plus':continue
 a=r['analysis'];c=a['entropy'][0]['c'];q=np.median([x['q'] for x in a['raw'] if x['kind']=='power']);xi=np.median([x['parameters'][3] for x in a['raw'] if x['kind']=='exponential']);face=colors[r['n']] if r['solver_stopping_pass'] else 'none';size=20 if r['chi']==128 else 45
 for ax,y in zip(axs,[q/np.pi,c,xi/r['n']]):ax.scatter(r['h'],y,s=size,facecolor=face,edgecolor=colors[r['n']],linewidth=.9)
axs[0].axhline(.5,c='k',lw=.7,ls=':');axs[0].set(ylabel='Signed-correlation fitted q / pi');axs[1].axhline(1,c='k',lw=.7,ls=':');axs[1].set(ylabel='Free OBC entropy fit c');axs[2].axhline(1/6,c='k',lw=.7,ls=':');axs[2].set(ylabel='Exponential-model xi / N',yscale='log')
for ax in axs:ax.set(xlabel='h',xlim=(.08,.82));ax.grid(alpha=.15)
for n,c in colors.items():axs[0].scatter([],[],c=c,label=f'N={n}')
axs[0].legend(fontsize=8);fig.suptitle('kappa=0.8 OBC: hollow = stopping tolerance unmet; fits alone do not establish a phase');F=O/'figures';F.mkdir(exist_ok=True);fig.savefig(F/'slice_size_diagnostics.png',dpi=170);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained');plotted=[]
for ax,h in zip(axs,[.3,.4,.7]):
 options=[r for r in rows if r['n']==128 and r['h']==h and r['chi']==256 and r['initial']=='plus']
 if not options:ax.text(.1,.5,'Not executed');continue
 r=options[-1];a=np.load(ROOT/r['archive']);x=np.arange(len(a['central_raw']));ax.plot(x,a['central_raw'],'o-',ms=3,label='raw');ax.plot(x,a['central_connected'],'x--',ms=3,label='connected');ax.axhline(0,c='k',lw=.5);ax.set(xlabel='distance r',ylabel='central signed C(r)',title=f'h={h}, stop={r["solver_stopping_pass"]}');ax.legend();plotted.append(r['archive'])
fig.suptitle('Same midpoint window, both endpoints in central half-chain; all signs/nodes retained');fig.savefig(F/'signed_correlations_controls.png',dpi=170);plt.close(fig)
dump(F/'sources.json',dict(slice=[r['archive'] for r in rows],correlations=plotted,code_sha=sha(__file__)));print('Floating slice plots written from',len(rows),'actual source states')
