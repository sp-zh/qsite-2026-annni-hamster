"""Predeclared finite-size features; spectral/size evidence is separate from detectors."""
import numpy as np
from .diagnostics import local_peaks
def independent_features(v,n):
 v=np.asarray(v);sf=v[...,n:2*n];weight=np.sqrt(np.r_[1,np.full(n//2-1,2),1]);return np.concatenate([(sf[...,:n//2+1]-1/n)*weight,v[...,-1:]],axis=-1)
def response_curves(h,values,n,states=None,ambiguous=None):
 h=np.asarray(h);values=np.asarray(values);mid=(h[:-1]+h[1:])/2;dh=np.diff(h)
 out={'h_mid':mid,'dmx_dh':np.diff(values[:,-1])/dh,'minus_dm0_dh':-np.diff(values[:,n])/dh,'minus_dmap_dh':-np.diff(values[:,n+n//4])/dh,'unique_feature_speed':np.linalg.norm(np.diff(independent_features(values,n),axis=0),axis=1)/dh}
 chi=np.full(len(mid),np.nan)
 if states is not None:
  for i in range(len(mid)):
   if states[i] is not None and states[i+1] is not None and not (ambiguous is not None and (ambiguous[i] or ambiguous[i+1])):
    chi[i]=-np.log(np.clip(abs(np.vdot(states[i],states[i+1]))**2,1e-300,1))/dh[i]**2
 out['chi_f']=chi;return out
def peaks_and_primary(h,y):
 h=np.asarray(h);mid=(h[:-1]+h[1:])/2;support=np.column_stack([h[:-1],h[1:]]);allpeaks=local_peaks(mid,y,support);interior=[p for p in allpeaks if not p['endpoint'] and p['value']>0]
 ordered=sorted(interior,key=lambda p:(-p['value'],p['coordinate']));best=ordered[0] if ordered else None
 competing=[p for p in ordered[1:] if p['value']>=.9*best['value'] and abs(p['coordinate']-best['coordinate'])>.075] if best else []
 return dict(peaks=allpeaks,primary=best,resolvable=bool(best and not competing),competing=competing,rule='Largest non-endpoint peak of the SAME named observable; ambiguous if another peak >=90% and separated >.075. No nearest-reference peak pairing.',smoothing=None,interpolation=None)
def physical_reference(n,k,h,state,obs,binder):
 # Independently justified interior anchors, not output of any evaluated detector.
 # h=0 and k=0 are analytic; finite positive-h extensions require high order and controls.
 sf=obs['structure_factor'];mx=obs['mx']
 if k==0 and h<=.70:return 'ferro-like','R0','Exact Ising ordered side, away from h=1; PBC finite-size observables retained'
 if k==0 and h>=1.30:return 'paramagnetic-like','R0','Exact Ising disordered side, away from h=1'
 if k<=.3 and h<=.2 and sf[0]>=.75 and binder>=.58:return 'ferro-like','R0_extension','Small-field continuation from classical ferro; m0 and fourth moment consistent; not a proved exact region boundary'
 if k>=.65 and h<=.1 and sf[n//4]>=.40:return 'antiphase-like','R0_extension','Small-field continuation from classical period4; full SF peak and amplitude; requires separate finite-size trend for Rlarge'
 if h>=1.6 and mx>=.8 and sf[0]<.4 and sf[n//4]<.3:return 'paramagnetic-like','R0_extension','High-field continuation, transverse polarization and absence of strong order; interior only'
 return None,'RN_only','No independent discrete phase label assigned; evaluate named finite-size features'
