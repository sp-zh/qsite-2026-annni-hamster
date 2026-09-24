"""Cea et al. Eq8/B2 mapped paper sigma-z -> this project's Pauli X.
Seven-point signed oscillatory part; fit K freely, never from the ZZ decay exponent.
Finite-OBC profile fitting remains sensitive to N, windows and background removal.
"""
import numpy as np
from scipy.optimize import least_squares
SMOOTH=np.array([-15/496,-1/248,71/248,.5,137/496,1/248,-1/31])
def extract(x):
 x=np.asarray(x);smooth=np.array([SMOOTH@x[j-3:j+4] for j in range(3,len(x)-3)]);return np.arange(4,len(x)-2),x[3:-3]-smooth,smooth
def fit_profile(x):
 n=len(x);j,osc,smooth=extract(x);chord=n/np.pi*np.sin(np.pi*j/n);rows=[]
 for fraction in [.2,.3]:
  mask=(j>=fraction*n)&(j<=n*(1-fraction));sites=j[mask];y=osc[mask];log=np.log(chord[mask]);amp=np.sqrt(np.mean(y*y))
  if amp<1e-8:rows.append(dict(edge_fraction=fraction,status='oscillation_unresolved',amplitude=float(amp)));continue
  def basis(a):return np.exp(-a[1]*log)[:,None]*np.column_stack([np.cos(a[0]*sites),np.sin(a[0]*sites)])
  def residual(a):
   b=basis(a);coef=np.linalg.lstsq(b,y,rcond=None)[0];return b@coef-y
  fits=[least_squares(residual,[q,.4],bounds=([.001,-.5],[np.pi-.001,2]),max_nfev=400) for q in np.linspace(.03,np.pi-.03,24)]
  fits.sort(key=lambda f:sum(f.fun**2));f=fits[0];coef=np.linalg.lstsq(basis(f.x),y,rcond=None)[0];rmse=np.sqrt(np.mean(f.fun**2))
  rows.append(dict(edge_fraction=fraction,status='finite_size_fit_only',q=float(f.x[0]),K=float(f.x[1]),coefficients=coef.tolist(),amplitude=float(amp),rmse=float(rmse),relative_rmse=float(rmse/amp),parameters_at_bound=bool(f.x[1]<-.49 or f.x[1]>1.99),competing_minima=[dict(q=float(a.x[0]),K=float(a.x[1]),rss=float(sum(a.fun**2))) for a in fits[:4]],sites=sites.tolist()))
 return dict(j=j.tolist(),oscillatory=osc.tolist(),uniform=smooth.tolist(),fits=rows,operator='Project Pauli X = paper sigma-z under global Hadamard',source='Cea arXiv2402.11022v1 Eq8 AppendixB EqB2; historical downloaded primary text re-read Stage6',scope='Separate finite-OBC Friedel K fit; not ZZ correlation exponent; window/bond/size reproducibility required before boundary interpretation')
