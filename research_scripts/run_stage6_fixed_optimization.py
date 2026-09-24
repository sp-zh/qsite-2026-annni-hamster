"""B-opt energy restarts and separately isolated B-expressivity oracle fitting."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_candidates import *
from annni.stage6_assess import assess
from annni.stage6_reference import record
parser=argparse.ArgumentParser();parser.add_argument('--oracle',action='store_true');args=parser.parse_args()
points=json.loads((OUT/'domain_wall_candidates/development_101_0_index.json').read_text());assert len(points)==36
if args.oracle:points=points[:12]
rows=[];name='oracle_expressivity' if args.oracle else 'fixed_energy_restarts'
for point in points:
 for method in ['B3','C3']:
  r=point['methods']['C3']['selected'] if method=='C3' else next(x['selected'] for x in json.loads((OUT/'legacy_b3/development_index.json').read_text()) if x['kappa']==point['kappa'] and x['h']==point['h']);r=dict(r,basis=r.get('basis','physical'));c=r['selected'];words=c['words'];n=r['n'];k=r['kappa'];h=r['h'];basis=r['basis'];ref=r['ref'];target=np.load(ROOT/record(n,k,h)['archive'])['state'] if args.oracle else None
  for seed in ([977] if args.oracle else [877,991,1117]):
   key=dict(source=r['sha256'],code=sha(__file__),seed=seed,oracle=args.oracle,maxiter=2000);p=OUT/'failure_mechanisms'/name/(uid(key)+'.json')
   if p.exists():rows.append(json.loads(p.read_text()));continue
   guard();rng=np.random.default_rng(seed);initial=np.array(c['params'])+rng.normal(0,.15,len(words)) if args.oracle else rng.normal(0,.35,len(words));t=time.perf_counter()
   if not words:
    state=evaluate([],[],n,basis,ref,k,h)[2];result=dict(key=key,n=n,kappa=k,h=h,method=method,seed=seed,source_candidate=r['archive'],objective='oracle_ED_fidelity_OFFLINE_ONLY' if args.oracle else 'energy_only',nfev=0,nit=0,seconds=0.,optimizer_success=None,disposition='no_parameters_not_optimized',independent_initialization=False,confirmation_eligible=False,**assess(state,n,k,h));dump(p,result);rows.append(result);dump(OUT/f'failure_mechanisms/{name}_index.json',rows);continue
   if args.oracle:
    fit=minimize(lambda x:evaluate(x,words,n,basis,ref,k,h,target=target)[:2],initial,jac=True,method='L-BFGS-B',options=dict(maxiter=2000,ftol=1e-13,gtol=1e-8,maxls=30));log=dict(initial=initial.tolist(),final=fit.x.tolist(),nit=int(fit.nit),nfev=int(fit.nfev),success=bool(fit.success),reason=str(fit.message),seconds=time.perf_counter()-t)
   else:fit,log=optimize(n,k,h,basis,ref,words,initial,2000)
   log['optimized_objective']=log.pop('energy',float(fit.fun));state=evaluate(fit.x,words,n,basis,ref,k,h)[2];metric=assess(state,n,k,h);g=gate_table(n,basis,ref,words,fit.x);a=p.with_suffix('.npz');p.parent.mkdir(exist_ok=True);np.savez_compressed(a,state=state,params=fit.x,initial=initial)
   result=dict(key=key,n=n,kappa=k,h=h,method=method,seed=seed,objective='oracle_ED_fidelity_OFFLINE_ONLY' if args.oracle else 'energy_only',basis=basis,ref=ref,words=words,**log,**metric,gates=g,cnots=resources(g,n)['cnots'],archive=str(a.relative_to(ROOT)),sha256=sha(a),confirmation_eligible=False,source_candidate=r['archive']);dump(p,result);rows.append(result);dump(OUT/f'failure_mechanisms/{name}_index.json',rows)
   print(name,k,h,method,seed,metric['joint_pass'],round(result['seconds'],2),flush=True)
