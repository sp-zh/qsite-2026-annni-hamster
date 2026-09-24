import numpy as np
import pennylane as qml
from annni.upgrade_gates import *
from annni.upgrade_adapt import PLAN

def qml_state(gates,n,mixed=False,p=0):
 @qml.qnode(qml.device('default.mixed' if mixed else 'default.qubit',wires=n))
 def circuit():
  for g in gates:
   if g[0]=='CNOT':
    qml.CNOT(wires=g[1:])
    if mixed:qml.DepolarizingChannel(p,wires=g[2])
   elif g[0]=='H':qml.Hadamard(g[1])
   elif g[0]=='X':qml.PauliX(g[1])
   elif g[0]=='RX':qml.RX(g[2],g[1])
   elif g[0]=='RZ':qml.RZ(g[2],g[1])
  return qml.state()
 return circuit()
def test_refs():
 for n in [8,12]:
  for ref,count in [('plus',0),('ghz',n-1),('antiphase',n-2)]:
   g=reference_gates(n,ref);s=evolve(g,n);assert resources(g,n)['cnots']==count
   np.testing.assert_allclose(np.linalg.norm(s),1,atol=1e-12)
   np.testing.assert_allclose(s,s[::-1],atol=1e-12)
   ids=np.arange(1<<n);shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1));np.testing.assert_allclose(s,s[shift],atol=1e-12)
   if ref=='antiphase':
    assert np.sum(abs(s)>.1)==4;np.testing.assert_allclose(s[abs(s)>.1],.5)
    np.testing.assert_allclose(observations(s,n)['structure_factor'][n//4],.5)
def test_rotation_and_pool():
 rng=np.random.default_rng(4);s=rng.normal(size=256)+1j*rng.normal(size=256);s/=np.linalg.norm(s)
 for w in pool(8,True):
  np.testing.assert_allclose(apply_pauli(apply_pauli(s,w),w),s)
  np.testing.assert_allclose(apply_pauli(s[::-1],w),apply_pauli(s,w)[::-1])
  np.testing.assert_allclose(evolve(pauli_gates(w,.37),8,rho=s),rotate(s,w,.37),atol=1e-12)
  for g in pauli_gates(w,.37):
   if g[0]=='CNOT':assert (g[1]-g[2])%8 in (1,2,6,7)
def test_gradient():
 words=pool(8,True)[::7];params=np.random.default_rng(2).normal(size=len(words))*.1
 e,g,s=state_and_grad(params,words,8,'antiphase',.8,.5)
 for j in [0,3,len(words)-1]:
  a=params.copy();b=params.copy();a[j]+=1e-6;b[j]-=1e-6
  fd=(state_and_grad(a,words,8,'antiphase',.8,.5)[0]-state_and_grad(b,words,8,'antiphase',.8,.5)[0])/2e-6
  np.testing.assert_allclose(g[j],fd,atol=2e-8)
def test_density_and_folding():
 words=pool(8)[:3];g=compile_circuit(8,'ghz',words,[.1,-.23,.4]);s=evolve(g,8)
 np.testing.assert_allclose(s,qml_state(g,8),atol=1e-12)
 for p in [0,.01,.05]:
  rho=density(g,8,p);np.testing.assert_allclose(rho,qml_state(g,8,True,p),atol=1e-11)
  assert abs(np.trace(rho)-1)<1e-12;assert np.linalg.eigvalsh(rho).min()>-1e-12
  if p==0:np.testing.assert_allclose(rho,np.outer(s,s.conj()),atol=1e-12)
 for f in [3,5]:
  gg=compile_circuit(8,'ghz',words,[.1,-.23,.4],fold=f)
  assert resources(gg,8)['cnots']==f*resources(g,8)['cnots'];np.testing.assert_allclose(evolve(gg,8),s,atol=1e-12)
def test_bit_order_energy():
 from annni.model import Chain
 chain=Chain(8);s=np.zeros(256,complex);s[128]=1
 assert observations(s,8)['correlations'][0]==1
 s=np.random.default_rng(12).normal(size=256)+1j*np.random.default_rng(13).normal(size=256);s/=np.linalg.norm(s)
 np.testing.assert_allclose(h_action(s,8,.3,.7),chain.full_matrix(.3,.7)@s,atol=1e-12)
 o=observations(s,8);np.testing.assert_allclose(np.vdot(s,h_action(s,8,.3,.7)).real,8*(-o['correlations'][1]+.3*o['correlations'][2]-.7*o['mx']))
 np.testing.assert_allclose(sum(o['structure_factor']),1)
def test_heldout_frozen():
 assert len(PLAN['held_out'])>=48
 assert not set(map(tuple,PLAN['held_out']))&set(map(tuple,PLAN['development']+PLAN['final_map']+PLAN['validation']))
