import numpy as np
import pennylane as qml
import pytest
from annni.circuits import HVAEngine,edges,prepare,qnode,observe,resources
from annni.model import Chain

def test_shape_edges_angles():
    assert edges(8)[0]==[(i,(i+1)%8) for i in range(8)]
    assert edges(8)[1]==[(i,(i+2)%8) for i in range(8)]
    with pytest.raises(ValueError): HVAEngine().state(np.zeros(6))
    theta=np.array([[.11,.23,.37]])
    with qml.queuing.AnnotatedQueue() as q: prepare(theta)
    ops=qml.tape.QuantumScript.from_queue(q).operations
    assert len(ops)==32
    assert all(np.isclose(o.parameters[0],.22) for o in ops[8:16])
    assert all(np.isclose(o.parameters[0],.46) for o in ops[16:24])
    assert all(np.isclose(o.parameters[0],.74) for o in ops[24:])
    r=resources(8,2)
    assert r['cnots']==64 and r['channel_count']==64 and r['target_counts']==[8]*8

def test_basis_and_asymmetric_state():
    n=8;c=Chain(n)
    @qml.qnode(qml.device('default.qubit',wires=n))
    def basic():
        qml.PauliX(0);qml.PauliX(5)
        return qml.state()
    state=basic()
    assert np.argmax(abs(state))==132
    np.testing.assert_equal(c.z[132],[-1,1,1,1,1,-1,1,1])
    rng=np.random.default_rng(71)
    state=rng.normal(size=256)+1j*rng.normal(size=256);state/=np.linalg.norm(state)
    @qml.qnode(qml.device('default.qubit',wires=n))
    def asymmetric():
        qml.StatePrep(state,wires=range(n)) # independent convention test only
        return [qml.expval(qml.Z(i)@qml.Z((i+2)%n)) for i in range(n)]
    expected=np.sum(abs(state[:,None])**2*c.z*np.roll(c.z,-2,axis=1),axis=0)
    np.testing.assert_allclose(asymmetric(),expected,atol=1e-12)
    from test_physics import upstream_builder
    matrix=qml.matrix(upstream_builder()(8,.3,.7),wire_order=range(n))
    np.testing.assert_allclose(matrix@state,c.full_matrix(.3,.7)@state,atol=1e-12)

def test_state_symmetry_and_decomposition():
    theta=np.random.default_rng(1).normal(size=(2,3))*.3
    a=HVAEngine().state(theta); b=qnode()(theta); d=qnode(decomposed=True)(theta)
    np.testing.assert_allclose(a,b,atol=1e-12)
    np.testing.assert_allclose(b,d,atol=1e-12)
    assert abs(np.linalg.norm(a)-1)<1e-12
    ids=np.arange(256);shift=((ids<<1)&255)|(ids>>7)
    np.testing.assert_allclose(a,a[shift],atol=1e-12)
    np.testing.assert_allclose(a,a[::-1],atol=1e-12)

def test_analytic_gradient_finite_difference_and_autodiff():
    engine=HVAEngine();x=np.random.default_rng(3).uniform(-.4,.4,6)
    energy,grad=engine.value_grad(x,.3,.7)
    eps=1e-6
    fd=np.array([(engine.value_grad(x+eps*np.eye(6)[i],.3,.7)[0]-
                  engine.value_grad(x-eps*np.eye(6)[i],.3,.7)[0])/(2*eps) for i in range(6)])
    np.testing.assert_allclose(grad,fd,atol=2e-7,rtol=2e-7)
    from test_physics import upstream_builder
    ham=upstream_builder()(8,.3,.7)
    @qml.qnode(qml.device('default.qubit',wires=8),interface='autograd',diff_method='backprop')
    def cost(t):
        prepare(t.reshape((2,3)));return qml.expval(ham)
    qx=qml.numpy.array(x,requires_grad=True)
    np.testing.assert_allclose(qml.grad(cost)(qx),grad,atol=1e-10)
    assert abs(cost(qx)-energy)<1e-11

def test_observables_energy_and_save(tmp_path):
    theta=np.random.default_rng(5).uniform(-.3,.3,(2,3));eng=HVAEngine()
    state=eng.state(theta);obs=observe(state)
    e=eng.value_grad(theta.ravel(),.8,.4)[0]
    assert abs(e-8*(-obs['correlations'][1]+.8*obs['correlations'][2]-.4*obs['mx']))<1e-11
    np.testing.assert_allclose(obs['structure_factor'].sum(),1,atol=1e-12)
    np.savez(tmp_path/'p.npz',params=theta)
    np.testing.assert_allclose(eng.state(np.load(tmp_path/'p.npz')['params']),state,atol=1e-14)

def test_baseline_coordinates_and_basis():
    d=np.load('results/baseline/grid_n8.npz')
    assert np.isnan(d['states'][:,0,:]).all() and np.isnan(d['chi_f'][:,0]).all()
    np.testing.assert_allclose(d['h_mid'],(d['h'][:-1]+d['h'][1:])/2)
    k=int(np.flatnonzero(np.isclose(d['kappa'],.3))[0]);h=7
    psi=d['states'][k,h];c=Chain(8)
    assert np.linalg.norm(c.full_matrix(d['kappa'][k],d['h'][h])@psi-8*d['energy_per_site'][k,h]*psi)<1e-8
    np.testing.assert_allclose(observe(psi)['correlations'],d['correlations'][k,h],atol=1e-12)
