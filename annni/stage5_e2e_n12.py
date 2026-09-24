"""Literal circuit execution, joint-bitstring sufficient statistics and frozen diagnostics."""
import json,hashlib,time
import numpy as np
from .stage5_adapt import ROOT,OUT,PLAN,sha,dump,guard
from .upgrade_gates import *
from .upgrade_mitigation import measurement_probs,estimated_vector,LINEAR
from .stage5_measurement_groups import groups
from .upgrade_detection import predict
CFG=json.loads((OUT/'n12_scaling/detection_frozen.json').read_text())
def hva_gates(params,n):
 gates=reference_gates(n,'plus')
 for gamma,eta,beta in params:
  for distance,angle in [(1,gamma),(2,eta)]:
   for i in range(n):j=(i+distance)%n;gates += [('CNOT',i,j),('RZ',j,2*float(angle)),('CNOT',i,j)]
  gates += [('RX',i,2*float(beta)) for i in range(n)]
 return gates

def distributions(row,p,fold=1,sv=False):
 n=row['n'];g=row['gates'];g=[gate for x in g for gate in ([x]*fold if x[0]=='CNOT' else [x])];key=dict(n=n,p=p,gates=g,backend=sha(ROOT/'annni/upgrade_gates.py'),measure=sha(ROOT/'annni/upgrade_mitigation.py'),measurement_backend=sha(ROOT/'annni/stage5_measurement_groups.py'),sv=sv);uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();path=OUT/'end_to_end/probabilities'/uid;path.parent.mkdir(exist_ok=True);meta=path.with_suffix('.json');archive=path.with_suffix('.npz')
 if meta.exists():
  r=json.loads(meta.read_text());assert r['key']==json.loads(json.dumps(key)) and sha(archive)==r['sha256'];a=np.load(archive);return {b:a[f'p{i}'] for i,b in enumerate(r['bases'])},r
 guard();t=time.perf_counter();reused_density=None
 for candidate in (OUT/'noise/cache').glob('*.json'):
  cached=json.loads(candidate.read_text());ck=cached['key']
  if ck['n']==n and ck['p']==p and ck.get('keep_density') and ck['gates']==json.loads(json.dumps(g)) and ck['backend']==sha(ROOT/'annni/upgrade_gates.py'):
   assert sha(ROOT/cached['archive'])==cached['sha256'];reused_density=cached;break
 rho=np.load(ROOT/reused_density['archive'])['rho'] if reused_density else density(g,n,p);assert abs(np.trace(rho)-1)<1e-9 and np.max(abs(rho-rho.conj().T))<1e-10
 if p==0:np.testing.assert_allclose(rho,np.outer(row['state'],row['state'].conj()),atol=1e-10)
 dist=groups(rho) if sv else {b:measurement_probs(rho,b) for b in ['Z'*n,'X'*n]};ob=vector(observations(rho,n));np.savez_compressed(archive,**{f'p{i}':v for i,v in enumerate(dist.values())},observables=ob);r=dict(key=json.loads(json.dumps(key)),bases=list(dist),sha256=sha(archive),archive=str(archive.relative_to(ROOT)),seconds=time.perf_counter()-t,cnots=resources(g,n)['cnots'],disposition='newly_executed measurements from reused density' if reused_density else 'newly_executed',density_source=reused_density['archive'] if reused_density else None);dump(meta,r);return dist,r

def anchor(k,h,ed,n):
 # Frozen physical-limit anchors, qualified by independent ED observables, not D1 labels.
 if k<=.15 and h<=.2 and ed[n]>=.8:return 'ferro-like'
 if k>=.85 and h<=.2 and ed[n+n//4]>=.4:return 'antiphase-like'
 if k<=.3 and h>=1.8 and ed[-1]>=.85:return 'paramagnetic-like'
 return None

def measured(row,p,method):
 n=row['n'];key=dict(kappa=row['kappa'],h=row['h'],gates=row['gates'],p=p,method=method,n=n,code=sha(ROOT/'annni/stage5_e2e_n12.py'),measurement_backend=sha(ROOT/'annni/stage5_measurement_groups.py'),diagnostic_sha=sha(OUT/'n12_scaling/detection_frozen.json'),budgets=PLAN['mitigation_shots'],replicates=32);uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();path=OUT/'end_to_end/measurements'/uid;path.parent.mkdir(exist_ok=True);meta=path.with_suffix('.json');archive=path.with_suffix('.npz')
 if meta.exists():r=json.loads(meta.read_text());assert sha(archive)==r['sha256'];return r
 folds=[1,3,5] if method=='zne' else [1];ds=[];records=[]
 for f in folds:
  d,r=distributions(row,p,f,method=='sv');ds.append(d);records.append(r)
 exact=[estimated_vector(d,n,method=='sv')[0] for d in ds];truth=LINEAR@np.array(exact) if method=='zne' else exact[0];samples={};stats={};sampling={};cost={};quality=[]
 v0=vector(observations(row['state'],n));ved=row['ed_vector'];label=anchor(row['kappa'],row['h'],ved,n)
 for budget in PLAN['mitigation_shots']:
  rng=np.random.default_rng(np.random.SeedSequence([51051,int(uid[:8],16),budget]));vals=[];allcounts=[];alloc_scales=[budget] if method!='zne' else [budget//3+(i<budget%3) for i in range(3)];groups_list=[]
  for dist,amount in zip(ds,alloc_scales):
   bases=list(dist);alloc=np.full(len(bases),amount//len(bases));alloc[:amount%len(bases)]+=1;groups_list.append((bases,alloc))
  for rep in range(32):
   svectors=[];repcounts=[];denominators=[]
   for dist,(bases,alloc) in zip(ds,groups_list):
    counts=np.array([rng.multinomial(int(a),dist[b]) for b,a in zip(bases,alloc)],dtype=np.int32);estimate={b:c/int(a) for b,c,a in zip(bases,counts,alloc)};v,den=estimated_vector(estimate,n,method=='sv');svectors.append(v);repcounts.extend(counts);denominators.append(den)
   vals.append(LINEAR@np.array(svectors) if method=='zne' else svectors[0]);allcounts.append(np.array(repcounts));quality.append(dict(budget=budget,rep=rep,denominators=denominators))
  v=np.array(vals);samples[f'samples_{budget}']=v;samples[f'counts_{budget}']=np.array(allcounts);pred=[predict(x,CFG) if np.isfinite(x).all() else dict(D1='degraded',D3='degraded') for x in v];stats[str(budget)]=dict(mean=v.mean(0).tolist(),covariance=np.cov(v,rowvar=False).tolist(),mse_own_clean=np.mean((v-v0)**2,axis=0).tolist(),mse_ED=np.mean((v-ved)**2,axis=0).tolist(),D1=[x['D1'] for x in pred],D3=[x['D3'] for x in pred],nonfinite=int(np.sum(~np.isfinite(v))),outside_physical=int(np.sum((abs(v[:,:n])>1)|(abs(v[:,n:2*n])>1))),repeated_error_quantiles=np.quantile(np.max(abs(v-ved),axis=1),[.025,.5,.975]).tolist());sampling[str(budget)]=[dict(bases=b,allocations=a.tolist()) for b,a in groups_list];cost[str(budget)]=dict(total_shots=budget,gate_shots=int(sum(a*r['cnots'] for a,r in zip(alloc_scales,records))),measurement_settings=sum(len(b) for b,_ in groups_list))
 np.savez_compressed(archive,ideal=v0,ed=ved,deterministic=truth,**samples);r=dict(key=key,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),n=n,kappa=row['kappa'],h=row['h'],p=p,method=method,anchor=label,prep_pass=row['joint_pass'],statistics=stats,sampling=sampling,cost=cost,quality=quality,probability_records=records,deterministic_prediction=predict(truth,CFG),ED_diagnostic=predict(ved,CFG),disposition='newly_executed',randomization='Independent repetitions across distinct physical estimation keys; identical cached keys reuse exactly the same counts across arm labels. All same-basis observables share joint counts.',unclipped=True);dump(meta,r);return r
