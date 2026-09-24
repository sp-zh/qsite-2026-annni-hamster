"""Isolated TeNPy 1.1.1 OBC experiments. Never load arbitrary MPS into circuits."""
import sys,json,time,pickle,hashlib,logging,argparse
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigsh
from scipy.optimize import least_squares
import tenpy
from tenpy.models.model import CouplingMPOModel
from tenpy.networks.site import SpinHalfSite
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
from tenpy.algorithms.exact_diag import ExactDiag
logging.basicConfig(level=logging.ERROR)
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1/floating_validation';O.mkdir(exist_ok=True);PLAN=json.loads((O.parent/'experiment_plan.json').read_text())
def dump(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,default=lambda a:a.item() if isinstance(a,np.generic) else str(a)));t.replace(p)
class ANNNI(CouplingMPOModel):
 def init_sites(self,p):return SpinHalfSite(conserve=None,sort_charge=False)
 def init_terms(self,p):
  k=p.get('kappa',.8);h=p.get('h',.5);n=self.lat.N_sites
  # Sigmax/y/z are Pauli matrices, unlike Sx/Sz. No Sz U(1).
  for i in range(n):self.add_onsite_term(-h,i,'Sigmax')
  for d,c in [(1,-1),(2,k)]:
   for i in range(n-d):self.add_coupling_term(c,i,i+d,'Sigmaz','Sigmaz')
def model(n,k,h):return ANNNI(dict(L=n,lattice='Chain',bc_MPS='finite',bc_x='open',kappa=k,h=h))
def ed_matrix(n,k,h,periodic=False):
 ids=np.arange(1<<n);z=1-2*((ids[:,None]>>np.arange(n-1,-1,-1))&1)
 diagonal=sum(c*z[:,i]*z[:,(i+d)%n] for d,c in [(1,-1),(2,k)] for i in range(n if periodic else n-d))
 rows=np.tile(ids,n);cols=np.concatenate([ids^(1<<i) for i in range(n)])
 return diags(diagonal)+coo_matrix((np.full(len(rows),-h),(rows,cols)),shape=(len(ids),len(ids))).tocsr()
def fits(c,entropy,n):
 out=[]
 for lo,hi in [(2,n//3),(4,n//2-2)]:
  r=np.arange(lo,hi+1)
  if len(r)<6:continue
  y=c[r]
  for kind in ['power','exponential']:
   def pred(a):return a[0]*np.cos(a[1]*r+a[2])*(r**(-a[3]) if kind=='power' else np.exp(-r/a[3]))
   sols=[]
   for q in np.linspace(.6,1.8,7):
    fit=least_squares(lambda a:pred(a)-y,[.5,q,0,1 if kind=='power' else 10],bounds=([-2,0,-np.pi,.001],[2,np.pi,np.pi,5 if kind=='power' else 10*n]),max_nfev=1000)
    sols.append(fit)
   best=min(sols,key=lambda a:sum(a.fun**2));rss=float(sum(best.fun**2));out.append(dict(kind=kind,window=[lo,hi],params=best.x.tolist(),q=float(best.x[1]),rss=rss,aic=float(len(r)*np.log(max(rss/len(r),1e-30))+8)))
 ent=[]
 for frac in [.15,.25]:
  l=np.arange(1,n);mask=(l>=n*frac)&(l<=n*(1-frac));x=np.log(2*n/np.pi*np.sin(np.pi*l[mask]/n));a=np.polyfit(x,entropy[mask],1)
  ent.append(dict(edge_fraction=frac,c=float(6*a[0]),intercept=float(a[1]),rms=float(np.sqrt(np.mean((np.polyval(a,x)-entropy[mask])**2)))))
 return out,ent

def run(n,k,h,chi,init='plus',max_sweeps=24):
 if datetime.now(timezone.utc)>=datetime.fromisoformat(PLAN['deadline']):raise TimeoutError('budget')
 key=f'n{n}_k{k:.3f}_h{h:.3f}_chi{chi}_{init}';path=O/(key+'.json')
 sourcehash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 if path.exists():
  a=json.loads(path.read_text());assert a['source_sha256']==sourcehash;return a
 t=time.perf_counter();m=model(n,k,h)
 prod=[np.array([1,1])/np.sqrt(2)]*n if init=='plus' else ['up' if i%4<2 else 'down' for i in range(n)]
 psi=MPS.from_product_state(m.lat.mps_sites(),prod,bc='finite')
 opts=dict(mixer=True,max_sweeps=max_sweeps,min_sweeps=4,max_E_err=1e-9,max_S_err=1e-6,trunc_params=dict(chi_max=chi,svd_min=1e-11),lanczos_params=dict(P_tol=1e-12))
 engine=dmrg.TwoSiteDMRGEngine(psi,m,opts);energy,psi=engine.run()
 zz=np.real(psi.correlation_function('Sigmaz','Sigmaz',hermitian=True));z=psi.expectation_value('Sigmaz');x=psi.expectation_value('Sigmax');conn=zz-z[:,None]*z[None,:];ent=psi.entanglement_entropy();raw=[];connected=[]
 for r in range(n//2):
  sites=np.arange(n//4,min(3*n//4,n-r));raw.append(float(np.mean(zz[sites,sites+r])));connected.append(float(np.mean(conn[sites,sites+r])))
 raw=np.array(raw);connected=np.array(connected);fit,ef=fits(raw,ent,n);fitc,_=fits(connected,ent,n)
 np.savez_compressed(O/(key+'.npz'),zz=zz,connected_zz=conn,z=z,x=x,entropy=ent,central_raw=raw,central_connected=connected)
 with open(O/(key+'.pkl'),'wb') as f:pickle.dump(psi,f)
 stats={k:np.asarray(v).tolist() for k,v in engine.sweep_stats.items()};trunc=stats.get('max_trunc_err',[])
 row=dict(n=n,kappa=k,h=h,chi_max=chi,actual_chi=max(psi.chi),init=init,energy=float(energy),seconds=time.perf_counter()-t,bc='OBC',pauli_normalization=True,conserve=None,tenpy=tenpy.__version__,source_sha256=sourcehash,options=opts,sweeps=stats,max_discarded_weight=max(trunc) if trunc else None,fit_raw=fit,fit_connected=fitc,entropy_fits=ef,archive=str((O/(key+'.npz')).relative_to(R)),checkpoint=str((O/(key+'.pkl')).relative_to(R)),disposition='newly_executed',evidence_grade='not_resolved')
 dump(path,row);print(key,round(row['seconds'],2),energy,flush=True);return row

def verify():
 rows=[]
 for n in [8,12]:
  m=model(n,.8,.5);ex=ExactDiag(m,max_size=20000000);ex.build_full_H_from_mpo();a=ex.full_H.to_ndarray();expected=ed_matrix(n,.8,.5).toarray();err=float(np.max(abs(a-expected)));assert err<1e-12
  del a,expected,ex
  row=run(n,.8,.5,64,max_sweeps=24);e,s=eigsh(ed_matrix(n,.8,.5),k=1,which='SA',tol=1e-12);ep,sp=eigsh(ed_matrix(n,.8,.5,True),k=1,which='SA',tol=1e-12)
  assert abs(row['energy']-e[0])<1e-7
  rows.append(dict(n=n,matrix_max_error=err,dmrg_energy_error=row['energy']-float(e[0]),obc_energy=float(e[0]),pbc_energy=float(ep[0])))
 dump(O/'verification.json',dict(passed=True,rows=rows))

if __name__=='__main__':
 cfg=PLAN['floating_validation'];rows=[]
 for k,h in cfg['centers']:
  for chi in cfg['chi']:
   for init in cfg['initial']:
    rows.append(run(128,k,h,chi,init));dump(O/'index.json',rows)
  for offset in [-cfg['offset'],cfg['offset']]:
   for n in cfg['neighbors_n']:
    for chi in cfg['neighbor_chi']:
     rows.append(run(n,k,round(h+offset,3),chi));dump(O/'index.json',rows)
 for k,h in cfg['controls']:
  rows.append(run(cfg['control_n'],k,h,128));dump(O/'index.json',rows)
