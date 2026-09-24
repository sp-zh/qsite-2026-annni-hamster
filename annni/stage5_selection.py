"""State-access-assisted selectors. ED fields never enter deployment selection."""
import json,time,hashlib
from pathlib import Path
import numpy as np
from .stage5_adapt import ROOT,OUT,PLAN,sha,dump,assess,optimize_words
from .upgrade_gates import *
def translate(state,n,r=1):
 ids=np.arange(1<<n);r%=n;dest=((ids<<r)&((1<<n)-1))|(ids>>(n-r));out=np.empty_like(state);out[dest]=state;return out

def symmetry(state,n,k,h):
 P=float(np.vdot(state,state[::-1]).real);T=np.vdot(state,translate(state,n));s0=sum(translate(state,n,r) for r in range(n))/n;w0=float(np.vdot(s0,s0).real);joint=(s0+s0[::-1])/2;hs=h_action(state,n,k,h);e=float(np.vdot(state,hs).real)
 return dict(parity=P,w_plus=(1+P)/2,T_real=float(T.real),T_imag=float(T.imag),eta_T=float(1-T.real),w0=w0,w_plus_0=float(np.vdot(joint,joint).real),variance=float(np.vdot(hs,hs).real-e*e),energy=e)

def choose(candidates,rule,cfg=None):
 # Only energy/resource/state-access metrics; no ED, gap, coordinate labels or fidelity.
 n=candidates[0]['n'];cfg=cfg or {};unresolved=False;pool=candidates
 if rule=='S0':
  refs={}
  for c in candidates:refs.setdefault((c['ref'],c['seed']),[]).append(c)
  reduced=[]
  for group in refs.values():
   emin=min(c['energy'] for c in group);reduced.append(min((c for c in group if c['energy']<=emin+n*1e-4),key=lambda c:(c['cnots'],c['energy'])))
  pool=reduced;tol=n*1e-4
 elif rule=='S1':tol=PLAN['selector_numerical_tie_total']
 elif rule=='S2':
  pool=[c for c in candidates if c['w0']>=cfg['w0_min'] and c['w_plus']>=cfg['parity_min']]
  if not pool:pool=candidates;unresolved=True
  tol=n*cfg['energy_tolerance_per_site']
 else:raise ValueError(rule)
 emin=min(c['energy'] for c in pool);winner=min((c for c in pool if c['energy']<=emin+tol),key=lambda c:(c['cnots'],c['variance'],c['energy']))
 return dict(candidate=winner,selection_unresolved=unresolved,rule=rule,energy_tolerance_total=tol,state_access_assisted=rule=='S2')

def load_candidates(runs):
 out=[];seen=set()
 for run in runs:
  if run['method']!='cost':continue
  path=ROOT/run.get('run_record',str(Path(run['archive']).with_suffix('.json')))
  raw=json.loads(path.read_text());assert sha(ROOT/raw['archive'])==raw['sha256']
  for j,c in enumerate(raw['checkpoints']):
   uid=hashlib.sha256(json.dumps([raw['ref'],c['words'],c['params']],sort_keys=True).encode()).hexdigest()
   if uid in seen:continue
   seen.add(uid);state=state_and_grad(np.array(c['params']),c['words'],raw['n'],raw['ref'],raw['kappa'],raw['h'])[2];met,ob,ed=assess(state,raw['n'],raw['kappa'],raw['h']);sym=symmetry(state,raw['n'],raw['kappa'],raw['h']);out.append(dict(**{k:v for k,v in c.items() if k not in sym and k not in met},**(met|sym),n=raw['n'],kappa=raw['kappa'],h=raw['h'],ref=raw['ref'],seed=raw['seed'],uid=uid,source=str(path.relative_to(ROOT)),source_sha=sha(path),checkpoint=j,source_stop=raw['stop'],source_budget=raw['key']['budget'],disposition='historical_reused' if 'stage4' in str(path) else 'newly_executed'))
 return out

def materialize(c):
 p=OUT/'selected'/c['uid'];p.parent.mkdir(exist_ok=True);a=p.with_suffix('.npz');m=p.with_suffix('.json')
 if m.exists():
  row=json.loads(m.read_text());assert sha(a)==row['sha256'];return row
 state=state_and_grad(np.array(c['params']),c['words'],c['n'],c['ref'],c['kappa'],c['h'])[2];met,ob,ed=assess(state,c['n'],c['kappa'],c['h']);np.savez_compressed(a,state=state,ed_state=ed,params=c['params'],words=c['words'],**ob)
 row=dict(n=c['n'],kappa=c['kappa'],h=c['h'],ref=c['ref'],seed=c['seed'],selected=c,archive=str(a.relative_to(ROOT)),sha256=sha(a),**met);dump(m,row);return row

def retry(candidates,cfg):
 s=choose(candidates,'S2',cfg);best=min(candidates,key=lambda c:c['energy']);trigger=s['selection_unresolved'] or s['candidate']['energy']>best['energy']+best['n']*.001
 if not trigger:return candidates,dict(triggered=False)
 key=hashlib.sha256(json.dumps([best['uid'],PLAN['reopt'],cfg],sort_keys=True).encode()).hexdigest();path=OUT/'reopt'/f'{key}.json'
 if path.exists():r=json.loads(path.read_text());return candidates+[r['candidate']],r
 t=time.perf_counter();fit,state=optimize_words(best['n'],best['kappa'],best['h'],best['ref'],best['words'],best['params'],maxiter=2000);met,ob,ed=assess(state,best['n'],best['kappa'],best['h']);sym=symmetry(state,best['n'],best['kappa'],best['h']);c=best|met|sym|dict(params=fit.x.tolist(),uid=key,optimizer_success=bool(fit.success),disposition='newly_executed',initial_source=best['uid']);r=dict(triggered=True,candidate=c,seconds=time.perf_counter()-t,nfev=int(fit.nfev),nit=int(fit.nit),message=str(fit.message),independent_cold_start=False);dump(path,r);return candidates+[c],r
