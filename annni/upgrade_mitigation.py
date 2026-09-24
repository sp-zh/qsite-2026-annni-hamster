"""ZNE and measurable global-X verification, with joint-bitstring shot samples."""
import numpy as np
from .upgrade_gates import *
LINEAR=np.linalg.pinv(np.column_stack([np.ones(3),[1,3,5]]))[0]
RICHARDSON=np.array([15/8,-5/4,3/8])
def measurement_probs(rho,basis):
 n=len(basis);r=rho.copy()
 for i,b in enumerate(basis):
  if b=='Z':continue
  u=H if b=='X' else matrix(('RX',i,np.pi/2))
  r=one_axis(r,u,i,n);r=one_axis(r,u.conj(),i,n,n)
 probs=r.diagonal().real
 assert probs.min()>-1e-10
 probs=np.maximum(probs,0);return probs/probs.sum()
def groups(rho):
 n=int(np.log2(len(rho)));out={'Z'*n:measurement_probs(rho,'Z'*n),'X'*n:measurement_probs(rho,'X'*n)}
 for i in range(n):
  for j in range(i+1,n):
   basis=['X']*n;basis[i]=basis[j]='Y';w=''.join(basis);out[w]=measurement_probs(rho,w)
 return out

def estimated_vector(distributions,n,sv=False):
 _,z,_=geometry(n);pz=distributions['Z'*n];px=distributions['X'*n];pair=z.T@(pz[:,None]*z);mx=(px@z).mean()
 if sv:
  parity=np.prod(z,axis=1);P=float(px@parity);denom=1+P
  if denom<=.05:return np.full(2*n+1,np.nan),denom
  op=np.eye(n)*P
  for i in range(n):
   for j in range(i+1,n):
    w=['X']*n;w[i]=w[j]='Y';op[i,j]=op[j,i]=-float(distributions[''.join(w)]@parity)
  pair=(pair+op)/denom;mx=(mx+np.mean(px@(parity[:,None]*z)))/denom
 else:denom=1.
 c=np.array([sum(pair[i,(i+r)%n] for i in range(n))/n for r in range(n)])
 return np.r_[c,np.fft.fft(c).real/n,mx],denom

def sample_estimate(distributions,n,budget,rng,sv=False):
 keys=list(distributions) if sv else ['Z'*n,'X'*n];alloc=np.full(len(keys),budget//len(keys));alloc[:budget%len(keys)]+=1
 sampled={k:rng.multinomial(int(count),distributions[k])/count for k,count in zip(keys,alloc)}
 # Multinomial counts are sufficient statistics of whole joint bitstrings;
 # all correlations and parity from a group share the same counts.
 v,d=estimated_vector(sampled,n,sv)
 return v,dict(shots=int(sum(alloc)),groups=len(keys),allocations=alloc.tolist(),denominator=float(d))
def algebra_check(rho):
 n=int(np.log2(len(rho)));P=np.eye(1<<n)[::-1];proj=(np.eye(1<<n)+P)/2;r=proj@rho@proj;r/=np.trace(r)
 v,den=estimated_vector(groups(rho),n,True)
 np.testing.assert_allclose(v,vector(observations(r,n)),atol=2e-11)
 return float(den)
