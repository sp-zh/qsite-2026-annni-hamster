"""Frozen Stage3 resolvability rules atop unchanged diagnostic v1.
Grid supports, branch tests and deterministic numerical error are not CIs.
"""
import numpy as np
from scipy.signal import find_peaks,peak_prominences,peak_widths
from .diagnostics import local_peaks

def segments(valid):
    valid=np.asarray(valid,bool)
    starts=np.flatnonzero(valid & ~np.r_[False,valid[:-1]])
    stops=np.flatnonzero(valid & ~np.r_[valid[1:],False])+1
    return list(zip(starts,stops))

def derivative_no_gaps(h,y,valid,sign=1):
    derivative=np.full(len(h),np.nan)
    for start,stop in segments(valid):
        if stop-start>=3:
            derivative[start:stop]=sign*np.gradient(y[start:stop],h[start:stop],edge_order=2)
    return derivative

def feature_peaks(h,y,valid,switch,checked,sensitive,settings,sign=1):
    h=np.asarray(h);y=np.asarray(y);valid=np.asarray(valid,bool)
    derivative=derivative_no_gaps(h,y,valid,sign)
    rows=[]
    for a,b in segments(valid):
        if b-a<3:continue
        xx=h[a:b];yy=derivative[a:b]
        peaks=find_peaks(yy,plateau_size=True)[0]
        prom=peak_prominences(yy,peaks)[0] if len(peaks) else []
        widths=peak_widths(yy,peaks,rel_height=.5)[0]*(h[1]-h[0]) if len(peaks) else []
        detail={int(i):(float(p),float(w)) for i,p,w in zip(peaks,prom,widths)}
        candidates=local_peaks(xx,yy)
        for r in candidates:
            j=a+r['index'];prominence,width=detail.get(r['index'],(0.,None))
            amplitude=float(np.ptp(y[a:b]));lo=max(a,j-1);hi=min(b-1,j+1)
            stable=True
            for offset in [0,1]:
                ids=np.arange(a+offset,b,2)
                if len(ids)<3:stable=False;continue
                coarse=sign*np.gradient(y[ids],h[ids],edge_order=2)
                cp=find_peaks(coarse,prominence=settings['min_peak_prominence'])[0]
                if not len(cp) or np.min(abs(h[ids[cp]]-h[j]))>.10000001:stable=False
            unchecked=any(switch[t] and not checked[t] for t in range(lo,hi+1))
            branch_bad=any(bool(sensitive[t]) for t in range(lo,hi+1))
            reasons=[]
            if r['endpoint']:reasons.append('endpoint_peak')
            if amplitude<settings['min_observable_range']:reasons.append('insufficient_observable_range')
            if prominence<settings['min_peak_prominence']:reasons.append('insufficient_derivative_prominence')
            if prominence<settings['numerical_floor']:reasons.append('numerical_floor')
            if not stable:reasons.append('coarse_grid_unstable')
            if unchecked:reasons.append('unchecked_branch_switch')
            if branch_bad:reasons.append('branch_sensitive')
            rows.append(dict(index=int(j),h=float(h[j]),height=float(derivative[j]),
                interval_low=float(h[lo]),interval_high=float(h[hi]),step=float(h[1]-h[0]),
                endpoint=r['endpoint'],prominence=prominence,half_prominence_width=width,
                observable_range=amplitude,coarse_grid_stable=stable,resolved=not reasons,
                status='resolved' if not reasons else 'not_resolved',reasons=reasons))
    return derivative,rows
