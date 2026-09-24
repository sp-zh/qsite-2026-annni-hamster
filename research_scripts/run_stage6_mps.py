"""New OBC slice; full states/checkpoints, fixed-midpoint pairs and literal Pauli H."""
import sys,time,pickle,argparse,logging
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import tenpy
from tenpy.models.model import CouplingMPOModel
from tenpy.networks.site import SpinHalfSite
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
logging.basicConfig(level=logging.ERROR)
class ANNNI(CouplingMPOModel):
 def init_sites(self,p):return SpinHalfSite(conserve=None,sort_charge=False)
 def init_terms(self,p):
  n=self.lat.N_sites;k=p.get('kappa',.8);h=p.get('h',.5)
  for i in range(n):self.add_onsite_term(-h,i,'Sigmax')
  for d,c in [(1,-1),(2,k)]:
   for i in range(n-d):self.add_coupling_term(c,i,i+d,'Sigmaz','Sigmaz')
def pairs(n,r):
 return [(i,i+r) for i in range(n) if n//4<=i and i+r<3*n//4 and abs((2*i+r)-(n-1))<=4]
def run(n,k,h,chi,initial='plus',sweeps=32):
 guard();key=dict(n=n,kappa=float(k),h=float(h),chi=chi,initial=initial,sweeps=sweeps,code=sha(__file__),tenpy=tenpy.__version__,bc='OBC');base=OUT/'floating_boundary_scan/cache'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  row=json.loads(meta.read_text());assert sha(ROOT/row['archive'])==row['sha256'];return row
 t=time.perf_counter();model=ANNNI(dict(L=n,lattice='Chain',bc_MPS='finite',bc_x='open',kappa=k,h=h))
 product=[np.array([1,1])/np.sqrt(2)]*n if initial=='plus' else ['up' if i%4<2 else 'down' for i in range(n)]
 psi=MPS.from_product_state(model.lat.mps_sites(),product,bc='finite');opts=dict(mixer=True,max_sweeps=sweeps,min_sweeps=4,max_E_err=1e-9,max_S_err=1e-6,trunc_params=dict(chi_max=chi,svd_min=1e-11),lanczos_params=dict(P_tol=1e-12))
 engine=dmrg.TwoSiteDMRGEngine(psi,model,opts);energy,psi=engine.run();zz=psi.correlation_function('Sigmaz','Sigmaz',hermitian=True).real;z=psi.expectation_value('Sigmaz');x=psi.expectation_value('Sigmax');connected=zz-z[:,None]*z[None,:];entropy=psi.entanglement_entropy()
 sets=[pairs(n,r) for r in range(n//3+1)];raw=np.array([np.mean([zz[i,j] for i,j in s]) for s in sets]);conn=np.array([np.mean([connected[i,j] for i,j in s]) for s in sets]);old=np.array([np.mean(zz[np.arange(n//4,min(3*n//4,n-r)),np.arange(n//4,min(3*n//4,n-r))+r]) for r in range(n//2)])
 stats={k:np.asarray(v).tolist() for k,v in engine.sweep_stats.items()};de=abs(stats['Delta_E'][-1]/max(stats['E'][-1],1.0));ds=abs(stats['Delta_S'][-1])
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,zz=zz,z=z,x=x,connected_zz=connected,entropy=entropy,central_raw=raw,central_connected=conn,legacy_raw=old)
 with base.with_suffix('.pkl').open('wb') as f:pickle.dump(psi,f)
 row=dict(key=key,n=n,kappa=k,h=h,chi=chi,initial=initial,energy=float(energy),energy_per_site=float(energy/n),options=opts,actual_chi=max(psi.chi),sweeps=stats,solver_stopping_pass=bool(de<1e-9 and ds<1e-6),last_relative_energy_change=de,last_entropy_change=ds,pairs=sets,pair_counts=list(map(len,sets)),mx=float(x[n//4:3*n//4].mean()),tail_rms=float(np.sqrt(np.mean(raw[-5:]**2))),central_entropy=float(entropy[n//2-1]),seconds=time.perf_counter()-t,archive=str(a.relative_to(ROOT)),sha256=sha(a),checkpoint=str(base.with_suffix('.pkl').relative_to(ROOT)),checkpoint_sha=sha(base.with_suffix('.pkl')),disposition='newly_executed')
 dump(meta,row);print(n,k,h,chi,initial,'seconds',round(row['seconds'],2),'stopping',row['solver_stopping_pass'],flush=True);return row
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--task',default='coarse');args=parser.parse_args();cfg=PLAN['mps'];rows=[]
 jobs=[dict(n=64,k=.8,h=h,chi=128) for h in cfg['coarse_h']] if args.task=='coarse' else json.loads((OUT/f'floating_boundary_scan/{args.task}_jobs.json').read_text())
 for job in jobs:
  rows.append(run(**job));dump(OUT/f'floating_boundary_scan/{args.task}_index.json',rows);progress('mps_'+args.task,len(rows),f'.venv-tn/bin/python scripts/run_stage6_mps.py --task {args.task}')
