"""Small-size OBC/PBC bridge; no transfer of large-OBC labels to N8 PBC."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from annni.upgrade_gates import diagonals
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigsh
rows=[]
for n in [8,12]:
 ids,z,flips=geometry(n);nn,nnn,_=diagonals(n,'open');size=1<<(n-1);reps=ids[:size];targets=np.concatenate([f[:size] for f in flips]);targets=np.minimum(targets,((1<<n)-1)^targets);x=coo_matrix((np.ones(n*size),(np.tile(reps,n),targets)),shape=(size,size)).tocsr()
 for h in [.15,.3,.325,.35,.4,.45,.5,.55,.6,.7,.8]:
  guard();t=time.perf_counter();a=diags((-nn+.8*nnn)[:size])-h*x;e,s=eigsh(a,k=2,which='SA',v0=np.ones(size)/np.sqrt(size),tol=1e-13,maxiter=20000);order=np.argsort(e);e=e[order];reduced=s[:,order[0]];state=np.r_[reduced,reduced[::-1]]/np.sqrt(2);p=abs(state)**2;zz=np.einsum('i,ij,ik->jk',p,z,z);corr=np.array([np.mean(np.diag(zz,r)) for r in range(n)]);mx=sum(np.vdot(state,state[f]).real for f in flips)/n;q=np.arange(n)*2*np.pi/n;sf=np.array([np.einsum('ij,ij->',np.exp(1j*w*(np.arange(n)[:,None]-np.arange(n)[None,:])),zz).real/n**2 for w in q]);pbc=record(n,.8,h);key=dict(n=n,kappa=.8,h=h,bc='OBC',code=sha(__file__));path=OUT/'floating_boundary_scan/bridge'/uid(key);path.parent.mkdir(exist_ok=True);archive=path.with_suffix('.npz');np.savez_compressed(archive,state=state,zz=zz,correlations=corr,structure_factor=sf,mx=mx,q=q);rows.append(dict(key=key,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),energy=float(e[0]),global_flip_even_sector_gap=float(e[1]-e[0]),residual=float(np.linalg.norm(h_action(state,n,.8,h,bc='open')-e[0]*state)),sector='P=+1 only; no translation symmetry assumed for OBC',pbc_reference=pbc['archive'],obc_mx=mx,obc_m0=sf[0],obc_map=sf[n//4],pbc_mx=pbc['mx'],pbc_m0=pbc['structure_factor'][0],pbc_map=pbc['structure_factor'][n//4],seconds=time.perf_counter()-t));dump(OUT/'floating_boundary_scan/bridge_index.json',rows)
print('New small-size bridge:',len(rows))
