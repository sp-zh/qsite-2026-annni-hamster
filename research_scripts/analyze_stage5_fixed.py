import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.signal import find_peaks
from annni.stage5_adapt import *
from annni.upgrade_detection import uhlmann_squared,peak_support_mask
O=OUT/'end_to_end';curves=[];peaks=[];qualified=[]
for version,step in [('branches',.025),('branches_refined',.0125)]:
 rows=json.loads((O/version/'fixed_index.json').read_text())
 for k in [0,.3,.8]:
  points=sorted([r for r in rows if r['kappa']==k],key=lambda r:r['h']);hs=np.array([r['h'] for r in points]);mid=(hs[:-1]+hs[1:])/2;q=[r['state']['joint_pass'] for r in points];support=peak_support_mask(q);local=[]
  for p in [0,.01,.05]:
   aa=[np.load(ROOT/next(r for r in x['noise'] if r['p']==p)['archive']) for x in points];v=np.array([vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx']))) for a in aa]);d=np.diff(v,axis=0)/step;ff=np.array([uhlmann_squared(a['rho'],b['rho']) for a,b in zip(aa[:-1],aa[1:])]);metrics={'full_observable_change':np.linalg.norm(d,axis=1),'mx_derivative':abs(d[:,-1]),'state_access_chi':-np.log(np.maximum(ff,1e-300))/step**2}
   for name,y in metrics.items():
    row=dict(version=version,step=step,kappa=k,p=p,metric=name,h_mid=mid.tolist(),values=y.tolist(),preparation_pass=q,state_access=name=='state_access_chi');curves.append(row);imax=int(np.argmax(y));local.append(dict(p=p,metric=name,support=[float(hs[imax]),float(hs[imax+1])],quality_support=bool(support[imax]),endpoint=imax in [0,len(y)-1]))
    ii=list(find_peaks(y)[0])+([0] if y[0]>y[1] else [])+([len(y)-1] if y[-1]>y[-2] else [])
    for j in ii:peaks.append(dict(version=version,step=step,kappa=k,p=p,metric=name,support=[float(hs[j]),float(hs[j+1])],quality_support=bool(support[j]),endpoint=j in [0,len(y)-1],height=float(y[j])))
  qualified.append(dict(version=version,kappa=k,global_peaks=local,interpretation='Grid supports, not statistical confidence. Structure held fixed; pure preparation quality applies to full four-node peak stencil.'))
dump(O/'fixed_curves.json',curves);dump(O/'fixed_peaks.json',peaks);dump(O/'fixed_peak_summary.json',qualified);print(qualified)
