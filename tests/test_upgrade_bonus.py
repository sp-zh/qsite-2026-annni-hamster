import numpy as np
from annni.upgrade_gates import *
from annni.upgrade_mitigation import *
from annni.upgrade_detection import uhlmann_squared
from annni.upgrade_dynamics import trotter_gates
from annni.model import Chain
from scipy.sparse.linalg import expm_multiply

def test_sv_and_joint_sampling():
 g=compile_circuit(8,'antiphase',pool(8)[:2],[.2,.3]);rho=density(g,8,.05);algebra_check(rho)
 d=groups(rho);v,c=sample_estimate(d,8,10000,np.random.default_rng(22),True)
 assert c['shots']==10000 and c['groups']==30;assert len(v)==17
 # The same Z bitstring covariance gives exactly C(r)==C(N-r).
 v,_=sample_estimate(d,8,10000,np.random.default_rng(23),False);np.testing.assert_allclose(v[1:8],v[7:0:-1],atol=1e-14)
def test_uhlmann_pure_limit():
 a=evolve(compile_circuit(8,'ghz',pool(8)[:2],[.2,.3]),8);b=evolve(compile_circuit(8,'ghz',pool(8)[:2],[.3,.4]),8)
 np.testing.assert_allclose(uhlmann_squared(np.outer(a,a.conj()),np.outer(b,b.conj())),abs(np.vdot(a,b))**2,atol=1e-9)
 rho=density(compile_circuit(8,'ghz',pool(8)[:2],[.2,.3]),8,.05);np.testing.assert_allclose(uhlmann_squared(rho,rho),1,atol=1e-8)
def test_trajectory():
 n=8;g=compile_circuit(n,'ghz',pool(n)[:1],[.2]);p=.05;exact=vector(observations(density(g,n,p),n));rng=np.random.default_rng(22);vals=np.array([vector(observations(evolve(g,n,p,trajectory_rng=rng),n)) for _ in range(2048)])
 assert np.max(abs(vals.mean(0)-exact)/(vals.std(0,ddof=1)/np.sqrt(len(vals))+1e-10))<5
 assert np.max(abs(vals.mean(0)-exact))<.06

def test_trotter_second_order():
 s=evolve(reference_gates(8,'0011'),8);ex=expm_multiply(-1j*.2*Chain(8).full_matrix(.8,.5),s);err=[]
 for dt in [.2,.1,.05]:
  a=s.copy()
  for _ in range(round(.2/dt)):a=evolve(trotter_gates(8,.8,.5,dt),8,rho=a)
  err.append(np.linalg.norm(a-ex))
 assert err[0]/err[1]>3.5 and err[1]/err[2]>3.5
 assert resources(trotter_gates(8,.8,.5,.1),8)['cnots']==32

def test_reverse_compile():
 for w in pool(8,True):
  a=evolve(reference_gates(8,'plus')+pauli_gates(w,.23),8);b=evolve(reference_gates(8,'plus')+pauli_gates(w,.23,True),8);np.testing.assert_allclose(a,b,atol=1e-12)

def test_peak_support_uses_neighbor_states():
 from annni.upgrade_detection import peak_support_mask
 quality=np.ones(10,bool);quality[4]=False;mask=peak_support_mask(quality)
 assert np.array_equal(np.flatnonzero(~mask),[2,3,4,5])
