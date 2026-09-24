"""Read archived whole-bitstring experiments; no resampling per detector."""
from .stage6_common import *
from .upgrade_gates import vector,observations,evolve
from .upgrade_mitigation import LINEAR,RICHARDSON,estimated_vector,measurement_probs
from .upgrade_detection import predict as old_predict
from .stage6_detector import predict as new_predict
from .stage6_wall_features import features,predict as wall_predict
from .stage6_reference import record
from .stage6_diagnostics import physical_reference
from functools import lru_cache
@lru_cache(2)
def configs(n):
 f=json.loads((OUT/'confirmation/method_frozen.json').read_text());old=json.loads((ROOT/('results/stage4_upgrade_v1/detection/frozen.json' if n==8 else 'results/stage5_v1/n12_scaling/detection_frozen.json')).read_text());return old[str(n)] if str(n) in old else old,f['detectors'][str(n)],f['wall_detectors'][str(n)]
def predict(v,n,wall=None):
 old,new,w= configs(n)
 if not np.isfinite(v).all():return dict(D1='uncertain',D3='uncertain',D4='uncertain',D5='unmeasured' if wall is None else 'uncertain')
 x=old_predict(v,old);return dict(D1=x['D1'],D3=x['D3'],D4=new_predict(v,new)['label'],D5='unmeasured' if wall is None else wall_predict(wall,w)['label'])
def wall_estimates(measurement,budget=None):
 if measurement['method']=='sv':return None
 n=measurement['n'];records=measurement['probability_records'];coeff=LINEAR if measurement['method']=='zne' else RICHARDSON if measurement['method']=='zne_quadratic' else np.array([1.]);values=[]
 if budget is None:
  for r in records:
   a=np.load(ROOT/r['archive']);ds={b:a[f'p{i}'] for i,b in enumerate(r['bases'])};v=estimated_vector(ds,n,False)[0];values.append(features(ds['Z'*n],v[-1],n))
  return coeff@np.array(values)
 a=np.load(ROOT/measurement.get('counts_archive',measurement['archive']));counts=a[f'counts_{budget}'];out=[]
 for rep in range(len(counts)):
  offset=0;vs=[]
  for setting in measurement['sampling'][str(budget)]:
   bs=setting['bases'];alloc=setting['allocations'];ds={b:counts[rep,offset+i]/amount for i,(b,amount) in enumerate(zip(bs,alloc))};offset+=len(bs);v=estimated_vector(ds,n,False)[0];vs.append(features(ds['Z'*n],v[-1],n))
  out.append(coeff@np.array(vs))
 return np.array(out)
def ed_measurements(n,k,h):
 r=record(n,k,h);state=np.load(ROOT/r['archive'])['state'];v=vector(observations(state,n));key=dict(reference=r['sha256'],n=n,kappa=k,h=h,budgets=PLAN['measurement']['budgets'],repeats=32,seed=9719,code=sha(__file__));base=OUT/'noise_diagnosability/ed_measurements'/uid(key);p=base.with_suffix('.json')
 if p.exists():return json.loads(p.read_text())
 # Classical ideal-information reference, no physical StatePrep and no invented CNOT cost.
 ds={'Z'*n:abs(state)**2,'X'*n:abs(evolve([('H',i) for i in range(n)],n,rho=state))**2};ds={b:p/p.sum() for b,p in ds.items()};data={};cost={}
 for budget in key['budgets']:
  rng=np.random.default_rng(np.random.SeedSequence([9719,budget,*np.frombuffer(bytes.fromhex(uid(key)),dtype='<u4').tolist()]));alloc=[budget//2,budget-budget//2];counts=np.array([[rng.multinomial(a,ds[b]) for b,a in zip(ds,alloc)] for _ in range(32)]);samples=[];wall=[]
  for cc in counts:
   d={b:c/a for b,c,a in zip(ds,cc,alloc)};vv=estimated_vector(d,n,False)[0];samples.append(vv);wall.append(features(d['Z'*n],vv[-1],n))
  data.update({f'counts_{budget}':counts,f'samples_{budget}':samples,f'wall_{budget}':wall,f'covariance_{budget}':np.cov(samples,rowvar=False)});cost[str(budget)]=dict(shots_per_repeat=budget,repeats=32,physical_preparation_cost=None,scope='ED classical ideal-information reference')
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,exact=v,wall_exact=features(ds['Z'*n],v[-1],n),**data);out=dict(key=key,archive=str(a.relative_to(ROOT)),sha256=sha(a),cost=cost,reference=r['archive'],disposition='newly_executed_ideal_information_sampling');dump(p,out);return out
def scores(v,target,n):
 e=np.asarray(v)-np.asarray(target)
 return dict(mse=float(np.mean(e**2)),max_c=float(np.max(abs(e[:n]))),max_sf=float(np.max(abs(e[n:2*n]))),mx_error=float(abs(e[-1])))
def label_status(label,reference):
 if reference is None:return 'reference_unlabelled'
 if label in ['unmeasured']:return 'unmeasured'
 if label in ['uncertain','degraded']:return 'rejected'
 return 'correct' if label==reference else 'wrong_accepted'
