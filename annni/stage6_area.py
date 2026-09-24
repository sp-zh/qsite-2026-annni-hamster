"""Voronoi-cell area on a stated rectangular domain; refinements never pooled."""
import numpy as np
def edges(values,lo=None,hi=None):
 x=np.unique(np.asarray(values,float));assert len(x)>1 and np.all(np.diff(x)>0)
 return np.r_[x[0] if lo is None else lo,(x[:-1]+x[1:])/2,x[-1] if hi is None else hi]
def cell_weights(kappa,h,domain=None,region=None):
 domain=domain or [min(kappa),max(kappa),min(h),max(h)];kx=edges(kappa,*domain[:2]);hy=edges(h,*domain[2:]);region=domain if region is None else region
 a=np.maximum(0,np.minimum(kx[1:],region[1])-np.maximum(kx[:-1],region[0]));b=np.maximum(0,np.minimum(hy[1:],region[3])-np.maximum(hy[:-1],region[2]));return a[:,None]*b[None,:]
