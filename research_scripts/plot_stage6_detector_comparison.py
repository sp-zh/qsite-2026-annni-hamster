"""All old/new frozen detectors on the same labelled subset and shot budget."""
import sys,argparse,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--task',default='core');task=p.parse_args().task
source=OUT/f'end_to_end/{task}_summary.json';data=json.loads(source.read_text());rows=[]
detectors=['D1','D3','D4','D5'];methods=['B3','H6'];estimators=['raw','zne_quadratic']
fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True,sharey=True,layout='constrained')
for i,method in enumerate(methods):
    for j,pval in enumerate([.01,.05]):
        ax=axs[i,j]
        for offset,estimator,color in [(-.18,'raw','#277DA1'),(.18,'zne_quadratic','#CC6B32')]:
            key=f'{method}_{estimator}_p{pval}_100000'
            if key not in data:continue
            r=data[key];values=[];covered=[]
            for detector in detectors:
                counts=r['label_repeat_counts'][detector]['physical_label'];labelled=sum(v for k,v in counts.items() if k!='reference_unlabelled');correct=counts.get('correct',0)
                values.append(correct/labelled if labelled else np.nan);covered.append(labelled/32)
                rows.append(dict(method=method,estimator=estimator,p=pval,detector=detector,total_coordinates=r['physical_coordinates'],labelled_coordinate_equivalents=labelled/32,correct_coordinate_equivalents=correct/32,rejected_coordinate_equivalents=counts.get('rejected',0)/32,wrong_accepted_coordinate_equivalents=counts.get('wrong_accepted',0)/32,unlabelled_coordinates=counts.get('reference_unlabelled',0)/32,total_shots=r['total_shots'],total_gate_shots=r['total_gate_shots']))
            assert len(set(covered))==1
            ax.bar(np.arange(4)+offset,values,width=.34,color=color,label=estimator)
        ax.set(title=f'{method}, p={pval}; labelled subset only',xticks=range(4),xticklabels=detectors,ylim=(0,1.08),ylabel='Correct fraction given independent label');ax.grid(axis='y',alpha=.15);ax.legend(fontsize=8)
fig.suptitle(f'{task}: all frozen detectors; 100k total shots/repeat, 32 repeats\nQuadratic ZNE has greater CNOT-shot cost; unlabelled coordinates are not assigned accuracy')
F=OUT/'end_to_end/figures';F.mkdir(exist_ok=True);fig.savefig(F/f'{task}_all_detector_comparison.png',dpi=170);plt.close(fig)
dump(OUT/f'end_to_end/{task}_all_detector_comparison.json',dict(rows=rows,source=str(source.relative_to(ROOT)),source_sha=sha(source),scope='Same physical-labelled subset, repeat-normalized counts. Old D1/D3 and new D4/D5 are all retained; no per-point detector switching. This is not whole-map accuracy. See regional ladder for phase-balanced/region-level breakdown.'))
with (OUT/f'end_to_end/{task}_all_detector_comparison.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(task,'detector comparison rows',len(rows))
