"""Independent P=+1,T=1 orbit ED. No detector labels enter this solver."""
from functools import lru_cache
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigsh
from .stage6_common import *
from .upgrade_gates import geometry,h_action,observations
@lru_cache(4)
def sector(n):
 dim=1<<n; orbit=np.full(dim,-1,int);members=[]
 for b in range(dim):
  if orbit[b]>=0:continue
  x=b;s=set()
  for _ in range(n):
   s.update([x,(dim-1)^x]);x=((x<<1)&(dim-1))|(x>>(n-1))
  m=np.array(sorted(s));orbit[m]=len(members);members.append(m)
 sizes=np.array([len(m) for m in members]);reps=np.array([m[0] for m in members]);z=1-2*((reps[:,None]>>np.arange(n-1,-1,-1))&1)
 nn=(z*np.roll(z,-1,axis=1)).sum(1);nnn=(z*np.roll(z,-2,axis=1)).sum(1)
 rows=[];cols=[];data=[]
 for j,b in enumerate(reps):
  for i in range(n):
   target=orbit[b^(1<<i)];rows.append(target);cols.append(j);data.append(np.sqrt(sizes[j]/sizes[target]))
 x=coo_matrix((data,(rows,cols)),shape=(len(reps),len(reps))).tocsr()
 assert abs(x-x.T).max()<1e-12
 return orbit,sizes,nn,nnn,x
def solve(n,k,h):
 assert h>0
 orbit,sizes,nn,nnn,x=sector(n);a=diags(-nn+k*nnn)-h*x
 es,vs=eigsh(a,k=3,which='SA',v0=np.sqrt(sizes/(1<<n)),tol=2e-14,maxiter=30000)
 order=np.argsort(es);es=es[order];vs=vs[:,order];v=vs[:,0];v*=1 if v.sum()>0 else -1
 state=v[orbit]/np.sqrt(sizes[orbit]);res=float(np.linalg.norm(h_action(state,n,k,h)-es[0]*state));gap=float(es[1]-es[0]);ambiguous=bool(gap<=100*max(res,1e-14))
 return state,float(es[0]),dict(sector_energies=es.tolist(),sector_gap=gap,residual=res,residual_gap_ratio=res/max(gap,1e-300),reference_numerical_ambiguous=ambiguous,sector_dimension=len(sizes),sector='P=+1,T=1; gap is sector-excitation gap, not full-space ground splitting')
def record(n,k,h):
 guard();k=float(k);h=float(h);key=dict(n=n,kappa=k,h=h,bc='PBC',code=sha(__file__),model=sha(ROOT/'annni/upgrade_gates.py'));base=OUT/'reference_atlas/cache'/uid(key);p=base.with_suffix('.json')
 if p.exists():
  r=json.loads(p.read_text());assert r['key']==key and sha(ROOT/r['archive'])==r['sha256'];return r
 t=time.perf_counter();state,e,extra=solve(n,k,h);source='newly_executed';old=None
 if n==8:
  a=np.load(ROOT/'results/baseline/grid_n8.npz');ii=np.flatnonzero(abs(a['kappa']-k)<1e-13);jj=np.flatnonzero(abs(a['h']-h)<1e-13)
  if len(ii)==len(jj)==1:
   old=a['states'][ii[0],jj[0]];extra['historical_state_fidelity']=float(abs(np.vdot(old,state))**2)
   # Existing ground state reused only when same-sector cross-check is numerically unambiguous.
   if extra['historical_state_fidelity']>1-1e-10:
    state=old;source='historical_ground_state_reused_new_sector_spectrum';extra['historical_source']='results/baseline/grid_n8.npz'
 o=observations(state,n);_,z,_=geometry(n);m=z.mean(1);prob=abs(state)**2;m2=float(prob@m**2);m4=float(prob@m**4);binder=1-m4/(3*m2*m2) if m2>1e-20 else None
 base.parent.mkdir(exist_ok=True);archive=base.with_suffix('.npz');np.savez_compressed(archive,state=state,energy=e,**o)
 r=dict(key=key,n=n,kappa=k,h=h,energy=e,energy_per_site=e/n,**o,binder=binder,m4=m4,**extra,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),seconds=time.perf_counter()-t,disposition=source);dump(p,r);return r
def ising_reference(k):
 k=np.asarray(k,dtype=float)
 # Rationalized original expression; k=0 limit exactly1.
 return np.where(k<.5,(2-4*k)/(1+np.sqrt((1-3*k+4*k*k)/(1-k))),np.nan)
