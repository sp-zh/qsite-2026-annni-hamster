"""Frozen observable-only diagnostics. Labels are reference resemblance, not phases."""
import numpy as np
from scipy.cluster.vq import kmeans2
from .upgrade_gates import *
def controls(n):
 states=[evolve(reference_gates(n,r),n) for r in ['ghz','antiphase','plus']]
 return np.array([vector(observations(s,n)) for s in states]+[np.r_[1,np.zeros(n-1),np.ones(n)/n,0]])
def train(x,n):
 x=np.array(x);mu=x.mean(0);scale=np.maximum(x.std(0),.05);z=(x-mu)/scale
 _,s,v=np.linalg.svd(z,full_matrices=False);pc=v[:3];scores=z@pc.T
 centers,labels=kmeans2(scores,3,minit='++',seed=2026,iter=100)
 anchor=(controls(n)[:3]-mu)/scale@pc.T
 from scipy.optimize import linear_sum_assignment
 ii,jj=linear_sum_assignment(np.linalg.norm(centers[:,None]-anchor[None,:],axis=-1));mapping=np.empty(3,int);mapping[ii]=jj
 d=np.linalg.norm(scores-centers[labels],axis=1);cut=float(np.quantile(d,.95)*1.25)
 return dict(n=n,mu=mu.tolist(),scale=scale.tolist(),components=pc.tolist(),explained_variance=(s[:3]**2/sum(s**2)).tolist(),centers=centers.tolist(),mapping=mapping.tolist(),max_cluster_distance=cut,margin=.1,training='clean development B3 observations only; no coordinates/p/reference/resources',labels=['ferro-like','antiphase-like','paramagnetic-like','degraded','uncertain'],d1_max_distance=.45,d1_margin=.08)
def predict(v,cfg):
 n=cfg['n'];v=np.asarray(v);ctrl=controls(n)
 # Full C and all SF treated as two equally weighted feature blocks plus Mx.
 delta=v-ctrl;dist=np.sqrt((np.mean(delta[:,:n]**2,axis=1)+np.mean((2*delta[:,n:2*n])**2,axis=1)+delta[:,-1]**2)/3)
 order=np.argsort(dist);d1=int(order[0]) if dist[order[0]]<=cfg['d1_max_distance'] and dist[order[1]]-dist[order[0]]>=cfg['d1_margin'] else 4
 z=(v-np.array(cfg['mu']))/cfg['scale'];pc=z@np.array(cfg['components']).T;dd=np.linalg.norm(pc-np.array(cfg['centers']),axis=1);j=int(np.argmin(dd));d3=int(cfg['mapping'][j]) if dd[j]<=cfg['max_cluster_distance'] else 4
 # The fully mixed control is explicitly distinguishable by low transverse signal.
 if d1==3:d3=3
 return dict(D1=cfg['labels'][d1],D3=cfg['labels'][d3],D1_distances=dist.tolist(),D3_distances=dd.tolist(),full_features=v.tolist())
def uhlmann_squared(a,b):
 # Trace norm ||sqrt(a)sqrt(b)||_1 squared avoids squaring tiny physical eigenvalues.
 roots=[]
 for rho in [a,b]:
  ev,u=np.linalg.eigh((rho+rho.conj().T)/2)
  if ev.min() < -1e-9:raise ValueError('non PSD density')
  ev=np.where(ev<1e-14,0,ev)
  roots.append((u*np.sqrt(np.maximum(ev,0)))@u.conj().T)
 f=float(np.sum(np.linalg.svd(roots[0]@roots[1],compute_uv=False))**2)
 if f>1+1e-7:raise ValueError(f)
 return min(f,1.)

def peak_support_mask(node_quality):
 """A local maximum of interval differences uses its neighbors: four node states."""
 q=np.asarray(node_quality,dtype=bool)
 return np.array([bool(np.all(q[max(0,j-1):min(len(q),j+3)])) for j in range(len(q)-1)])
