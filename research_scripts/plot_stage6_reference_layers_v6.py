"""Plot independent region coverage, RN diagnostics and OBC evidence separately."""
import sys,csv,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import ROOT,OUT,sha,dump
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
A=OUT/'reference_atlas';F=A/'figures';F.mkdir(exist_ok=True)
paths=[A/'reference_regions_v6.csv',A/'boundary_reference_v6.csv',OUT/'floating_boundary_scan/evidence_map_v4.csv']
r,b,m=[list(csv.DictReader(p.open())) for p in paths]
fig,axs=plt.subplots(1,3,figsize=(15,5.4),layout='constrained')
colors={'ferro-like':'#277DA1','antiphase-like':'#D17B0F','paramagnetic-like':'#679436'}
seen=set()
for row in r:
 if row['bc']!='PBC':continue
 key=(row['kappa'],row['h'])
 if key in seen:continue
 seen.add(key);label=row['physical_label'];proxy=row['RN_proxy_label'];x,y=float(row['kappa']),float(row['h'])
 axs[0].scatter(x,y,s=18 if label else 10,marker='o' if label else 'x',color=colors.get(label,'#b8b8b8'),alpha=.85)
for label,col in colors.items():axs[0].scatter([],[],color=col,s=20,label=label+' interior')
axs[0].scatter([],[],color='#b8b8b8',s=12,marker='x',label='No independent physical label')
axs[0].set(xlabel='kappa',ylabel='h',title='Physical reference labels at evaluated points');axs[0].legend(fontsize=7,loc='upper left',bbox_to_anchor=(0,-.17))
features={'minus_dm0_dh':('o','#277DA1','- d m0²/dh'),'minus_dmap_dh':('s','#D17B0F','- d m(pi/2)²/dh'),'dmx_dh':('^','#679436','d Mx/dh'),'chi_f':('D','#9467bd','fidelity susceptibility')}
for row in b:
 if row['bc']!='PBC' or str(row['n'])!='8' or row['resolvable']!='True' or row['feature'] not in features:continue
 marker,col,label=features[row['feature']];pos=float(row['position']);lo=float(row['low']);hi=float(row['high'])
 axs[1].errorbar(float(row['kappa']),pos,yerr=[[pos-lo],[hi-pos]],fmt=marker,color=col,ms=4,lw=.8)
for marker,col,label in features.values():axs[1].plot([],[],marker=marker,color=col,ls='none',label=label)
axs[1].scatter([0],[1],marker='*',s=95,color='black',label='Exact bulk Ising point (R0)')
paths.append(A/'analytic_Ising_reference.json')
axs[1].set(xlabel='kappa',ylabel='h',title='N=8 PBC: separately named RN features');axs[1].legend(fontsize=7,loc='upper left',bbox_to_anchor=(0,-.17),title='Grid intervals, not statistical confidence intervals',title_fontsize=7)
categories=[('supported_antiphase_sample','Supported AP',colors['antiphase-like']),('candidate_floating','Candidate floating','#9467bd'),('supported_floating_sample','Supported floating','#2a9d8f'),('supported_paramagnetic_side_sample','Supported PM side',colors['paramagnetic-like']),('unresolved','Unresolved / incomplete','#999999')]
for row in m:
 status=row['status'];cat=next((i for i,(key,_,_) in enumerate(categories[:4]) if key in status),4)
 axs[2].scatter(float(row['h']),cat,color=categories[cat][2],s=42,marker='o')
axs[2].set(yticks=range(5),yticklabels=[x[1] for x in categories],xlabel='h at kappa=0.8',title='Large-N OBC evidence v4: discrete samples',ylim=(-.5,4.5),xlim=(.075,.825));axs[2].invert_yaxis()
for ax in axs:ax.grid(alpha=.15)
fig.suptitle('Reference layers have different scope; no OBC labels transferred onto the PBC grid',fontsize=12)
fig.savefig(F/'reference_layers_v6.png',dpi=170);plt.close(fig)
dump(F/'reference_layers_v6_sources.json',dict(sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in paths],code_sha=sha(__file__),data=dict(regions=r,RN_features=b,OBC_evidence=m)))
print('Reference layers plotted from v6 atlas and v4 OBC evidence')
