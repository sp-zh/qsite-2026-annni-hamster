import numpy as np
from annni.stage5_selection import translate,symmetry
from annni.stage5_baseline_selectors import choose
from annni.upgrade_gates import h_action
from annni.model import Chain

def test_translation_and_parity_algebra():
 n=6;I=np.eye(64,dtype=complex);T=np.column_stack([translate(v,n) for v in I]);P=I[::-1];Q=sum(np.linalg.matrix_power(T,r) for r in range(n))/n;H=Chain(n).full_matrix(.3,.7).toarray()
 J=(Q+P@Q)/2
 for a,b in [(J@J,J),(J.conj().T,J),(P@P,I),(np.linalg.matrix_power(T,n),I),(Q.conj().T,Q),(Q@Q,Q),(T@P,P@T),(T@H,H@T),(P@H,H@P)]:np.testing.assert_allclose(a,b,atol=1e-12)

def test_nonzero_momentum_counterexample():
 n=6;v=np.zeros(64,dtype=complex);v[1]=1;s=sum((-1)**r*translate(v,n,r) for r in range(n));s=(s+s[::-1]);s/=np.linalg.norm(s);m=symmetry(s,n,.3,.7);assert abs(m['T_real']+1)<1e-12 and abs(m['w0'])<1e-12 and abs(m['w_plus']-1)<1e-12

def test_same_sector_excited_counterexample():
 n=6;I=np.eye(64,dtype=complex);Q=sum(np.column_stack([translate(v,n,r) for v in I]) for r in range(n))/n;Q=(Q+Q[::-1])/2;e,U=np.linalg.eigh(Q);B=U[:,e>.9];H=Chain(n).full_matrix(.3,.7).toarray();e,U=np.linalg.eigh(B.conj().T@H@B);s=B@U[:,1];m=symmetry(s,n,.3,.7);assert m['w0']>.999 and m['w_plus']>.999 and abs(m['variance'])<1e-10 and abs(np.vdot(s,B@U[:,0]))<1e-10

def test_selector_units_and_oracle_independence():
 a=dict(n=8,energy=-8,cnots=32,variance=.001,w0=1,w_plus=1,ref='a',seed=11);b=a|dict(energy=-7.9996,cnots=31,w0=.5)
 assert choose([a,b],'S0')['candidate']['cnots']==31
 assert choose([a,b],'S1')['candidate']['cnots']==32
 cfg=dict(w0_min=.99,parity_min=.999999,energy_tolerance_per_site=1e-8)
 assert choose([a,b],'S2',cfg)['candidate']['cnots']==32
 assert choose([b],'S2',cfg)['selection_unresolved']
 assert choose([a|{'fidelity':0},b|{'fidelity':1}],'S2',cfg)['candidate']['cnots']==32

def test_unique_positive_field_ground_symmetry():
 for k,h in [(0,.2),(.975,.15),(.8,.5)]:
  s=Chain(8).ground_state(k,h).state;m=symmetry(s,8,k,h);assert m['w0']>1-1e-10 and m['w_plus']>1-1e-10

def test_hva_literal_mapping_and_measurement_statistics():
 from annni.stage5_e2e import hva_gates
 from annni.circuits import HVAEngine
 from annni.upgrade_gates import evolve,density,vector,observations,resources
 from annni.upgrade_mitigation import groups,estimated_vector
 n=8;theta=np.random.default_rng(151).normal(0,.12,(2,3));g=hva_gates(theta,n);s=evolve(g,n)
 np.testing.assert_allclose(s,HVAEngine(n).state(theta),atol=1e-12)
 assert resources(g,n)['cnots']==4*n*2
 rho=density(g,n,0);np.testing.assert_allclose(rho,np.outer(s,s.conj()),atol=1e-12)
 v,den=estimated_vector(groups(rho),n,True);np.testing.assert_allclose(v,vector(observations(s,n)),atol=1e-11);assert abs(den-2)<1e-11

def test_selection_does_not_modify_state():
 from copy import deepcopy
 a=dict(n=8,energy=-8,cnots=32,variance=.001,w0=1,w_plus=1,ref='a',seed=11,params=[.1,.2],words=['YZIIIIII'])
 saved=deepcopy(a);choose([a],'S2',dict(w0_min=.99,parity_min=.999999,energy_tolerance_per_site=1e-6));assert a==saved

def test_folding_and_periodic_connectivity():
 from annni.upgrade_gates import pool,compile_circuit,evolve
 n=8;words=pool(n,True)[::7];params=np.linspace(.01,.12,len(words));g=compile_circuit(n,'antiphase',words,params)
 for gate in g:
  if gate[0]=='CNOT':assert min((gate[1]-gate[2])%n,(gate[2]-gate[1])%n)<=2
 for scale in [3,5]:np.testing.assert_allclose(evolve(compile_circuit(n,'antiphase',words,params,scale),n),evolve(g,n),atol=1e-11)

def test_parity_verification_does_not_fix_momentum():
 from annni.upgrade_mitigation import groups,estimated_vector
 from annni.upgrade_gates import observations,vector
 n=6;v=np.zeros(64,dtype=complex);v[1]=1;s=sum((-1)**r*translate(v,n,r) for r in range(n));s+=s[::-1];s/=np.linalg.norm(s)
 out,den=estimated_vector(groups(np.outer(s,s.conj())),n,True);np.testing.assert_allclose(out,vector(observations(s,n)),atol=1e-12);assert abs(den-2)<1e-12 and symmetry(s,n,.3,.7)['w0']<1e-10

def test_new_test_unsealed_after_freeze_and_no_overlap():
 import json
 from annni.stage5_adapt import OUT,PLAN,sha
 f=json.loads((OUT/'selector_frozen.json').read_text());u=json.loads((OUT/'selector_benchmark/test/unsealed.json').read_text());assert u['timestamp']>f['timestamp'] and u['freeze_sha']==sha(OUT/'selector_frozen.json')
 sets=[set(map(tuple,PLAN[x])) for x in ['validation_v2','test_v2','n12_test_v2']]
 assert list(map(len,sets))==[24,72,24]
 assert all(not a&b for i,a in enumerate(sets) for b in sets[i+1:])
 assert not set.union(*sets)&set(map(tuple,PLAN['final_map']+PLAN['held_out']+PLAN['development']+PLAN['validation']))

def test_n12_frozen_detector_controls_and_dimensions():
 import json
 from annni.stage5_adapt import OUT
 from annni.upgrade_detection import predict,controls
 cfg=json.loads((OUT/'n12_scaling/detection_frozen.json').read_text());assert cfg['n']==12 and len(cfg['mu'])==25
 result=[predict(v,cfg) for v in controls(12)];assert [r['D1'] for r in result]==['ferro-like','antiphase-like','paramagnetic-like','degraded'];assert result[-1]['D3']=='degraded'


def test_s0_same_resource_ties_follow_historical_energy():
 a=dict(n=8,energy=-8,cnots=32,variance=.01,w0=1,w_plus=1,ref='a',seed=11);b=a|dict(ref='b',energy=-7.9999,variance=.00001)
 assert choose([a,b],'S0')['candidate']['ref']=='a'


def test_s1_requires_only_energy_resource_fields():
 a=dict(n=8,energy=-8.,cnots=32);b=dict(n=8,energy=-8.+1e-11,cnots=32)
 assert choose([a,b],'S1')['candidate'] is a


def test_n12_energy_gradient_for_extended_pool():
 from annni.upgrade_gates import pool,state_and_grad
 n=12;ops=pool(n,True);words=[ops[0],ops[len(ops)//2],ops[-1]];theta=np.array([-.17,.08,.24]);eps=1e-6
 for ref in ['plus','antiphase']:
  energy,grad,state=state_and_grad(theta,words,n,ref,.8,.5)
  fd=[]
  for j in range(len(theta)):
   shift=np.eye(len(theta))[j]*eps
   fd.append((state_and_grad(theta+shift,words,n,ref,.8,.5)[0]-state_and_grad(theta-shift,words,n,ref,.8,.5)[0])/(2*eps))
  np.testing.assert_allclose(grad,fd,atol=2e-7,rtol=2e-6)
  assert abs(np.vdot(state,state)-1)<1e-11


def test_hva_cache_keys_keep_fractional_field_and_protocol():
 import json,hashlib
 from pathlib import Path
 from annni.stage5_hva_baseline import key_for
 keys=[key_for(.3,h) for h in [.3125,.325,.3375,1.3125]]
 ids=[hashlib.sha256(json.dumps(k,sort_keys=True).encode()).hexdigest() for k in keys]
 assert len(set(ids))==4
 assert all(Path(x).with_suffix('.npz').stem==x for x in ids)
 assert all(k['layers']==6 and k['seeds']==[11,23,37] and k['optimizer']['maxiter']==400 for k in keys)

def test_reused_x_basis_joint_measurements_match_literal_settings():
 from annni.stage5_measurement_groups import groups as reused
 from annni.upgrade_mitigation import groups as original
 rng=np.random.default_rng(51902)
 for n in [3,4,8]:
  a=rng.normal(size=(2**n,3))+1j*rng.normal(size=(2**n,3));rho=a@a.conj().T;rho/=np.trace(rho)
  before=rho.copy();old=original(rho);new=reused(rho)
  assert list(old)==list(new)
  for key in old:np.testing.assert_allclose(new[key],old[key],atol=2e-14,rtol=2e-13)
  np.testing.assert_array_equal(rho,before)
