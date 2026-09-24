"""Literal per-CNOT target depolarization using PennyLane default.mixed."""
import numpy as np
import pennylane as qml
from .circuits import prepare,observe,resources

def noisy_density(theta,p,n=8):
    dev=qml.device('default.mixed',wires=n,shots=None)
    @qml.qnode(dev)
    def circuit():
        prepare(theta,n,decomposed=True,p=p)
        return qml.state()
    return np.asarray(circuit())

def check_schedule(theta,p,n=8):
    with qml.queuing.AnnotatedQueue() as queue:
        prepare(theta,n,decomposed=True,p=p)
    ops=qml.tape.QuantumScript.from_queue(queue).operations
    cnots=0;channels=0;targets=[0]*n
    for i,op in enumerate(ops):
        if op.name=='CNOT':
            cnots+=1
            channel=ops[i+1]
            assert channel.name=='DepolarizingChannel'
            assert list(channel.wires)==[op.wires[1]]
            assert np.isclose(channel.parameters[0],p)
            targets[op.wires[1]]+=1
        if op.name=='DepolarizingChannel':
            channels+=1
            assert i>0 and ops[i-1].name=='CNOT'
    assert cnots==channels==4*n*len(theta)
    return dict(cnots=cnots,channels=channels,target_counts=targets)

def density_checks(rho,tol=1e-10):
    trace=np.trace(rho)
    hermiticity=float(np.max(abs(rho-rho.conj().T)))
    eig=np.linalg.eigvalsh(rho)
    assert abs(trace-1)<tol and hermiticity<tol
    assert eig.min()>=-tol and eig.max()<=1+tol
    return dict(trace_real=float(trace.real),trace_imag=float(trace.imag),
                hermiticity_error=hermiticity,min_eigenvalue=float(eig.min()),max_eigenvalue=float(eig.max()),
                purity=float(np.trace(rho@rho).real))
