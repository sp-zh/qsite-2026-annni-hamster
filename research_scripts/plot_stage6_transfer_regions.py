"""Show difficult N12 coordinates at their own scales, without hiding failures."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
parser=argparse.ArgumentParser();parser.add_argument('--task',default='n12');task=parser.parse_args().task
data=json.loads((OUT/f'n12_transfer/{task}_paired_summary.json').read_text())['rows']
methods=['B3','C0','C1','H6'];regions=['low_field','antiphase_band','interior']
fig,axs=plt.subplots(len(methods),len(regions),figsize=(11,10),sharex='col',sharey='col',layout='constrained')
categories=[('joint pass','o','#276FBF',lambda r:r['joint_pass']),('observable pass / state fail','s','#CC6B32',lambda r:r['observable_pass'] and not r['state_pass']),('observable fail','x','#884455',lambda r:not r['observable_pass'])]
for i,method in enumerate(methods):
    for j,region in enumerate(regions):
        ax=axs[i,j];rr=[r for r in data if r['method']==method and r['region']==region]
        for label,marker,color,condition in categories:
            a=[r for r in rr if condition(r)];ax.scatter([r['kappa'] for r in a],[r['h'] for r in a],marker=marker,color=color,label=label,s=35)
        ax.set(title=f'{method}: {sum(r["joint_pass"] for r in rr)}/{len(rr)} joint',xlabel='kappa',ylabel='h')
        if i==0:ax.set_title(region.replace('_',' ')+f'\n{method}: {sum(r["joint_pass"] for r in rr)}/{len(rr)} joint')
        if region=='low_field':ax.set(xlim=(.43,.57),ylim=(0,.105))
        elif region=='antiphase_band':ax.set(xlim=(.64,1),ylim=(.20,.55))
        else:ax.set(xlim=(0,1),ylim=(0,1.8))
handles,labels=axs[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3)
fig.suptitle(f'{task}: frozen transfer, separate region scales\nPreparation acceptance categories, not phase labels; all fixed coordinates retained')
folder=OUT/'n12_transfer/figures';folder.mkdir(exist_ok=True)
fig.savefig(folder/f'{task}_region_quality.png',dpi=170);plt.close(fig)
print('Transfer region figure',task)
