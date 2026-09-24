"""Compiled-circuit density and trajectory data; complete provenance keys."""
import time,json,hashlib
import numpy as np
from .stage5_adapt import ROOT,OUT,PLAN,sha,dump,guard
from .upgrade_gates import *
_OLD=None
def physical_key(key):
 return hashlib.sha256(json.dumps({k:key[k] for k in ['n','kappa','h','p','fold','reverse','gates','backend']},sort_keys=True).encode()).hexdigest()
def old_lookup():
 global _OLD
 if _OLD is None:
  _OLD={}
  for p in (ROOT/'results/stage4_upgrade_v1/noise/cache').glob('*.json'):
   r=json.loads(p.read_text());_OLD.setdefault(physical_key(r['key']),[]).append(r)
 return _OLD
def noise_record(row,p,fold=1,reverse=False,keep=False):
 guard();n=row['n'];s=row['selected'];g=compile_circuit(n,row['ref'],s['words'],s['params'],fold,reverse)
 key=dict(keep_density=keep,n=n,kappa=row['kappa'],h=row['h'],p=p,fold=fold,reverse=reverse,gates=g,params=s['params'],bc='PBC',shots=None,backend=sha(ROOT/'annni/upgrade_gates.py'),noise_code=sha(ROOT/'annni/stage5_noise.py'),source_state_sha=row['sha256'])
 key=json.loads(json.dumps(key))
 uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();base=OUT/'noise/cache'/uid;meta=base.with_suffix('.json');archive=base.with_suffix('.npz')
 if meta.exists():
  r=json.loads(meta.read_text());assert r['key']==key and sha(ROOT/r['archive'])==r['sha256']
  if not keep or 'rho' in np.load(ROOT/r['archive']):return r
 for old in old_lookup().get(physical_key(key),[]):
  if keep and not old['key'].get('keep_density',False):continue
  assert sha(ROOT/old['archive'])==old['sha256']
  r=old|dict(key=key,disposition='historical_reused',historical_key=old['key'],prep_joint_pass=row['joint_pass'],reuse_reason='Identical literal gates, parameters, N/PBC, Hamiltonian point, p, fold/direction and unchanged upgrade_gates backend; source metadata changes do not change physical data')
  meta.parent.mkdir(parents=True,exist_ok=True);dump(meta,r);return r
 t=time.perf_counter();rho=density(g,n,p);simsec=time.perf_counter()-t;o=observations(rho,n)
 a=np.load(ROOT/row['archive']);pure=a['state'];ed=a['ed_state'];v=vector(o);v0=vector(observations(pure,n));ved=vector(observations(ed,n));res=resources(g,n)
 if p==0:np.testing.assert_allclose(rho,np.outer(pure,pure.conj()),atol=1e-10)
 check=dict(trace_real=float(np.trace(rho).real),trace_imag=float(np.trace(rho).imag),hermiticity_error=float(np.max(abs(rho-rho.conj().T))))
 assert abs(np.trace(rho)-1)<1e-9 and check['hermiticity_error']<1e-10
 if n==8:check['min_eigenvalue']=float(np.linalg.eigvalsh(rho).min());assert check['min_eigenvalue']>-1e-9
 base.parent.mkdir(parents=True,exist_ok=True)
 np.savez_compressed(archive,**o,prep=v0-ved,noise=v-v0,total=v-ved,**({'rho':rho} if keep else {}))
 r=dict(key=key,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),n=n,kappa=row['kappa'],h=row['h'],p=p,fold=fold,reverse=reverse,energy=n*(-o['correlations'][1]+row['kappa']*o['correlations'][2]-row['h']*o['mx']),fidelity_ed=float(np.vdot(ed,rho@ed).real),epsilon_c_total=float(max(abs(v[:n]-ved[:n]))),epsilon_sf_total=float(max(abs(v[n:2*n]-ved[n:2*n]))),epsilon_mx_total=float(abs(v[-1]-ved[-1])),prep_joint_pass=row['joint_pass'],seconds=simsec,checks=check,disposition='newly_executed',noise_channels=res['cnots'],**res)
 dump(meta,r);return r

def trajectories(row,p,count=512,seed=2026):
 n=row['n'];s=row['selected'];g=compile_circuit(n,row['ref'],s['words'],s['params']);rng=np.random.default_rng(seed);t=time.perf_counter();vals=[];fids=[];ed=np.load(ROOT/row['archive'])['ed_state']
 for _ in range(count):
  state=evolve(g,n,p,trajectory_rng=rng);vals.append(vector(observations(state,n)));fids.append(abs(np.vdot(ed,state))**2)
 vals=np.array(vals);return dict(mean=vals.mean(0),sem=vals.std(0,ddof=1)/np.sqrt(count),samples=vals,fidelity_ed=np.mean(fids),seconds=time.perf_counter()-t,count=count,seed=seed)
