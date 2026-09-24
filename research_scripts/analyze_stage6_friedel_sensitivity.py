"""Auxiliary background sensitivity, never replaces the frozen evidence protocol."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_friedel import SMOOTH, fit_profile
from scipy.optimize import least_squares
O=OUT/'floating_boundary_scan'
def fit_raw(x):
    n=len(x);j=np.arange(1,n+1);out=[]
    for fraction in [.2,.3]:
        mask=(j>=fraction*n)&(j<=n*(1-fraction));sites=j[mask];y=x[mask]
        u=(sites-(n+1)/2)/n;chord=n/np.pi*np.sin(np.pi*sites/n)
        background=np.column_stack([np.ones(len(u)),u,u*u])
        def basis(a):
            return np.column_stack([background,chord[:,None]**(-a[1])*np.column_stack([np.cos(a[0]*sites),np.sin(a[0]*sites)])])
        def residual(a):
            b=basis(a);return b@np.linalg.lstsq(b,y,rcond=None)[0]-y
        fits=[least_squares(residual,[q,.4],bounds=([.001,-.5],[np.pi-.001,2]),max_nfev=400) for q in np.linspace(.03,np.pi-.03,24)]
        best=min(fits,key=lambda f:sum(f.fun**2));b=basis(best.x);coef=np.linalg.lstsq(b,y,rcond=None)[0]
        oscillatory=b[:,3:]@coef[3:];scale=np.sqrt(np.mean(oscillatory**2))
        out.append(dict(edge_fraction=fraction,q=float(best.x[0]),K=float(best.x[1]),rmse=float(np.sqrt(np.mean(best.fun**2))),relative_to_fitted_oscillation_rmse=float(np.sqrt(np.mean(best.fun**2))/max(scale,1e-15)),coefficients=coef.tolist(),sites=sites.tolist()))
    return out
rows=[];seen=set()
for task in ['bounded','followup','controls']:
    p=O/f'{task}_index.json'
    if not p.exists():continue
    for r in json.loads(p.read_text()):
        if r['h'] not in [.4,.425,.475,.5] or r['sha256'] in seen:continue
        seen.add(r['sha256']);x=np.load(ROOT/r['archive'])['x']
        key=dict(source=r['sha256'],code=sha(__file__),original_code=sha(ROOT/'annni/stage6_friedel.py'))
        cache=O/'sensitivity_cache'/(uid(key)+'.json')
        if cache.exists():result=json.loads(cache.read_text())
        else:
            result=dict(key=key,original=fit_profile(x)['fits'],reflection_reversed=fit_profile(x[::-1])['fits'],raw_quadratic_background=fit_raw(x),reflection_profile_max_error=float(max(abs(x-x[::-1]))))
            dump(cache,result)
        rows.append(dict(n=r['n'],h=r['h'],chi=r['chi'],initial=r['initial'],archive=r['archive'],**result))
        dump(O/'friedel_sensitivity.json',dict(scope='Auxiliary sensitivity only. Original Eq8/B2 fits and frozen thresholds remain authoritative. Raw-background polynomial is an alternative nuisance model, not a new acceptance rule; fit errors are not statistical confidence intervals.',rows=rows))
        print(r['n'],r['h'],[round(f['K'],3) for f in result['original']],[round(f['K'],3) for f in result['raw_quadratic_background']],flush=True)
