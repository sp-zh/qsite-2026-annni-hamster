"""Energy-only bounded ADAPT, auditable independent starts and checkpoints."""
import json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from scipy.optimize import minimize
from .upgrade_gates import *
from .model import Chain
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage4_upgrade_v1'
PLAN=json.loads((OUT/'experiment_plan.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2));t.replace(p)
def guard():
 if datetime.now(timezone.utc)>=datetime.fromisoformat(PLAN['deadline']):raise TimeoutError('New 12 hour budget reached; resume checkpoint preserved')
def fp():return {f:sha(ROOT/f) for f in ['annni/upgrade_gates.py','annni/upgrade_adapt.py','configs/stage4_upgrade_v1.json','annni/model.py']}
def reference(n,k,h):
 assert h>0
 path=OUT/'ed'/f'n{n}_k{k.hex()}_h{h.hex()}.npz'
 if path.exists():
  a=np.load(path);return a['state'],float(a['energy']),str(path.relative_to(ROOT))
 source='newly_executed'
 if n==8:
  a=np.load(ROOT/'results/baseline/grid_n8.npz');ii=np.flatnonzero(abs(a['kappa']-k)<1e-12);jj=np.flatnonzero(abs(a['h']-h)<1e-12)
  if len(ii)==len(jj)==1:
   s=a['states'][ii[0],jj[0]];e=float(a['energy_per_site'][ii[0],jj[0]]*8);source='historical_reused results/baseline/grid_n8.npz'
  else:r=Chain(n).ground_state(k,h);s,e=r.state,r.energy
 else:r=Chain(n).ground_state(k,h);s,e=r.state,r.energy
 path.parent.mkdir(exist_ok=True);np.savez_compressed(path,state=s,energy=e,n=n,kappa=k,h=h,source=source)
 return s,e,str(path.relative_to(ROOT))
def assess(state,n,k,h):
 ed,e,src=reference(n,float(k),float(h));o=observations(state,n);r=observations(ed,n)
 energy=float(np.vdot(state,h_action(state,n,k,h)).real);de=(energy-e)/n
 if de < -1e-9:raise ArithmeticError(de)
 t=PLAN['thresholds'];ec=float(max(abs(o['correlations']-r['correlations'])));es=float(max(abs(o['structure_factor']-r['structure_factor'])));em=abs(o['mx']-r['mx']);f=float(abs(np.vdot(ed,state))**2)
 op=de<=t['delta_e'] and ec<=t['epsilon_c'] and es<=t['epsilon_sf'] and em<=t['epsilon_mx'];sp=f>=t['fidelity']
 return dict(energy=energy,ed_energy=e,delta_e=de,epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,fidelity=f,observable_pass=bool(op),state_pass=bool(sp),joint_pass=bool(op and sp),ed_source=src),o,ed

def optimize_words(n,k,h,ref,words,initial,maxiter=None):
 def fun(x):return state_and_grad(x,words,n,ref,k,h)[:2]
 fit=minimize(fun,initial,jac=True,method='L-BFGS-B',options=dict(maxiter=maxiter or PLAN['maxiter'],ftol=PLAN['ftol'],gtol=PLAN['gtol'],maxls=30))
 return fit,state_and_grad(fit.x,words,n,ref,k,h)[2]
def adaptive(n,k,h,ref,seed,budget=128,rule='cost',extended=True,group='development',fixed=False):
 guard();k=float(k);h=float(h)
 key=dict(n=n,k=k,h=h,ref=ref,seed=seed,budget=budget,rule=rule,extended=extended,fixed=fixed,fp=fp())
 uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();path=OUT/'adaptive/cache'/uid;meta=path.with_suffix('.json')
 if meta.exists():
  result=json.loads(meta.read_text());assert result['key']==key and sha(path.with_suffix('.npz'))==result['sha256'];return result
 start=time.perf_counter();rng=np.random.default_rng(np.random.SeedSequence([seed,n,round(k*100000),round(h*100000)]));words=[];params=np.array([]);state=evolve(reference_gates(n,ref),n);energy=float(np.vdot(state,h_action(state,n,k,h)).real);base=resources(reference_gates(n,ref),n)['cnots'];poolwords=pool(n,extended);costs=np.array([2*(len(w)-w.count('I')-1) for w in poolwords]);steps=[];checkpoints=[];calls=iters=0
 def savepoint(reason,success):
  met,ob,ed=assess(state,n,k,h);g=compile_circuit(n,ref,words,params)
  checkpoints.append(dict(words=words.copy(),params=params.tolist(),reason=reason,optimizer_success=success,**resources(g,n),**met))
 savepoint('reference',True)
 thresholds=PLAN['cnots_checkpoints'] if n==8 else PLAN['n12_cnots_checkpoints']; reached=set();stop='budget'
 if fixed:
  words=[]
  for i in range(n):
   w=['I']*n;w[i]='Y';w[(i+1)%n]='Z';words.append(''.join(w))
  initial=rng.uniform(-.15,.15,len(words));fit,state=optimize_words(n,k,h,ref,words,initial);params=fit.x;energy=float(fit.fun);calls+=fit.nfev;iters+=fit.nit
  steps.append(dict(initial=initial.tolist(),params=params.tolist(),energy=energy,success=bool(fit.success),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev)))
  savepoint('fixed_short',bool(fit.success));stop='fixed_short'
 else:
  while True:
   guard();used=base+sum(2*(len(w)-w.count('I')-1) for w in words);eligible=used+costs<=budget
   if not eligible.any():break
   hs=h_action(state,n,k,h)
   grads=np.array([2*np.vdot(hs,-1j*apply_pauli(state,w)).real for w in poolwords]);scores=abs(grads)/(costs if rule=='cost' else 1);scores[~eligible]=-1
   best=scores.max()
   if best<PLAN['gradient_stop']:
    stop='pool_gradient';break
   tied=np.flatnonzero(scores>=best*(1-1e-8)-1e-12);idx=int(rng.choice(tied));words.append(poolwords[idx]);initial=np.r_[params,rng.uniform(-.01,.01)];fit,state=optimize_words(n,k,h,ref,words,initial);params=fit.x;previous=energy;energy=float(fit.fun);calls+=fit.nfev;iters+=fit.nit
   used+=int(costs[idx]);steps.append(dict(step=len(words),word=poolwords[idx],pool_gradient=grads.tolist(),selected_gradient=float(grads[idx]),initial=initial.tolist(),params=params.tolist(),energy=energy,cnots=used,success=bool(fit.success),message=str(fit.message),nit=int(fit.nit),nfev=int(fit.nfev)))
   for b in thresholds:
    if b not in reached and used>=b-1 and used<=b:
     savepoint('budget_checkpoint_'+str(b),bool(fit.success));reached.add(b)
   if abs(previous-energy)<PLAN['improvement_stop']:
    stop='energy_stagnation';break
  savepoint(stop,bool(steps[-1]['success']) if steps else True)
 # Do not select using ED; all checkpoints retained including failed states.
 emin=min(c['energy'] for c in checkpoints);candidates=[c for c in checkpoints if c['energy']<=emin+n*PLAN['selection_energy_tolerance_per_site']];selected=min(candidates,key=lambda c:(c['cnots'],c['energy']))
 chosen=state_and_grad(np.array(selected['params']),selected['words'],n,ref,k,h)[2];m,o,ed=assess(chosen,n,k,h)
 path.parent.mkdir(parents=True,exist_ok=True);archive=path.with_suffix('.npz');np.savez_compressed(archive,params=selected['params'],words=selected['words'],state=chosen,ed_state=ed,**o)
 result=dict(key=key,n=n,kappa=k,h=h,ref=ref,seed=seed,group_first=group,method='fixed' if fixed else rule,selected=selected,checkpoints=checkpoints,steps=steps,stop=stop,seconds=time.perf_counter()-start,nfev=int(calls),nit=int(iters),pool_gradient_evaluations=len(steps)*len(poolwords),gradient_measurement_note='analytic statevector derivatives; parameter shift hardware upper bound 2*pool size energies per step, each energy has 2 commuting bases',archive=str(archive.relative_to(ROOT)),sha256=sha(archive),disposition='newly_executed',**m)
 dump(meta,result);return result

def select(rows):
 best=min(r['energy'] for r in rows);eligible=[r for r in rows if r['energy']<=best+r['n']*PLAN['selection_energy_tolerance_per_site']]
 return min(eligible,key=lambda r:(r['selected']['cnots'],r['energy']))
