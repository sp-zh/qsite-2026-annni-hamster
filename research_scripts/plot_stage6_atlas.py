import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':10})
O=OUT/'reference_atlas';F=O/'figures';F.mkdir(exist_ok=True)
ks=PLAN['atlas']['kappa_n8'];hs=np.arange(.05,2.001,.05);slices=json.loads((O/'slices_n8.json').read_text());data=[]
for k in ks:
 vals=[]
 for h in hs:
  r=next(r for r in slices[str(float(k))] if abs(r['h']-h)<1e-10) if str(float(k)) in slices else next(r for r in slices[str(k)] if abs(r['h']-h)<1e-10)
  vals.append([r['structure_factor'][0],r['structure_factor'][2],r['mx']])
 data.append(vals)
data=np.array(data);np.savez_compressed(O/'atlas_plot_data.npz',kappa=ks,h=hs,values=data)
fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for i,title in enumerate(['m(0)^2','m(pi/2)^2','Mx']):
 p=axs[i].pcolormesh(ks,hs,data[:,:,i].T,shading='nearest',vmin=0,vmax=.5 if i==1 else 1);fig.colorbar(p,ax=axs[i]);axs[i].set(xlabel='kappa',ylabel='h',title=title)
fig.suptitle('N=8 PBC ED reference observables; no four-phase truth labels');fig.savefig(F/'atlas_n8.png',dpi=160);plt.close(fig)
low=json.loads((O/'low_field.json').read_text())
ks=PLAN['atlas']['low_kappa'];hs=PLAN['atlas']['low_h'];data=[]
for k in ks:
 vals=[]
 for h in hs:
  r=next(r for r in low if abs(r['kappa']-k)<1e-10 and abs(r['h']-h)<1e-10)
  vals.append([r['structure_factor'][0],r['structure_factor'][2],r['mx']])
 data.append(vals)
data=np.array(data)
np.savez_compressed(O/'low_field_plot_data.npz',kappa=ks,h=hs,values=data);fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for i,title in enumerate(['m(0)^2','m(pi/2)^2','Mx']):
 p=axs[i].pcolormesh(ks,hs,data[:,:,i].T,shading='nearest',vmin=0,vmax=.5 if i==1 else 1);fig.colorbar(p,ax=axs[i]);axs[i].set(xlabel='kappa',ylabel='h',title=title)
fig.suptitle('New low-positive-field reference: nonuniform cells, all108 coordinates');fig.savefig(F/'low_field_reference.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
for ax,n in zip(axs,[8,12,16]):
 rows=json.loads((O/f'slices_n{n}.json').read_text())['0.8'];hh=np.array([r['h'] for r in rows]);sf=np.array([r['structure_factor'] for r in rows]);p=ax.pcolormesh(hh,np.arange(n)*2/n,sf.T,shading='nearest',vmin=0,vmax=.5);ax.set(xlabel='h',ylabel='q/pi',title=f'N={n}, kappa=.8');fig.colorbar(p,ax=ax)
fig.suptitle('All discrete wavevectors; q and2pi-q are equivalent; self background1/N retained');fig.savefig(F/'full_wavevector_reference.png',dpi=160);plt.close(fig)
print('ED reference figures written')
