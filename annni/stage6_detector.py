"""Observable-only covariance metric with no duplicated C/SF block.
Training uses independent development reference labels. Unknown points may reject.
No coordinates, p, reference identifiers, resources or exact states enter predict.
"""
from .stage6_diagnostics import independent_features
from .upgrade_detection import controls
import numpy as np
LABELS=['ferro-like','antiphase-like','paramagnetic-like','degraded','uncertain']
def train(vectors,labels,n):
 vectors=np.asarray(vectors);z=independent_features(vectors,n);ctrl=independent_features(controls(n),n);means=[];deviations=[]
 for j,label in enumerate(LABELS[:3]):
  x=z[np.array(labels)==label];means.append(x.mean(0) if len(x) else ctrl[j]);deviations.extend(x-means[-1])
 means.append(ctrl[3]);cov=np.cov(np.array(deviations),rowvar=False) if len(deviations)>2 else np.eye(z.shape[1])*.01;cov=(cov+cov.T)/2+.01*np.eye(z.shape[1]);inverse=np.linalg.inv(cov)
 return dict(n=n,centers=np.array(means).tolist(),covariance=cov.tolist(),precision=inverse.tolist(),maximum_distance=5.,minimum_margin=.2,features='sqrt(multiplicity)*(m_q^2-1/N) for unique conjugate q pairs + Mx; C omitted because Fourier redundant',training='Independent-labelled clean development ED only; no noise labels or coordinates in inference',regularization=.01)
def predict(v,cfg):
 v=np.asarray(v)
 if not np.all(np.isfinite(v)):return dict(label='uncertain',reason='nonfinite')
 f=independent_features(v,cfg['n']);delta=np.array(cfg['centers'])-f;d=np.sqrt(np.maximum(np.einsum('ij,jk,ik->i',delta,cfg['precision'],delta),0));order=np.argsort(d);accept=bool(d[order[0]]<=cfg['maximum_distance'] and d[order[1]]-d[order[0]]>=cfg['minimum_margin'])
 return dict(label=LABELS[order[0]] if accept else 'uncertain',distances=d.tolist(),margin=float(d[order[1]]-d[order[0]]),accepted=accept)
