"""Signed fixed-midpoint correlation fits; finite-window comparisons, not p-values."""
import numpy as np
from scipy.optimize import least_squares
def fit_models(c,n):
 rows=[]
 for lo,hi in [(2,n//4),(4,n//3)]:
  r=np.arange(lo,min(hi,len(c)-1)+1);y=np.asarray(c)[r];split=max(5,int(.7*len(r)));train=r[:split];test=r[split:]
  for kind in ['ordered','power','exponential']:
   def pred(a,x):
    envelope=a[0]+a[3]/x if kind=='ordered' else a[0]*x**(-a[3]) if kind=='power' else a[0]*np.exp(-x/a[3])
    return envelope*np.cos(a[1]*x+a[2])
   lower=[-2,0,-np.pi,-4 if kind=='ordered' else .001];upper=[2,np.pi,np.pi,4 if kind in ['ordered','power'] else 10*n]
   fits=[]
   for q in np.linspace(.7,1.8,8):
    a0=[.5,q,0,.1 if kind=='ordered' else .5 if kind=='power' else 10]
    fits.append(least_squares(lambda a:pred(a,train)-y[:split],a0,bounds=(lower,upper),max_nfev=500))
   best=min(fits,key=lambda f:sum(f.fun**2));full=least_squares(lambda a:pred(a,r)-y,best.x,bounds=(lower,upper),max_nfev=1000)
   rows.append(dict(kind=kind,window=[int(r[0]),int(r[-1])],train_r=train.tolist(),test_r=test.tolist(),parameters=full.x.tolist(),training_parameters=best.x.tolist(),q=float(full.x[1]),rss=float(sum(full.fun**2)),heldout_mse=float(np.mean((pred(best.x,test)-y[split:])**2)),optimizer_success=bool(full.success),points=len(r),parameter_count=4))
 return rows
def entropy_fits(entropy,n,q):
 l=np.arange(1,n);x=np.log(2*n/np.pi*np.sin(np.pi*l/n));rows=[]
 for frac in [.15,.25]:
  mask=(l>=n*frac)&(l<=n*(1-frac));xx=x[mask];y=entropy[mask]
  for correction in [False,True]:
   a=np.column_stack([xx,np.ones(len(xx))])
   if correction:a=np.column_stack([a,np.cos(q*l[mask])/np.exp(xx/2),np.sin(q*l[mask])/np.exp(xx/2)])
   fit=np.linalg.lstsq(a,y,rcond=None)[0];rows.append(dict(edge_fraction=frac,oscillation_correction=correction,c=float(6*fit[0]),rms=float(np.sqrt(np.mean((a@fit-y)**2))),coefficients=fit.tolist(),correction_definition='Fixed1/2 nuisance exponent; not a fitted Luttinger K'))
 return rows
