import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
from annni.vqe import optimize
O=OUT/'ablation';O.mkdir(exist_ok=True);dev=json.loads((OUT/'development/index.json').read_text());rows=[]
# Independent given-definition pilot, original uploaded parameters absent.
for k,h in [(0,.2),(.3,.2),(.3,.4)]:
 r=adaptive(8,k,h,'ghz',11,128,fixed=True,group='independent_pilot');rows.append(dict(kind='23-CNOT pilot',row=r,original_files_available=False))
# Development-only bounded pool/pruning/search-budget ablations, never heldout tuning.
for k,h in [(0,.2),(.3,.4),(.8,.5)]:
 point=next(p for p in dev if p['kappa']==k and p['h']==h);winner=point['methods']['B3'];s=winner['selected']
 for ref in PLAN['refs']:
  r=adaptive(8,k,h,ref,11,128,extended=False,group='pool_ablation');rows.append(dict(kind='two-site pool only',row=r))
 words=[];params=[]
 for w,t in zip(s['words'],s['params']):
  if abs(t)<1e-3:continue
  if words and words[-1]==w:params[-1]+=t
  else:words.append(w);params.append(t)
 fit,state=optimize_words(8,k,h,winner['ref'],words,np.array(params));met,o,ed=assess(state,8,k,h)
 g=compile_circuit(8,winner['ref'],words,fit.x);rows.append(dict(kind='prune merge reopt',kappa=k,h=h,before_cnots=s['cnots'],after_cnots=resources(g,8)['cnots'],threshold=.001,energy_change=float(fit.fun-winner['energy']),accepted_by_energy=bool(fit.fun<=winner['energy']+.0008),params=fit.x.tolist(),words=words,**met))
 for j,adapt in enumerate([r for r in point['candidates'] if r['method']=='cost']):
  seed=10000+j;theta=np.random.default_rng(seed).uniform(-.5,.5,(6,3));budget=max(20,adapt['nfev']);status,params,state,trace=optimize(theta,k,h,dict(maxiter=budget,maxfun=budget,ftol=1e-12,gtol=1e-7,maxls=30));met,o,ed=assess(state,8,k,h);name=f'fair_k{k}_h{h}_s{seed}'
  np.savez_compressed(O/(name+'.npz'),initial=theta,params=params,state=state,trace=trace);rows.append(dict(kind='matched energy-gradient evaluation cap HVA',kappa=k,h=h,seed=seed,cap=budget,adaptive_source=adapt['archive'],actual_hva_nfev=status['nfev'],scipy_possible_final_linesearch_overshoot=True,cnots=192,status=status,**met,archive=str((O/(name+'.npz')).relative_to(ROOT))))
 # Single-error sensitivities for identical ideal circuit. First-order approximation only.
 gates=compile_circuit(8,winner['ref'],s['words'],s['params']);v0=vector(observations(evolve(gates,8),8));inj=[]
 for j in range(s['cnots']):
  for pauli in range(3):inj.append(vector(observations(evolve(gates,8,injection=(j,pauli)),8))-v0)
 inj=np.array(inj);np.savez_compressed(O/f'injection_k{k}_h{h}.npz',single_error_changes=inj,first_derivative=inj.reshape(-1,3,17).mean(1).sum(0),ideal=v0)
 rows.append(dict(kind='single error injection',kappa=k,h=h,cnots=s['cnots'],error_configurations=len(inj),source=winner['archive'],scope='first order derivative at p0, not exact p=.05'))
 dump(O/'index.json',rows);print(k,h,len(rows),flush=True)
