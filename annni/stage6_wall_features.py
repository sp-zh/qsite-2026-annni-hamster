"""Higher-order wall statistics measured from the existing complete Z bitstrings.
Mean wall count follows C(1); the histogram and adjacency probability do not.
No claim that intermediate wall populations alone establish a floating phase.
"""
from functools import lru_cache
import numpy as np
from .upgrade_gates import geometry,evolve,reference_gates
from .stage6_detector import LABELS
@lru_cache(4)
def wall_geometry(n):
 ids,z,_=geometry(n);dw=(1-z*np.roll(z,-1,axis=1))//2;return dw.sum(1),np.all(dw*np.roll(dw,-1,axis=1)==0,axis=1)
def features(pz,mx,n):
 count,noadj=wall_geometry(n);hist=np.bincount(count,weights=np.asarray(pz),minlength=n+1)[::2]
 return np.r_[hist,np.asarray(pz)@noadj,float(mx)]
def pure_features(state,n):
 from .upgrade_gates import observations
 return features(abs(state)**2,observations(state,n)['mx'],n)
def train(values,labels,n):
 values=np.asarray(values);labels=np.array(labels);centers=[];delta=[]
 for name,ref in zip(LABELS[:3],['ghz','antiphase','plus']):
  x=values[labels==name];c=x.mean(0) if len(x) else pure_features(evolve(reference_gates(n,ref),n),n);centers.append(c);delta.extend(x-c)
 centers.append(features(np.ones(1<<n)/(1<<n),0,n));cov=np.cov(np.array(delta),rowvar=False) if len(delta)>2 else np.eye(values.shape[1])*.01;cov=(cov+cov.T)/2+.01*np.eye(values.shape[1])
 return dict(n=n,centers=np.array(centers).tolist(),precision=np.linalg.inv(cov).tolist(),covariance=cov.tolist(),maximum_distance=5.,minimum_margin=.2,features='Even total-wall-count histogram, probability of no adjacent walls, Mx',measurement='Uses the same Z/X joint counts; no additional settings. SV high-order wall statistics unavailable in the prescribed30/68-setting estimator and never silently projected.',training='Clean independently labelled development ED only')
def predict(v,cfg):
 if not np.isfinite(v).all():return dict(label='uncertain',reason='nonfinite')
 delta=np.array(cfg['centers'])-v;d=np.sqrt(np.maximum(np.einsum('ij,jk,ik->i',delta,cfg['precision'],delta),0));o=np.argsort(d);accepted=d[o[0]]<=cfg['maximum_distance'] and d[o[1]]-d[o[0]]>=cfg['minimum_margin'];return dict(label=LABELS[o[0]] if accepted else 'uncertain',distances=d.tolist(),accepted=bool(accepted))
