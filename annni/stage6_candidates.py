"""Energy-only physical/wall-basis ADAPT. This module never imports/loads ED.

Wall frame: y0=b0, yj=b(j-1) XOR bj. The closing wall is XOR(y1..).
Decode CNOT(0,1)..(N-2,N-1) is part of the literal, noisy circuit.
Y rotations and YZ/ZY blocks on wall bits permit changing total wall number;
no projection to the no-adjacent-wall effective subspace is used.
"""
from functools import lru_cache
from scipy.optimize import minimize
from .stage6_common import *
from .upgrade_gates import *
@lru_cache(4)
def decode_indices(n):
 y=np.arange(1<<n);b=np.zeros_like(y);bit=np.zeros_like(y)
 for j in range(n):
  bit^=(y>>(n-1-j))&1;b|=bit<<(n-1-j)
 return b,np.argsort(b)
def frame_to_physical(s,n,basis):return s if basis=='physical' else s[decode_indices(n)[1]]
def physical_to_frame(s,n,basis):return s if basis=='physical' else s[decode_indices(n)[0]]
def start_gates(n,basis,ref):
 if basis=='physical':return reference_gates(n,ref)
 if ref=='uniform':return [('H',i) for i in range(n)]
 if ref=='empty':return [('H',0)]
 if ref=='alternating':return [('H',0)]+[('X',j) for j in range(2,n,2)]
 raise ValueError(ref)
def gate_table(n,basis,ref,words,params,fold=1):
 g=start_gates(n,basis,ref)
 for w,t in zip(words,params):g+=pauli_gates(w,t)
 if basis=='wall':g += [('CNOT',i,i+1) for i in range(n-1)]
 assert all(min(abs(x[1]-x[2]),n-abs(x[1]-x[2]))<=2 for x in g if x[0]=='CNOT')
 return [x for gate in g for x in ([gate]*fold if gate[0]=='CNOT' else [gate])]
def words_pool(n,basis):
 if basis=='physical':return pool(n,True)
 out=[]
 for i in range(1,n):
  w=['I']*n;w[i]='Y';out.append(''.join(w))
 for d in [1,2]:
  for i in range(1,n-d):
   for pair in ['YZ','ZY','YX','XY']:
    w=['I']*n;w[i]=pair[0];w[i+d]=pair[1];out.append(''.join(w))
 return out
def evaluate(params,words,n,basis,ref,k,h,initial_state=None,target=None):
 s=evolve(start_gates(n,basis,ref),n) if initial_state is None else initial_state.copy();states=[]
 for t,w in zip(params,words):s=rotate(s,w,t);states.append(s)
 physical=frame_to_physical(s,n,basis)
 if target is None:adj=physical_to_frame(h_action(physical,n,k,h),n,basis);value=float(np.vdot(s,adj).real)
 else:
  targetframe=physical_to_frame(target,n,basis);overlap=np.vdot(targetframe,s);value=float(1-abs(overlap)**2);adj=-overlap*targetframe
 gradient=np.empty(len(words))
 for j in range(len(words)-1,-1,-1):
  gradient[j]=2*np.vdot(adj,-1j*apply_pauli(states[j],words[j])).real;adj=rotate(adj,words[j],-params[j])
 return value,gradient,physical
def optimize(n,k,h,basis,ref,words,initial,maxiter):
 initial_state=evolve(start_gates(n,basis,ref),n)
 def fun(x):return evaluate(x,words,n,basis,ref,k,h,initial_state)[:2]
 t=time.perf_counter();fit=minimize(fun,initial,jac=True,method='L-BFGS-B',options=dict(maxiter=maxiter,ftol=PLAN['optimization']['ftol'],gtol=PLAN['optimization']['gtol'],maxls=30))
 return fit,dict(initial=np.asarray(initial).tolist(),final=fit.x.tolist(),energy=float(fit.fun),nit=int(fit.nit),nfev=int(fit.nfev),success=bool(fit.success),reason=str(fit.message),seconds=time.perf_counter()-t)
def adaptive(n,k,h,basis,ref,search,seed,budget=128,group='development'):
 guard();key=dict(n=n,kappa=float(k),h=float(h),basis=basis,ref=ref,search=search,seed=seed,budget=budget,code=sha(__file__),backend=sha(ROOT/'annni/upgrade_gates.py'),optimizer=PLAN['optimization'],search_config=PLAN['search']);base=OUT/'domain_wall_candidates/cache'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():
  r=json.loads(meta.read_text());assert r['key']==key and sha(ROOT/r['archive'])==r['sha256'];return r
 rng=np.random.default_rng(seed);start=time.perf_counter();words=[];params=np.array([]);state=evolve(start_gates(n,basis,ref),n);physical=frame_to_physical(state,n,basis);energy=float(np.vdot(physical,h_action(physical,n,k,h)).real);poolwords=words_pool(n,basis);cost=np.array([max(0,2*(sum(p!='I' for p in w)-1)) for w in poolwords]);basecost=resources(gate_table(n,basis,ref,[],[]),n)['cnots'];used=basecost;steps=[];checkpoints=[];gradient_evals=0;stop='budget';checkpoints_at=[64,96,128,192,256]
 def savepoint(reason,success):
  gates=gate_table(n,basis,ref,words,params);checkpoints.append(dict(params=params.tolist(),words=words.copy(),energy=energy,optimizer_success=success,reason=reason,**resources(gates,n)))
 savepoint('reference_not_optimized',None)
 reached=set()
 for step in range(160):
  guard();eligible=used+cost<=budget
  if not eligible.any():break
  adj=physical_to_frame(h_action(physical,n,k,h),n,basis);grads=np.array([2*np.vdot(adj,-1j*apply_pauli(state,w)).real for w in poolwords]);gradient_evals+=len(poolwords);scores=abs(grads)/np.maximum(cost,1);scores[~eligible]=-1
  if max(scores)<1e-8:stop='pool_gradient';break
  ranked=np.argsort(-scores,kind='stable');probes=[]
  if search=='top4':
   for j in ranked[:min(4,int(eligible.sum()))]:
    initial=np.r_[params,rng.uniform(-.01,.01)];fit,log=optimize(n,k,h,basis,ref,words+[poolwords[j]],initial,35);probes.append(dict(index=int(j),word=poolwords[j],**log))
   winner=min(probes,key=lambda x:(x['energy'],cost[x['index']],x['index']));j=winner['index'];initial=np.array(winner['final'])
  else:
   tied=np.flatnonzero(scores>=max(scores)*(1-1e-8)-1e-12);j=int(rng.choice(tied));initial=np.r_[params,rng.uniform(-.01,.01)]
  words.append(poolwords[j]);fit,log=optimize(n,k,h,basis,ref,words,initial,PLAN['optimization']['maxiter']);params=fit.x;previous=energy;energy,_,physical=evaluate(params,words,n,basis,ref,k,h);state=physical_to_frame(physical,n,basis);used+=int(cost[j]);steps.append(dict(step=step,word=poolwords[j],cnots=used,pool_gradient=grads.tolist(),probes=probes,optimization=log))
  for cap in checkpoints_at:
   if cap not in reached and cap-1<=used<=cap:savepoint('checkpoint_'+str(cap),bool(fit.success));reached.add(cap)
  if abs(previous-energy)<1e-12:stop='energy_stagnation';break
  if used>=budget and all(cost[q]>0 or abs(grads[q])<1e-8 for q in range(len(cost))):break
 else:stop='parameter_cap160'
 savepoint(stop,bool(steps[-1]['optimization']['success']) if steps else None)
 emin=min(c['energy'] for c in checkpoints);selected=min([c for c in checkpoints if c['energy']<=emin+n*1e-6],key=lambda c:(c['cnots'],c['energy']));_,_,state=evaluate(selected['params'],selected['words'],n,basis,ref,k,h);gates=gate_table(n,basis,ref,selected['words'],selected['params']);base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,state=state,params=selected['params'],words=selected['words'],**observations(state,n));logs=[s['optimization'] for s in steps]+[p for s in steps for p in s['probes']]
 r=dict(key=key,n=n,kappa=k,h=h,basis=basis,ref=ref,search=search,seed=seed,selected=selected,checkpoints=checkpoints,steps=steps,gates=gates,stop=stop,seconds=time.perf_counter()-start,nfev=sum(x['nfev'] for x in logs),nit=sum(x['nit'] for x in logs),pool_gradient_evaluations=gradient_evals,archive=str(a.relative_to(ROOT)),sha256=sha(a),group=group,disposition='newly_executed',access='Pure-state analytic energy/gradients; no ED, fidelity, symmetry filter or free state projection');dump(meta,r);return r
def select(rows,tolerance=1e-6):
 emin=min(r['selected']['energy'] for r in rows);return min([r for r in rows if r['selected']['energy']<=emin+r['n']*tolerance],key=lambda r:(r['selected']['cnots'],r['selected']['energy']))
