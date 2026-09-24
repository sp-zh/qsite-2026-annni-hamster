import numpy as np
import pytest
from annni.stage3 import dense_literal
from annni.circuits import HVAEngine,qnode,observe,resources
from annni.noise import noisy_density,density_checks,check_schedule

@pytest.mark.parametrize('L,p',[(2,0),(2,.01),(4,.05),(6,.01)])
def test_literal_full_density_against_pennylane(L,p):
    theta=np.random.default_rng(101+L).uniform(-.5,.5,(L,3))
    a=dense_literal(theta,p);b=noisy_density(theta,p)
    np.testing.assert_allclose(a,b,atol=2e-11)
    density_checks(a)
    schedule=check_schedule(theta,p)
    assert schedule['cnots']==resources(8,L)['cnots']==32*L
    if p==0:
        s=HVAEngine().state(theta)
        np.testing.assert_allclose(a,np.outer(s,s.conj()),atol=1e-12)
    else:
        # Gate-local noise is not projected into pure-state even parity sector.
        ids=np.arange(256)
        parity=np.trace(a[:,ids[::-1]]).real
        assert abs(parity)<.99999

def test_gradient_near_optimum_and_mixed_control():
    d=np.load('results/calibration_v1/runs/p06_L6_s23.npz')
    theta=d['final_params'];x=theta.ravel();eng=HVAEngine()
    np.testing.assert_allclose(eng.state(theta),qnode()(theta),atol=1e-11)
    e,g=eng.value_grad(x,.3,.4)
    for i in [0,5,17]:
        step=np.zeros_like(x);step[i]=1e-6
        fd=(eng.value_grad(x+step,.3,.4)[0]-eng.value_grad(x-step,.3,.4)[0])/2e-6
        assert abs(fd-g[i])<2e-7
    rho=np.eye(256)/256;o=observe(rho);checks=density_checks(rho)
    assert checks['purity']==1/256 and o['mx']==0
    np.testing.assert_allclose(o['correlations'],[1]+[0]*7,atol=1e-12)
    np.testing.assert_allclose(o['structure_factor'],np.ones(8)/8,atol=1e-12)

def test_actual_optimized_noisy_parameters():
    t=np.load('results/calibration_v1/runs/p06_L6_s23.npz')['final_params']
    a=dense_literal(t,.05);b=noisy_density(t,.05)
    np.testing.assert_allclose(a,b,atol=2e-11)
