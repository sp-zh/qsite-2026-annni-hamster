"""One declared energy-only warm continuation per fixed development structure.
Distinct from the three independent random restarts and isolated ED-fidelity oracle.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_candidates import evaluate,start_gates,gate_table
from annni.upgrade_gates import evolve
from annni.stage6_assess import assess
from scipy.optimize import minimize
points=json.loads((OUT/'domain_wall_candidates/development_101_0_index.json').read_text());old=json.loads((OUT/'legacy_b3/development_index.json').read_text());rows=[]
options=dict(maxiter=2000,ftol=1e-14,gtol=1e-9,maxls=30)
for point in points:
 for method in ['B3','C3']:
  r=point['methods']['C3']['selected'] if method=='C3' else next(x['selected'] for x in old if (x['kappa'],x['h'])==(point['kappa'],point['h']));c=r['selected'];n=r['n'];k=r['kappa'];h=r['h'];basis=r.get('basis','physical');ref=r['ref'];words=c['words'];initial=np.array(c['params']);key=dict(source_sha=r['sha256'],options=options,code=sha(__file__),backend=sha(ROOT/'annni/stage6_candidates.py'));base=OUT/'failure_mechanisms/energy_continuation'/uid(key);meta=base.with_suffix('.json')
  if meta.exists():rows.append(json.loads(meta.read_text()));continue
  guard();t=time.perf_counter();s0=evolve(start_gates(n,basis,ref),n)
  if len(words):fit=minimize(lambda p:evaluate(p,words,n,basis,ref,k,h,initial_state=s0)[:2],initial,jac=True,method='L-BFGS-B',options=options);final=fit.x;status=dict(optimizer_success=bool(fit.success),nit=int(fit.nit),nfev=int(fit.nfev),reason=str(fit.message))
  else:final=initial;status=dict(optimizer_success=None,nit=0,nfev=0,reason='no_parameters_not_optimized')
  state=evaluate(final,words,n,basis,ref,k,h,initial_state=s0)[2];base.parent.mkdir(exist_ok=True);archive=base.with_suffix('.npz');np.savez_compressed(archive,state=state,initial=initial,params=final);out=dict(key=key,n=n,kappa=k,h=h,method=method,basis=basis,ref=ref,words=words,gates=gate_table(n,basis,ref,words,final),cnots=c['cnots'],source=r['archive'],archive=str(archive.relative_to(ROOT)),sha256=sha(archive),**status,**assess(state,n,k,h),seconds=time.perf_counter()-t,initialization='Same actual saved parameters, one energy-only continuation; not an independent seed',confirmation_eligible=False);dump(meta,out);rows.append(out);dump(OUT/'failure_mechanisms/energy_continuation_index.json',rows);print(method,k,h,out['joint_pass'],flush=True)
