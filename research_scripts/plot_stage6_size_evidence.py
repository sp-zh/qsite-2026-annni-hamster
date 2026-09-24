"""Independent finite-size observable/spectral evidence, without classifier labels."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.stage6_diagnostics import response_curves
O=OUT/'reference_atlas';F=O/'figures';F.mkdir(exist_ok=True);saved=[]
fig,axs=plt.subplots(4,4,figsize=(13,10),layout='constrained')
for col,k in enumerate([.3,.45,.55,.8]):
 for n,color in [(8,'#277DA1'),(12,'#D17B0F'),(16,'#679436')]:
  source=O/f'slices_n{n}.json';rows=json.loads(source.read_text())[str(k)];h=np.array([r['h'] for r in rows]);sf=np.array([r['structure_factor'] for r in rows]);mx=np.array([r['mx'] for r in rows]);gap=np.array([r['sector_gap'] for r in rows]);vals=np.array([r['correlations']+r['structure_factor']+[r['mx']] for r in rows]);states=[np.load(ROOT/r['archive'])['state'] for r in rows];curves=response_curves(h,vals,n,states,[r['reference_numerical_ambiguous'] for r in rows]);q=0 if k<.5 else n//4
  for ax,x,y in [(axs[0,col],h,sf[:,q]),(axs[1,col],h,mx),(axs[2,col],h,gap),(axs[3,col],curves['h_mid'],curves['chi_f'])]:ax.plot(x,y,'.-',color=color,label=f'N={n}',ms=2,lw=1)
  saved.append(dict(n=n,kappa=k,h=h,selected_sf=sf[:,q],selected_q=2*np.pi*q/n,mx=mx,sector_gap=gap,h_mid=curves['h_mid'],chi_f=curves['chi_f'],source=str(source.relative_to(ROOT)),sha256=sha(source)))
 axs[0,col].set_title(f'kappa={k}; '+('q=0' if k<.5 else 'q=pi/2'))
 axs[0,col].set_ylim(0,1 if k<.5 else .5)
 for ax in axs[:,col]:ax.set_xlim(0,1.5);ax.grid(alpha=.15)
 axs[-1,col].set_xlabel('h (chi_F plotted at interval midpoint)')
 axs[2,col].set_yscale('log');axs[3,col].set_yscale('symlog',linthresh=.1);axs[3,col].set_ylim(bottom=0)
for ax,title in zip(axs[:,0],['m_q² (self terms retained)','Mx','P=+,T=0 sector gap','Squared-overlap chi_F']):ax.set_ylabel(title)
axs[0,0].legend(fontsize=8);fig.suptitle('N=8/12/16 PBC evidence: sector gap is not the full-space ground-state splitting\nDifferent sampled h steps remain explicit; peaks are finite-size features, not exact phase boundaries',fontsize=11);fig.savefig(F/'multi_size_physical_evidence.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(11,3.8),layout='constrained')
for ax,k in zip(axs,[0,.3,.45]):
 for n,col in [(8,'#277DA1'),(12,'#D17B0F'),(16,'#679436')]:
  rows=json.loads((O/f'slices_n{n}.json').read_text())[str(k)];ax.plot([r['h'] for r in rows],[r['binder'] for r in rows],'.-',ms=2,lw=1,color=col,label=f'N={n}')
 ax.set(xlabel='h',ylabel='U4 = 1 - <m0^4>/(3 <m0^2>²)',title=f'kappa={k}',xlim=(0,1.5));ax.grid(alpha=.15)
axs[0].legend();fig.suptitle('Ferromagnetic Binder diagnostic: size trends retained, no fitted thermodynamic crossing claim');fig.savefig(F/'ferromagnetic_binder_sizes.png',dpi=160);plt.close(fig)
dump(F/'size_evidence_data.json',saved);print('Multisize ED evidence plotted from existing states only')
