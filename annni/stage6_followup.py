"""Isolated followup, immutable B3 gates and old estimators; exact integer costs."""
import json,hashlib,time,resource,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from .upgrade_gates import density,evolve,resources,observations,vector
from .upgrade_mitigation import estimated_vector,RICHARDSON,measurement_probs
from .stage5_measurement_groups import groups
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage6_followup_v1';OLD=ROOT/'results/stage6_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uid(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(x,indent=2,default=lambda a:a.tolist() if isinstance(a,np.ndarray) else a.item() if isinstance(a,np.generic) else str(a)));tmp.replace(p)
def cfg():return read(OUT/'config.json')
def guard():
 if datetime.now(timezone.utc)>=datetime.fromisoformat(cfg()['deadline']):raise TimeoutError('Followup deadline reached; checkpoints retained')
def alloc(total,groups):
 if total<groups:raise ValueError('budget_infeasible')
 return [total//groups+int(i<total%groups) for i in range(groups)]
def equal_gate_shots(target):
 # Existing 3-scale largest-remainder proportions. Maximal legal integer total.
 t=target//3
 def cost(t):return sum(f*n for f,n in zip([1,3,5],alloc(t,3)))
 while cost(t+1)<=target:t+=1
 while cost(t)>target:t-=1
 return t,cost(t)
def point(k,h):
 return next(x for x in read(OUT/'inputs.json').values() if x['kappa']==k and x['h']==h)
def data(row):return np.load(ROOT/row['archive'])
def folded(g,fold):return [x for gate in g for x in ([gate]*fold if gate[0]=='CNOT' else [gate])]
def physical(row,p,fold=1,sv=False):
 g=folded(row['gates'],fold);n=8
 key=dict(n=n,kappa=float(row['kappa']),h=float(row['h']),bc='PBC',gates=g,p=float(p),backend=sha(ROOT/'annni/upgrade_gates.py'),measurement_code=sha(ROOT/'annni/stage5_measurement_groups.py'),sv=sv,keep=False,shots=None)
 old=OLD/'end_to_end/probabilities'/f'{uid(key)}.json';base=OUT/'probabilities'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  r=read(meta);assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);return {b:a[f'p{i}'] for i,b in enumerate(r['bases'])},r
 guard();t=time.perf_counter();source=None
 if old.exists():
  oldr=read(old);assert oldr['key']==key;assert sha(ROOT/oldr['archive'])==oldr['sha256'];a=np.load(ROOT/oldr['archive']);dist={b:a[f'p{i}'] for i,b in enumerate(oldr['bases'])};v=a['observables'];extra={k:oldr[k] for k in ['trace_real','hermiticity','min_eigenvalue']};source=dict(metadata=str(old.relative_to(ROOT)),metadata_sha=sha(old),archive=oldr['archive'],sha256=oldr['sha256']);disposition='historical_reused'
 else:
  rho=density(g,n,p);trace=np.trace(rho);herr=float(np.max(abs(rho-rho.conj().T)));minimum=float(np.linalg.eigvalsh(rho).min());assert abs(trace-1)<1e-9 and herr<1e-10 and minimum>-1e-9
  if p==0:np.testing.assert_allclose(rho,np.outer(data(row)['state'],data(row)['state'].conj()),atol=1e-10)
  dist=groups(rho) if sv else {b:measurement_probs(rho,b) for b in ['Z'*n,'X'*n]};v=vector(observations(rho,n));extra=dict(trace_real=float(trace.real),hermiticity=herr,min_eigenvalue=minimum);disposition='newly_executed'
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,observables=v,**{f'p{i}':v for i,v in enumerate(dist.values())});res=resources(g,n)
 assert res['cnots']==fold*row['resources']['cnots']
 r=dict(key=key,bases=list(dist),archive=str(a.relative_to(ROOT)),sha256=sha(a),fold=fold,p=p,sv=sv,seconds=time.perf_counter()-t,disposition=disposition,source=source,noise_channels=res['cnots'],one_qubit_gates=len(g)-res['cnots'],process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**res,**extra);dump(meta,r);return dist,r

def historical_measurement(row,p,method,budget):
 for x in read(OUT/'historical_measurements.json'):
  if x['kappa']==row['kappa'] and x['h']==row['h'] and x['p']==p and x['estimator']==method:
   r=x['record'];assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);cc=np.load(ROOT/r.get('counts_archive',r['archive']))
   # Confirm the actual source gates, channel and budget fingerprint, not coordinate alone.
   compatible=all(prob['key']['gates']==[list(g) for g in folded(row['gates'],prob['fold'])] and prob['p']==p for prob in r['probability_records'])
   if not compatible:
    dump(OUT/'verification/rejected_coordinate_only_cache'/f"{uid(dict(point=row['id'],archive=r['archive']))}.json",dict(point_id=row['id'],source=r['archive'],reason='Same coordinate but different frozen literal gate table; cache rejected, never substituted',time=datetime.now(timezone.utc).isoformat()))
    continue
   return r,dict(samples=a[f'samples_{budget}'],counts=cc[f'counts_{budget}'],exact=a['exact'],own_clean=a['own_clean'])
 return None

def measure(row,p,method,mode,budget):
 guard();zero=row['resources']['cnots']==0
 if mode=='equal_gate' and not zero:
  zshots,equiv=equal_gate_shots(budget);total=zshots if method=='zne_quadratic' else equiv
 else:total=budget;equiv=None
 folds=[1,3,5] if method=='zne_quadratic' else [1];amounts=alloc(total,3) if len(folds)==3 else [total]
 probabilities=[physical(row,p,f,method=='sv') for f in folds];settings=[dict(fold=f,bases=list(d),allocations=alloc(amount,len(d))) for f,amount,(d,r) in zip(folds,amounts,probabilities)]
 cost=sum(sum(s['allocations'])*r['cnots'] for s,(d,r) in zip(settings,probabilities));c=row['resources']['cnots']
 if mode=='equal_gate' and not zero:assert cost==equiv*c and cost<=budget*c
 key=dict(n=8,kappa=row['kappa'],h=row['h'],bc='PBC',source_sha=row['sha256'],gate_hash=uid(row['gates']),parameters_hash=uid(row['selected_parameters']),p=p,method=method,mode=mode,budget=budget,settings=settings,probability_keys=[r['key'] for d,r in probabilities],repeats=32,seed=cfg()['seed'],code=sha(__file__),estimator=sha(ROOT/'annni/upgrade_mitigation.py'),numpy=np.__version__)
 base=OUT/'measurements'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  r=read(meta);assert r['key']==key and sha(ROOT/r['archive'])==r['sha256'];return r
 t=time.perf_counter();old=historical_measurement(row,p,method,budget) if mode=='equal_shots' else None
 coeff=RICHARDSON if method=='zne_quadratic' else np.array([1.]);exact=coeff@np.array([estimated_vector(d,8,method=='sv')[0] for d,r in probabilities]);denoms=[]
 if old:
  source,arrays=old;np.testing.assert_allclose(arrays['exact'],exact,atol=1e-10);samples=arrays['samples'];counts=arrays['counts'];disposition='historical_reused';source=dict(archive=source['archive'],sha256=source['sha256'],counts_archive=source.get('counts_archive',source['archive']),counts_sha=sha(ROOT/source.get('counts_archive',source['archive'])),key=source['key']);stream='Historical Stage6 shared streams, preserved counts; paired same-coordinate/repeat analysis'
 else:
  samples=[];counts=[]
  for rep in range(32):
   vs=[];cc=[];dd=[]
   for setting,(dist,r) in zip(settings,probabilities):
    ds={}
    for b,num in zip(setting['bases'],setting['allocations']):
     identity=dict(key=key,repeat=rep,fold=setting['fold'],basis=b);seed=np.random.SeedSequence([cfg()['seed'],*np.frombuffer(bytes.fromhex(uid(identity)),dtype='<u4').tolist()]);count=np.random.default_rng(seed).multinomial(num,dist[b]);cc.append(count);ds[b]=count/num
    v,den=estimated_vector(ds,8,method=='sv');vs.append(v);dd.append(den)
   samples.append(coeff@np.array(vs));counts.append(cc);denoms.append(dd)
  samples=np.array(samples);counts=np.array(counts,dtype=np.int32);disposition='newly_executed';source=None;stream='Independent followup SeedSequence keyed by full scientific fingerprint, repeat, fold and basis; shared observables use same joint counts'
 assert counts.shape[0]==32
 expected=np.array([a for s in settings for a in s['allocations']]);np.testing.assert_array_equal(counts.sum(-1),np.tile(expected,(32,1)))
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,samples=samples,counts=counts,exact=exact,own_clean=data(row)['clean'],covariance=np.cov(samples,rowvar=False),denominators=denoms)
 oneq=sum(sum(s['allocations'])*r['one_qubit_gates']+sum(num*sum(b!='Z' for b in basis) for basis,num in zip(s['bases'],s['allocations'])) for s,(d,r) in zip(settings,probabilities))
 r=dict(key=key,point_id=row['id'],kappa=row['kappa'],h=row['h'],p=p,method=method,mode=mode,budget=budget,settings=settings,archive=str(a.relative_to(ROOT)),sha256=sha(a),probabilities=[r for d,r in probabilities],shots_per_repeat=total,CNOT_shots_per_repeat=cost,one_qubit_gate_shots_per_repeat=oneq,measurement_settings=sum(len(s['bases']) for s in settings),target_CNOT_shots=budget*c,zero_CNOT_control=zero,equal_CNOT_verified=mode=='equal_gate' and not zero,budget_shortfall=budget*c-cost if mode=='equal_gate' else None,seconds=time.perf_counter()-t,disposition=disposition,source=source,random_stream=stream,unclipped=True);dump(meta,r);return r
