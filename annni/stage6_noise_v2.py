"""Version2 measurement streams: common seed families across arms/noise/estimators.
Physical simulation and estimators unchanged; old pilot v1 records retained.
"""
import resource
from .stage6_common import *
from .upgrade_gates import *
from .upgrade_mitigation import measurement_probs,estimated_vector,LINEAR
from .stage5_measurement_groups import groups
def stream(n,k,h,budget,rep,fold,basis):
 identity=dict(n=int(n),kappa_exact=float(k),h_exact=float(h),budget=int(budget),repeat=int(rep),fold=int(fold),basis=basis)
 return np.random.default_rng(np.random.SeedSequence([PLAN['measurement']['seed'],*np.frombuffer(bytes.fromhex(uid(identity)),dtype='<u4').tolist()]))
def physical(row,p,fold=1,need_sv=False,keep=False):
 assert 0<=p<=1 and fold in [1,3,5]
 n=row['n'];g=[x for gate in row['gates'] for x in ([gate]*fold if gate[0]=='CNOT' else [gate])]
 key=dict(n=n,kappa=float(row['kappa']),h=float(row['h']),bc='PBC',gates=g,p=float(p),backend=sha(ROOT/'annni/upgrade_gates.py'),measurement_code=sha(ROOT/'annni/stage5_measurement_groups.py'),sv=need_sv,keep=keep,shots=None);base=OUT/'end_to_end/probabilities'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  r=json.loads(meta.read_text());assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);return {b:a[f'p{i}'] for i,b in enumerate(r['bases'])},r
 guard();t=time.perf_counter();rho=density(g,n,p);trace=np.trace(rho);herr=float(np.max(abs(rho-rho.conj().T)));assert abs(trace-1)<1e-9 and herr<1e-10
 if p==0:np.testing.assert_allclose(rho,np.outer(row['state'],row['state'].conj()),atol=1e-10)
 minimum=float(np.linalg.eigvalsh(rho).min()) if n==8 else None
 if minimum is not None:assert minimum>-1e-9
 dist=groups(rho) if need_sv else {b:measurement_probs(rho,b) for b in ['Z'*n,'X'*n]};v=vector(observations(rho,n));base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,observables=v,**{f'p{i}':d for i,d in enumerate(dist.values())},**({'rho':rho} if keep else {}));res=resources(g,n)
 r=dict(key=key,n=n,kappa=row['kappa'],h=row['h'],p=p,fold=fold,bases=list(dist),archive=str(a.relative_to(ROOT)),sha256=sha(a),observables=v,seconds=time.perf_counter()-t,trace_real=float(trace.real),hermiticity=herr,min_eigenvalue=minimum,noise_channels=res['cnots'],process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**res,disposition='newly_executed');dump(meta,r);return dist,r
def measured(row,p,method,budgets=None):
 budgets=PLAN['measurement']['budgets'] if budgets is None else budgets
 n=row['n'];folds=[1,3,5] if method=='zne' else [1];records=[];ds=[]
 for fold in folds:
  d,r=physical(row,p,fold,method=='sv');records.append(r);ds.append(d)
 key=dict(probability_keys=[r['key'] for r in records],method=method,budgets=budgets,repeats=32,master_seed=PLAN['measurement']['seed'],estimator_code=sha(ROOT/'annni/upgrade_mitigation.py'),code=sha(__file__));base=OUT/'end_to_end/measurements'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  r=json.loads(meta.read_text());assert sha(ROOT/r['archive'])==r['sha256'];return r
 t=time.perf_counter();data={};sampling={};cost={};quality={};exact=[estimated_vector(d,n,method=='sv')[0] for d in ds];truth=LINEAR@np.array(exact) if method=='zne' else exact[0]
 for budget in budgets:
  scale_amounts=[budget] if len(folds)==1 else [budget//3+(i<budget%3) for i in range(3)];group_list=[]
  for d,amount in zip(ds,scale_amounts):
   b=list(d);alloc=np.full(len(b),amount//len(b));alloc[:amount%len(b)]+=1;group_list.append((b,alloc))
  samples=[];counts=[];denoms=[]
  for rep in range(32):
   vs=[];cc=[];dd=[]
   for fold_index,(d,(bs,alloc)) in enumerate(zip(ds,group_list)):
    c=np.array([stream(n,row['kappa'],row['h'],budget,rep,folds[fold_index],b).multinomial(int(a),d[b]) for b,a in zip(bs,alloc)],dtype=np.int32);v,den=estimated_vector({b:x/int(a) for b,x,a in zip(bs,c,alloc)},n,method=='sv');vs.append(v);cc.extend(c);dd.append(den)
   samples.append(LINEAR@np.array(vs) if method=='zne' else vs[0]);counts.append(cc);denoms.append(dd)
  v=np.array(samples);data[f'samples_{budget}']=v;data[f'counts_{budget}']=np.array(counts);data[f'covariance_{budget}']=np.cov(v,rowvar=False);sampling[str(budget)]=[dict(bases=b,allocations=a.tolist()) for b,a in group_list];cost[str(budget)]=dict(shots_per_rep=budget,all_reps_shots=32*budget,gate_shots_per_rep=int(sum(a*r['cnots'] for a,r in zip(scale_amounts,records))),settings=sum(len(b) for b,a in group_list),basis_single_qubit_gate_shots_per_rep=int(sum(int(amount)*sum(letter!='Z' for letter in b) for bases,alloc in group_list for b,amount in zip(bases,alloc))));quality[str(budget)]=dict(denominators=denoms,nonfinite=int(np.sum(~np.isfinite(v))),outside_range=int(np.sum((v[:,:n]<-1-1e-9)|(v[:,:n]>1+1e-9))),negative_structure_factor=int(np.sum(v[:,n:2*n]<-1e-9)),physical_comparison_tolerance=1e-9)
 base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,exact=truth,own_clean=vector(observations(row['state'],n)),**data);result=dict(key=key,n=n,kappa=row['kappa'],h=row['h'],p=p,method=method,archive=str(a.relative_to(ROOT)),sha256=sha(a),probability_records=records,sampling=sampling,cost=cost,quality=quality,seconds=time.perf_counter()-t,disposition='newly_executed',noise_scope='Every CNOT including references/decoding/folding target-depolarized',randomization='Shared per-coordinate/budget/repeat/fold/basis SeedSequence initialization across preparations and p; arm/p/estimator omitted. Multinomial algorithm draw consumption can differ with probabilities and allocations: this is common seeded streams, not identical categorical events. All detectors and linear/quadratic ZNE use the same archived counts.',stream_spec=dict(master_seed=PLAN['measurement']['seed'],fields=['n','kappa_exact','h_exact','budget','repeat','fold','basis'],omitted=['method','p','gates','estimator']),unclipped=True);dump(meta,result);return result
