"""Explicit wire-0-MSB gate tables and local Pauli rotations; no state projection.
Rotation exp(-i theta P): X->H, Y->RX(pi/2), parity CNOT ladder,
RZ(2 theta) on last support wire, reverse ladder, inverse basis gates.
Every literal CNOT is followed by target-only D_p, including reference/folding.
"""
from functools import lru_cache
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigsh
H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
X=np.array([[0,1],[1,0]],complex)
Y=np.array([[0,-1j],[1j,0]],complex)
Z=np.diag([1,-1]).astype(complex)
@lru_cache(None)
def geometry(n):
 ids=np.arange(1<<n);z=1-2*((ids[:,None]>>np.arange(n-1,-1,-1))&1)
 return ids,z,[ids^(1<<(n-1-i)) for i in range(n)]
def reference_gates(n,ref):
 if ref=='plus':return [('H',i) for i in range(n)]
 if ref=='ghz':return [('H',0)]+[('CNOT',i-1,i) for i in range(1,n)]
 if ref=='antiphase':
  assert n%4==0
  return [('H',0),('H',1)]+[g for i in range(2,n) for g in [('CNOT',i-2,i),('X',i)]]
 if ref=='zero':return []
 if ref=='0011':return [('X',i) for i in range(n) if i%4>=2]
 raise ValueError(ref)
def pauli_gates(word,theta,reverse=False):
 support=[i for i,p in enumerate(word) if p!='I']
 if reverse:support=support[::-1]
 assert support
 before=[('H',i) if word[i]=='X' else ('RX',i,np.pi/2) for i in support if word[i]!='Z']
 after=[('H',i) if word[i]=='X' else ('RX',i,-np.pi/2) for i in support[::-1] if word[i]!='Z']
 ladder=[('CNOT',i,j) for i,j in zip(support[:-1],support[1:])]
 return before+ladder+[('RZ',support[-1],2*float(theta))]+ladder[::-1]+after

def compile_circuit(n,ref,words,params,fold=1,reverse=False):
 assert len(words)==len(params) and fold in (1,3,5)
 gates=reference_gates(n,ref)
 for w,t in zip(words,params):gates+=pauli_gates(w,t,reverse)
 # Pauli supports stored in ascending index can create long periodic-edge ladders for triples.
 # Pair wrap is still NN/NNN; triples are reordered separately in pool below if needed.
 return [g for gate in gates for g in ([gate]*fold if gate[0]=='CNOT' else [gate])]

def resources(gates,n):
 levels=[0]*n;targets=[0]*n;order=[]
 for g in gates:
  wires=g[1:3] if g[0]=='CNOT' else [g[1]]
  d=max(levels[i] for i in wires)+1
  for i in wires:levels[i]=d
  if g[0]=='CNOT':targets[g[2]]+=1;order.append([g[1],g[2]])
 return dict(cnots=len(order),gate_count=len(gates),unitary_depth=max(levels),target_counts=targets,cnot_order=order)
def matrix(g):
 if g[0]=='H':return H
 if g[0]=='X':return X
 if g[0] in ('RX','RZ'):
  p=X if g[0]=='RX' else Z
  return np.cos(g[2]/2)*np.eye(2)-1j*np.sin(g[2]/2)*p
 raise ValueError(g)
def one_axis(a,u,wire,n,axis_offset=0):
 shape=a.shape; b=a.reshape((2,)*(n*(2 if a.ndim==2 else 1)))
 axis=wire+axis_offset
 b=np.moveaxis(b,axis,0);b=np.einsum('ab,b...->a...',u,b,optimize=False)
 return np.moveaxis(b,0,axis).reshape(shape)
def evolve(gates,n,p=0.,rho=None,trajectory_rng=None,injection=None):
 ids,z,flips=geometry(n)
 if rho is None:
  rho=np.zeros(1<<n,complex);rho[0]=1
 elif rho.ndim==2:rho=rho.copy()
 mixed=rho.ndim==2; cnot_index=0
 for g in gates:
  if g[0]=='CNOT':
   control,target=g[1:];perm=ids^(((ids>>(n-1-control))&1)<<(n-1-target))
   rho=rho[np.ix_(perm,perm)] if mixed else rho[perm]
   if mixed and p:
    f=flips[target];s=z[:,target];r=rho[np.ix_(f,f)]
    rho=(1-p)*rho+p/3*(r+s[:,None]*r*s[None,:]+s[:,None]*rho*s[None,:])
   elif trajectory_rng is not None and p:
    a=trajectory_rng.choice(4,p=[1-p,p/3,p/3,p/3])
    if a:rho=one_axis(rho,[None,X,Y,Z][a],target,n)
   if injection is not None and cnot_index==injection[0]:rho=one_axis(rho,[X,Y,Z][injection[1]],target,n)
   cnot_index+=1
  else:
   u=matrix(g);rho=one_axis(rho,u,g[1],n)
   if mixed:rho=one_axis(rho,u.conj(),g[1],n,n)
 return rho

def density(gates,n,p):
 a=np.zeros((1<<n,1<<n),complex);a[0,0]=1
 return evolve(gates,n,p,a)
@lru_cache(2048)
def pauli_map(word):
 n=len(word);ids,z,flips=geometry(n);perm=ids.copy();phase=np.ones(len(ids),complex)
 # output at flipped index = phase(input)*input
 for i,p in enumerate(word):
  if p in 'XY':perm=perm^(1<<(n-1-i))
  if p=='Y':phase*=1j*z[:,i]
  if p=='Z':phase*=z[:,i]
 return perm,phase

def apply_pauli(state,word):
 perm,phase=pauli_map(word)
 return phase[perm]*state[perm]
def rotate(state,word,theta):return np.cos(theta)*state-1j*np.sin(theta)*apply_pauli(state,word)
def pool(n,extended=False):
 words=[]
 for d in (1,2):
  for i in range(n):
   for pair in ('YZ','ZY'):
    a=['I']*n;a[i]=pair[0];a[(i+d)%n]=pair[1];words.append(''.join(a))
 if extended:
  for i in range(n):
   for triple in ('YXZ','ZXY'):
    a=['I']*n
    for j,p in enumerate(triple):a[(i+j)%n]=p
    words.append(''.join(a))
 return list(dict.fromkeys(words))
@lru_cache(16)
def diagonals(n,bc='periodic'):
 ids,z,flips=geometry(n)
 nn=sum(z[:,i]*z[:,(i+1)%n] for i in range(n if bc=='periodic' else n-1))
 nnn=sum(z[:,i]*z[:,(i+2)%n] for i in range(n if bc=='periodic' else n-2))
 c=np.array([np.mean(z*np.roll(z,-r,axis=1),axis=1) for r in range(n)])
 return nn,nnn,c

def h_action(s,n,k,h,bc='periodic'):
 nn,nnn,_=diagonals(n,bc);_,_,flips=geometry(n)
 return (-nn+k*nnn)*s-h*sum(s[f] for f in flips)
def observations(s,n):
 ids,z,flips=geometry(n);_,_,c=diagonals(n)
 if s.ndim==1:prob=abs(s)**2;mx=sum(np.vdot(s,s[f]).real for f in flips)/n
 else:prob=s.diagonal().real;mx=sum(np.sum(s[ids,f]).real for f in flips)/n
 corr=c@prob
 return dict(correlations=corr,structure_factor=np.fft.fft(corr).real/n,mx=float(mx))
def vector(obs):return np.r_[obs['correlations'],obs['structure_factor'],obs['mx']]
def state_and_grad(params,words,n,ref,k,h):
 state=evolve(reference_gates(n,ref),n);states=[]
 for t,w in zip(params,words):state=rotate(state,w,t);states.append(state)
 adj=h_action(state,n,k,h);energy=float(np.vdot(state,adj).real);gr=np.empty(len(words))
 for j in range(len(words)-1,-1,-1):
  gr[j]=2*np.vdot(adj,-1j*apply_pauli(states[j],words[j])).real
  adj=rotate(adj,words[j],-params[j])
 return energy,gr,state
