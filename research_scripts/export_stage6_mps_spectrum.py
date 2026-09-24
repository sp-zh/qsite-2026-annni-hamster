"""Full OBC structure factors derived from saved complete ZZ matrices, no DMRG rerun."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';records={}
for name in ['coarse','bounded','followup','controls']:
 p=O/f'{name}_index.json'
 if p.exists():
  for r in json.loads(p.read_text()):records[r['archive']]=r
rows=[]
for r in records.values():
 a=np.load(ROOT/r['archive']);n=r['n'];zz=a['zz'];connected=a['connected_zz'];q=2*np.pi*np.arange(n)/n;phase=np.exp(1j*q[:,None]*np.arange(n)[None,:]);sf=np.einsum('qi,ij,qj->q',phase,zz,phase.conj()).real/n**2;csf=np.einsum('qi,ij,qj->q',phase,connected,phase.conj()).real/n**2
 assert sf.min()>-1e-10;np.testing.assert_allclose(sf,sf[np.mod(-np.arange(n),n)],atol=1e-10);c=np.array([np.mean(np.diag(zz,k=d)) for d in range(n)]);cc=np.array([np.mean(np.diag(connected,k=d)) for d in range(n)]);fold=sf[:n//2+1];near=np.flatnonzero(fold>=fold.max()*.99)
 key=dict(source_sha=r['sha256'],code=sha(__file__));base=O/'full_spectrum'/uid(key);base.parent.mkdir(exist_ok=True);archive=base.with_suffix('.npz')
 if not archive.exists():np.savez_compressed(archive,q=q,r=np.arange(n),structure_factor=sf,connected_structure_factor=csf,obc_pair_average=c,connected_obc_pair_average=cc,obc_pair_counts=n-np.arange(n))
 rows.append(dict(n=n,kappa=r['kappa'],h=r['h'],chi=r['chi'],initial=r['initial'],source=r['archive'],source_sha=r['sha256'],archive=str(archive.relative_to(ROOT)),sha256=sha(archive),near_max_folded_q=q[near].tolist(),relative_peak_tolerance=.01,interpretation='q and2pi-q folded only for peak reporting; all q retained. Full-chain OBC SF includes edges and1/N self background. OBC pair-average C(r) divides byN-r and does not wrap. Central-pair fits remain separate. SF/C are not independent evidence.'))
dump(O/'full_spectrum_index.json',rows)
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
rr=sorted([r for r in rows if r['n']==64],key=lambda r:r['h']);h=np.array([r['h'] for r in rr]);values=np.array([np.load(ROOT/r['archive'])['structure_factor'] for r in rr]);q=np.load(ROOT/rr[0]['archive'])['q'];fig,ax=plt.subplots(figsize=(9,4));im=ax.pcolormesh(h,q/np.pi,values.T,shading='nearest',vmin=0,vmax=.5,cmap='viridis');ax.set(xlabel='h at kappa=.8',ylabel='all discrete q / pi',title='N64 OBC: full-chain structure factor (self terms retained)');fig.colorbar(im,ax=ax,label='m_q squared');fig.tight_layout();(O/'figures').mkdir(exist_ok=True);fig.savefig(O/'figures/full_wavevector_n64.png',dpi=170);plt.close(fig)
print('Derived spectra',len(rows))
