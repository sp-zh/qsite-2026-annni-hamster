import numpy as np
from annni.circuits import HVAEngine,observe,qnode
from annni.noise import noisy_density,check_schedule,density_checks
import pennylane as qml

def test_zero_noise_density_and_schedule():
    theta=np.random.default_rng(17).uniform(-.3,.3,(1,3))
    psi=HVAEngine().state(theta)
    rho=noisy_density(theta,0)
    np.testing.assert_allclose(rho,np.outer(psi,psi.conj()),atol=1e-11)
    a,b=observe(psi),observe(rho)
    for key in a:np.testing.assert_allclose(a[key],b[key],atol=1e-11)
    schedule=check_schedule(theta,.05)
    assert schedule['cnots']==32 and schedule['target_counts']==[4]*8
    density_checks(rho)

def test_channel_definition_and_noisy_psd():
    dev=qml.device('default.mixed',wires=1)
    psi=np.array([np.sqrt(.3),1j*np.sqrt(.7)])
    @qml.qnode(dev)
    def single(p):
        qml.StatePrep(psi,wires=[0]);qml.DepolarizingChannel(p,wires=0)
        return qml.state()
    rho=np.outer(psi,psi.conj());p=.05
    matrices=[qml.matrix(qml.X(0)),qml.matrix(qml.Y(0)),qml.matrix(qml.Z(0))]
    exact=(1-p)*rho+p/3*sum(m@rho@m for m in matrices)
    np.testing.assert_allclose(single(p),exact,atol=1e-12)
    noisy=noisy_density(np.array([[.1,.2,.3]]),.05)
    check=density_checks(noisy)
    assert check['purity']<1
