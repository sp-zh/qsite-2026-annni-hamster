"""New OBC slice; full states/checkpoints, fixed-midpoint pairs and literal Pauli H."""
import sys,time,pickle,argparse,logging,subprocess,resource
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
def run(n,k,h,chi,initial='plus',sweeps=32,resume=None,max_seconds=600):
 guard();key=dict(n=n,kappa=float(k),h=float(h),chi=chi,initial=initial,sweeps=sweeps,resume=resume,resume_sha=sha(ROOT/resume) if resume else None,max_seconds=max_seconds,code=sha(__file__),tenpy=tenpy.__version__,bc='OBC');base=OUT/'floating_boundary_scan/cache'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  row=json.loads(meta.read_text());assert sha(ROOT/row['archive'])==row['sha256'];return row
 t=time.perf_counter();model=ANNNI(dict(L=n,lattice='Chain',bc_MPS='finite',bc_x='open',kappa=k,h=h))
 product=[np.array([1,1])/np.sqrt(2)]*n if initial=='plus' else ['up' if i%4<2 else 'down' for i in range(n)]
 psi=pickle.load((ROOT/resume).open('rb')) if resume else MPS.from_product_state(model.lat.mps_sites(),product,bc='finite');assert psi.L==n
 opts=dict(mixer=True,max_hours=max_seconds/3600,max_sweeps=sweeps,min_sweeps=4,max_E_err=1e-9,max_S_err=1e-6,trunc_params=dict(chi_max=chi,svd_min=1e-11),lanczos_params=dict(P_tol=1e-12))
 engine=dmrg.TwoSiteDMRGEngine(psi,model,opts);base.parent.mkdir(exist_ok=True)
 def checkpoint(algorithm):
  stats=algorithm.sweep_stats;dump(base.with_suffix('.progress.json'),dict(pid=__import__('os').getpid(),sweeps=algorithm.sweeps,seconds=time.perf_counter()-t,last_delta_E=stats.get('Delta_E',[])[-1:] if stats else [],last_delta_S=stats.get('Delta_S',[])[-1:] if stats else [],key=key))
  if algorithm.sweeps%4==0:
   with base.with_suffix('.partial.pkl').open('wb') as f:pickle.dump(algorithm.psi,f)
 engine.checkpoint.connect(checkpoint);energy,psi=engine.run();zz=psi.correlation_function('Sigmaz','Sigmaz',hermitian=True).real;z=psi.expectation_value('Sigmaz');x=psi.expectation_value('Sigmax');connected=zz-z[:,None]*z[None,:];entropy=psi.entanglement_entropy()
 sets=[pairs(n,r) for r in range(n//3+1)];raw=np.array([np.mean([zz[i,j] for i,j in s]) for s in sets]);conn=np.array([np.mean([connected[i,j] for i,j in s]) for s in sets]);old=np.array([np.mean(zz[np.arange(n//4,min(3*n//4,n-r)),np.arange(n//4,min(3*n//4,n-r))+r]) for r in range(n//2)])
 stats={k:np.asarray(v).tolist() for k,v in engine.sweep_stats.items()};de=abs(stats['Delta_E'][-1]/max(stats['E'][-1],1.0));ds=abs(stats['Delta_S'][-1])
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,zz=zz,z=z,x=x,connected_zz=connected,entropy=entropy,central_raw=raw,central_connected=conn,legacy_raw=old)
 with base.with_suffix('.pkl').open('wb') as f:pickle.dump(psi,f)
 row=dict(key=key,n=n,kappa=k,h=h,chi=chi,initial=initial,energy=float(energy),energy_per_site=float(energy/n),options=opts,actual_chi=max(psi.chi),sweeps=stats,solver_stopping_pass=bool(de<1e-9 and ds<1e-6),last_relative_energy_change=de,last_entropy_change=ds,pairs=sets,pair_counts=list(map(len,sets)),mx=float(x[n//4:3*n//4].mean()),tail_rms=float(np.sqrt(np.mean(raw[-5:]**2))),central_entropy=float(entropy[n//2-1]),seconds=time.perf_counter()-t,archive=str(a.relative_to(ROOT)),sha256=sha(a),checkpoint=str(base.with_suffix('.pkl').relative_to(ROOT)),checkpoint_sha=sha(base.with_suffix('.pkl')),disposition='newly_executed',process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,initial_source=resume or 'independent_product_state',time_shelved=bool(engine.shelve))
 dump(meta,row);print(n,k,h,chi,initial,'seconds',round(row['seconds'],2),'stopping',row['solver_stopping_pass'],flush=True);return row

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--jobfile');args=parser.parse_args()
 if args.jobfile:
  job=json.loads(Path(args.jobfile).read_text());row=run(**job['arguments']);dump(Path(job['output']),row)
 else:
  O=OUT/'floating_boundary_scan';existing=json.loads((O/'refined_index.json').read_text());rows=existing.copy();jobs=json.loads((O/'refined_jobs.json').read_text());priority={.7:0,.4:1,.5:2,.55:3,.6:4,.525:5,.35:6,.3:7,.325:8};jobs.sort(key=lambda j:(priority.get(j['h'],9),j['n'],j['chi'],j.get('initial','plus')));failures=[]
  for job in jobs:
   if any(r['n']==job['n'] and r['h']==job['h'] and r['chi']==job['chi'] and r['initial']==job.get('initial','plus') for r in existing):continue
   guard();argsjob=dict(job)
   if job['chi']==256 and job.get('initial','plus')=='plus':
    lower=[r for r in rows if r['n']==job['n'] and r['h']==job['h'] and r['chi']==128 and r['initial']=='plus']
    if lower:argsjob['resume']=lower[-1]['checkpoint']
   path=O/'bounded_jobs'/uid(argsjob);path.parent.mkdir(exist_ok=True);output=path.with_suffix('.result.json');jobfile=path.with_suffix('.job.json');dump(jobfile,dict(arguments=argsjob,output=str(output)))
   if output.exists():r=json.loads(output.read_text())
   else:
    progress('mps_bounded',len(rows),'.venv-tn/bin/python scripts/run_stage6_mps_bounded.py',running_job=argsjob)
    try:
     with path.with_suffix('.log').open('a') as f:result=subprocess.run([sys.executable,__file__,'--jobfile',str(jobfile)],stdout=f,stderr=subprocess.STDOUT,timeout=780)
     if result.returncode!=0:raise RuntimeError(('Worker exit',result.returncode))
     r=json.loads(output.read_text())
    except (subprocess.TimeoutExpired,RuntimeError) as e:
     failures.append(dict(job=argsjob,error=str(e),disposition='executed_incomplete',log=str(path.with_suffix('.log').relative_to(ROOT))));dump(O/'bounded_failures.json',failures);continue
   rows.append(r);dump(O/'bounded_index.json',rows);print('bounded done',len(rows),r['n'],r['h'],r['chi'],r['solver_stopping_pass'],flush=True)
  dump(O/'bounded_index.json',rows);dump(O/'bounded_failures.json',failures)
