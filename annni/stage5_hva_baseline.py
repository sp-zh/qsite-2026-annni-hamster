"""Coordinate-keyed auxiliary HVA baseline; legacy decimal-suffix cache is never reused."""
import json,hashlib
import numpy as np
from .stage5_adapt import ROOT,OUT,PLAN,sha,dump,assess,guard
from .stage5_e2e import hva_gates
from .upgrade_gates import evolve,vector,observations
from .vqe import optimize
OPTIONS=dict(maxiter=400,ftol=1e-12,gtol=1e-7,maxls=30)
def key_for(k,h):
 return dict(n=8,kappa=float(k),h=float(h),layers=6,seeds=[11,23,37],optimizer=OPTIONS,versions=PLAN['versions'],code={name:sha(ROOT/name) for name in ['annni/stage5_hva_baseline.py','annni/vqe.py','annni/circuits.py','annni/model.py']})
def baseline_arm(k,h):
 guard();old=json.loads((ROOT/'results/stage3_v1/grid/selection_frozen.json').read_text())['rows'];matches=[r for r in old if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12]
 if matches:
  r=matches[0];a=np.load(ROOT/r['archive']);theta=a['final_params'];state=a['state'];source=dict(disposition='historical_reused',archive=r['archive'])
 else:
  key=key_for(k,h);uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();base=OUT/'end_to_end/hva_v2'/uid;archive=base.with_suffix('.npz');meta=base.with_suffix('.json');base.parent.mkdir(exist_ok=True)
  if meta.exists():
   r=json.loads(meta.read_text());assert r['key']==key and sha(archive)==r['sha256'];a=np.load(archive);theta=a['theta'];state=a['state']
  else:
   trials=[]
   for seed in key['seeds']:
    initial=np.random.default_rng(np.random.SeedSequence([seed,round(k*1e6),round(h*1e6)])).uniform(-.2,.2,(6,3));fit,t,s,trace=optimize(initial,k,h,OPTIONS,8);trials.append((fit,t,s,trace,initial))
   best=min(trials,key=lambda x:x[0]['energy']);fit,theta,state,trace,initial=best
   np.savez_compressed(archive,theta=theta,state=state,initials=[x[4] for x in trials],finals=[x[1] for x in trials])
   r=dict(key=key,kappa=float(k),h=float(h),n=8,trials=[x[0] for x in trials],traces=[x[3].tolist() for x in trials],selection='lowest energy',seeds=key['seeds'],disposition='newly_executed_corrected_coordinate_cache',archive=str(archive.relative_to(ROOT)),sha256=sha(archive));dump(meta,r)
  source=dict(disposition='newly_executed',archive=str(archive.relative_to(ROOT)),metadata=str(meta.relative_to(ROOT)))
 g=hva_gates(theta,8);np.testing.assert_allclose(evolve(g,8),state,atol=1e-10);met,obs,ed=assess(state,8,k,h)
 return dict(n=8,kappa=k,h=h,state=state,ed_vector=vector(observations(ed,8)),gates=g,joint_pass=met['joint_pass'],source=source)
