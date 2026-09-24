"""HVA: |+> then NN ZZ, NNN ZZ, X per layer; MSB wire 0.
IsingZZ(2a)=exp(-ia ZiZj), RX(2b)=exp(-ib Xi).
All-to-all logical connectivity for these ring couplings; no SWAP routing.
Compilation preserves source edge order, no cancellation/fusion in resource counts.
"""
import numpy as np
import pennylane as qml
from .model import Chain

def edges(n):
    if n < 5:
        raise ValueError("N>=5 required")
    return ([(i,(i+1)%n) for i in range(n)],
            [(i,(i+2)%n) for i in range(n)])

def validate(theta):
    if len(np.shape(theta)) != 2 or np.shape(theta)[1]!=3 or np.shape(theta)[0]<1:
        raise ValueError("theta must have shape (L,3), L>=1: gamma,eta,beta")

def prepare(theta,n=8,decomposed=False,p=None):
    validate(theta)
    if p is not None and (not decomposed or not 0<=p<=1):
        raise ValueError("Noise requires explicit CNOT decomposition and 0<=p<=1")
    nn,nnn=edges(n)
    for i in range(n):
        qml.Hadamard(i)
    for gamma,eta,beta in theta:
        for angle,pairs in [(gamma,nn),(eta,nnn)]:
            for control,target in pairs:
                if decomposed:
                    qml.CNOT([control,target])
                    if p is not None: qml.DepolarizingChannel(p,target)
                    qml.RZ(2*angle,target)
                    qml.CNOT([control,target])
                    if p is not None: qml.DepolarizingChannel(p,target)
                else:
                    qml.IsingZZ(2*angle,[control,target])
        for i in range(n):
            qml.RX(2*beta,i)

def qnode(n=8,decomposed=False,mixed=False,p=None):
    dev=qml.device('default.mixed' if mixed else 'default.qubit',wires=n,shots=None)
    @qml.qnode(dev,interface='autograd',diff_method='backprop')
    def circuit(theta):
        prepare(theta,n,decomposed,p)
        return qml.state()
    return circuit

def resources(n,L):
    theta=np.zeros((L,3))
    with qml.queuing.AnnotatedQueue() as queue:
        prepare(theta,n,True,p=0.)
    ops=qml.tape.QuantumScript.from_queue(queue).operations
    clocks=np.zeros(n,dtype=int); unitary_clocks=clocks.copy()
    cnots=[]; targets=np.zeros(n,dtype=int); counts={}
    for op in ops:
        wires=list(op.wires)
        counts[op.name]=counts.get(op.name,0)+1
        depth=1+max(clocks[w] for w in wires)
        for w in wires: clocks[w]=depth
        if op.name!='DepolarizingChannel':
            depth=1+max(unitary_clocks[w] for w in wires)
            for w in wires: unitary_clocks[w]=depth
        if op.name=='CNOT':
            cnots.append(wires); targets[wires[1]]+=1
    return dict(n=n,layers=L,parameters=3*L,high_level_gates=n+3*n*L,
                compiled_unitary_gates=n+7*n*L,cnots=len(cnots),
                unitary_depth=int(unitary_clocks.max()),depth_with_channels=int(clocks.max()),
                channel_count=counts['DepolarizingChannel'],target_counts=targets.tolist(),
                gate_counts=counts,cnot_order=cnots,nn_edges=edges(n)[0],nnn_edges=edges(n)[1])

def observe(state,n=8):
    """Pure vector or density matrix; no symmetry projection or renormalization."""
    chain=Chain(n)
    rho=np.asarray(state)
    if rho.ndim==1:
        prob=np.abs(rho)**2
        mx=sum(np.vdot(rho,rho[chain.indices^(1<<i)]).real for i in range(n))/n
    elif rho.shape==(1<<n,1<<n):
        prob=np.diag(rho).real
        mx=sum(rho[chain.indices,chain.indices^(1<<i)].sum().real for i in range(n))/n
    else:
        raise ValueError("state shape mismatch")
    c=chain.correlation_diagonals@prob
    sf=np.fft.fft(c).real/n
    return dict(correlations=c,structure_factor=sf,mx=float(mx))

class HVAEngine:
    """Exact fused statevector evolution with analytic adjoint gradient.

    Fusion is only a simulator optimization: each commuting family uses its
    sum generator. It implements exactly prepare(), not a different ansatz.
    Optimization never accesses ED states and never projects output states.
    """
    def __init__(self,n=8):
        self.n=n; self.chain=Chain(n); self.dim=1<<n
        self.generators=[self.chain.nn,self.chain.nnn]
        self.flips=np.stack([self.chain.indices^(1<<i) for i in range(n)])
        self.plus=np.ones(self.dim,dtype=complex)/np.sqrt(self.dim)

    def x_rotate(self,v,beta):
        # Apply exp(-i beta X) to each qubit using MSB-compatible bit masks.
        c,s=np.cos(beta),-1j*np.sin(beta)
        for flip in self.flips:
            v=c*v+s*v[flip]
        return v

    def generator(self,v,kind):
        return self.generators[kind]*v if kind<2 else v[self.flips].sum(axis=0)

    def evolve(self,v,angle,kind):
        return np.exp(-1j*angle*self.generators[kind])*v if kind<2 else self.x_rotate(v,angle)

    def state(self,theta):
        validate(theta)
        state=self.plus.copy()
        for i,angle in enumerate(np.asarray(theta).ravel()):
            state=self.evolve(state,angle,i%3)
        return state

    def value_grad(self,flat,kappa,h):
        if len(flat)%3 or len(flat)==0: raise ValueError("parameter length")
        states=[]; state=self.plus.copy()
        for i,angle in enumerate(flat):
            state=self.evolve(state,angle,i%3); states.append(state)
        adj=(-self.chain.nn+kappa*self.chain.nnn)*state-h*state[self.flips].sum(axis=0)
        value=float(np.vdot(state,adj).real); grad=np.empty(len(flat))
        for i in range(len(flat)-1,-1,-1):
            grad[i]=2*np.vdot(adj,-1j*self.generator(states[i],i%3)).real
            adj=self.evolve(adj,-flat[i],i%3)
        return value,grad
