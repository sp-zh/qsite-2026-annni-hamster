"""Explicit stencil supports; no derivative across invalid preparations or stitches."""
import numpy as np
from scipy.signal import find_peaks,peak_prominences,peak_widths

def segments(valid,edges):
    parts=[];start=None
    for i,ok in enumerate(valid):
        if start is not None and (not ok or (i and not edges[i-1])):
            parts.append((start,i));start=None
        if ok and start is None:start=i
    if start is not None:parts.append((start,len(valid)))
    return parts

def derivative_peaks(h,y,valid,edge_ok,settings,sign=1):
    h=np.asarray(h);y=np.asarray(y);valid=np.asarray(valid,bool);edge_ok=np.asarray(edge_ok,bool)
    assert len(edge_ok)==len(h)-1 and np.all(np.diff(h)>0)
    if len(h)>2:np.testing.assert_allclose(np.diff(h),h[1]-h[0],atol=1e-12)
    deriv=np.full(len(h),np.nan);rows=[]
    for a,b in segments(valid,edge_ok):
        if b-a<3:continue
        z=sign*np.gradient(y[a:b],h[a:b],edge_order=2);deriv[a:b]=z
        pp=find_peaks(z,plateau_size=True)[0];prom=peak_prominences(z,pp)[0];width=peak_widths(z,pp)[0]*(h[1]-h[0]);detail={int(i):(float(pr),float(w)) for i,pr,w in zip(pp,prom,width)}
        ids=set(pp.tolist())
        if z[0]>z[1]:ids.add(0)
        if z[-1]>z[-2]:ids.add(len(z)-1)
        for j in sorted(ids):
            i=a+j;endpoint=j in [0,len(z)-1];pr,w=detail.get(j,(0.,None));amp=float(np.ptp(y[a:b]));reasons=[]
            if endpoint:reasons.append('endpoint')
            if amp<settings['min_range']:reasons.append('insufficient_raw_signal_range')
            if pr<settings['min_prominence']:reasons.append('insufficient_derivative_prominence')
            rows.append(dict(index=int(i),h=float(h[i]),height=float(z[j]),prominence=pr,width=w,endpoint=endpoint,amplitude=amp,step=float(h[1]-h[0]),position_support=[float(h[max(a,i-1)]),float(h[min(b-1,i+1)])],full_computation_support=[float(h[a]),float(h[b-1])],support_indices=list(range(a,b)),resolved_under_protocol=not reasons,reasons=reasons))
    return deriv,rows

def coarsen_edges(indices,fine_edges):return np.array([all(fine_edges[a:b]) for a,b in zip(indices,indices[1:])],bool)
