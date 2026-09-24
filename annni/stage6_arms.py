"""Materialize actual saved gates/states. Historical coordinates use exact matching."""
from .stage6_common import *
from .stage6_io import candidate_paths
from .upgrade_gates import *
from .vqe import optimize
from functools import lru_cache
@lru_cache(8)
def _json(path,mtime):return json.loads(Path(path).read_text())
def read(path):return _json(str(path),path.stat().st_mtime_ns)
def arm(record):
 a=np.load(ROOT/record['archive']);c=record['selected'];g=record.get('gates') or compile_circuit(record['n'],record['ref'],c['words'],c['params']);s=a['state'];np.testing.assert_allclose(evolve(g,record['n']),s,atol=1e-10)
 return dict(n=record['n'],kappa=record['kappa'],h=record['h'],gates=g,state=s,source_archive=record['archive'],source_sha=record['sha256'])
def coordinate_match(rows,k,h):return next((r for r in rows if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12),None)
def frozen_hybrid_reuse(k,h,n,task):
 # Development/validation ran all four pure ablations before H6 was frozen.
 # Materialize its declared union from those exact candidate records without ED or reoptimization.
 from .stage6_candidates import select
 from .stage6_hybrid import components
 frozen=read(OUT/'confirmation/method_frozen.json')
 source=next((r for path in candidate_paths(task) for r in read(path) if r['n']==n and (r['kappa'],r['h'])==(k,h)),None)
 if source is None:raise FileNotFoundError(('Missing frozen H6 component source',task,n,k,h))
 names=components('H6',k,h,frozen['wall_component']);runs=[read(ROOT/path) for name in names for path in source['methods'][name]['runs']];chosen=select(runs)
 key=dict(task=task,n=n,kappa=k,h=h,materialization_code=sha(__file__),freeze_sha=sha(OUT/'confirmation/method_frozen.json'),sources=[r['sha256'] for r in runs])
 out=OUT/'domain_wall_candidates/frozen_h6_reuse'/f'{uid(key)}.json'
 if not out.exists():dump(out,dict(key=key,selected_source=chosen['archive'],components=names,selection='Frozen energy/resource rule, no ED',disposition='historical_within_run_candidates_reused_new_frozen_selection'))
 return arm(chosen)
def load(k,h,method,n=8,task=None):
 if method=='H6' and task in ['development','validation']:return frozen_hybrid_reuse(k,h,n,task)
 if method=='B3':
  for p in (OUT/'legacy_b3').glob((task+'_index.json') if task else '*index.json'):
   r=coordinate_match(read(p),k,h)
   if r and r['n']==n:return arm(r['selected'])
  # Stage5 corrected historical B3 source has literal old circuit; no selectors re-run.
  for p in (ROOT/'results/stage5_v1/selector_benchmark').glob('map/index.json' if task=='historical_map' else '*/index.json'):
   if p.parent.name=='audit':continue
   for r in read(p):
    if r.get('n')==n and abs(r.get('kappa',-10)-k)<1e-12 and abs(r.get('h',-10)-h)<1e-12 and 'B3' in r:return arm(r['B3'])
 elif method=='B5':
  for p in (ROOT/'results/stage5_v1/selector_benchmark').glob('map/index.json' if task=='historical_map' else '*/index.json'):
   if p.parent.name=='audit':continue
   for r in read(p):
    if r.get('n')==n and abs(r.get('kappa',-10)-k)<1e-12 and abs(r.get('h',-10)-h)<1e-12 and 'B5' in r:return arm(r['B5'])
 else:
  for p in (candidate_paths(task) if task else (OUT/'domain_wall_candidates').glob('*index.json')):
   if p.name.startswith(('pilot','stability')):continue
   for r in read(p):
    if r.get('n')==n and abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12 and method in r.get('methods',{}):return arm(r['methods'][method]['selected'])
 raise FileNotFoundError(('No actual circuit record',n,k,h,method))
def hva_gates(theta):
 n=8;g=[('H',i) for i in range(n)]
 for a,b,c in theta:
  for d,t in [(1,a),(2,b)]:
   for i in range(n):j=(i+d)%n;g += [('CNOT',i,j),('RZ',j,2*float(t)),('CNOT',i,j)]
  g += [('RX',i,2*float(c)) for i in range(n)]
 return g
def hva(k,h):
 for r in json.loads((ROOT/'results/stage3_v1/grid/selection_frozen.json').read_text())['rows']:
  if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12:
   a=np.load(ROOT/r['archive']);return dict(n=8,kappa=k,h=h,state=a['state'],gates=hva_gates(a['final_params']),source_archive=r['archive'],disposition='historical_reused')
 for p in (ROOT/'results/stage5_v1/end_to_end/hva_v2').glob('*.json'):
  r=read(p)
  if r['key']['kappa']==k and r['key']['h']==h:
   a=np.load(ROOT/r['archive']);return dict(n=8,kappa=k,h=h,state=a['state'],gates=hva_gates(a['theta']),source_archive=r['archive'],disposition='historical_reused_corrected_full_coordinate_cache')
 options=dict(maxiter=400,ftol=1e-12,gtol=1e-7,maxls=30);key=dict(n=8,kappa=float(k),h=float(h),layers=6,seeds=[11,23,37],options=options,code=sha(__file__),engine=sha(ROOT/'annni/circuits.py'),optimizer=sha(ROOT/'annni/vqe.py'));base=OUT/'end_to_end/hva'/uid(key);p=base.with_suffix('.json')
 if p.exists():r=read(p);assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);theta=a['theta'];state=a['state']
 else:
  trials=[]
  for seed in key['seeds']:
   guard();initial=np.random.default_rng(np.random.SeedSequence([seed,*np.frombuffer(bytes.fromhex(uid(key)),dtype='<u4').tolist()])).uniform(-.2,.2,(6,3));fit,theta,state,trace=optimize(initial,k,h,options,8);trials.append((fit,theta,state,trace,initial))
  best=min(trials,key=lambda t:t[0]['energy']);_,theta,state,_,_=best;base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,theta=theta,state=state,initials=[x[4] for x in trials],finals=[x[1] for x in trials]);r=dict(key=key,archive=str(a.relative_to(ROOT)),sha256=sha(a),trials=[x[0] for x in trials],traces=[x[3].tolist() for x in trials],selection='lowest energy only',disposition='newly_executed');dump(p,r)
 return dict(n=8,kappa=k,h=h,state=state,gates=hva_gates(theta),source_archive=r['archive'],disposition=r['disposition'])
