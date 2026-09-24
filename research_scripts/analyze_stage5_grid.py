"""All-arm common-grid diagnostics and measurement-repeat peak variability."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.signal import find_peaks
from annni.stage5_adapt import *
O=OUT/'end_to_end';core=json.loads((O/'core_index.json').read_text());fine=json.loads((O/'refined_index.json').read_text());curves=[];peaks=[]
for k,basehs in PLAN['windows']:
 for step,pool in [(.025,core),(.0125,core+fine)]:
  points=sorted([r for r in pool if abs(r['kappa']-k)<1e-10 and basehs[0]-1e-10<=r['h']<=basehs[-1]+1e-10],key=lambda r:r['h']);hs=np.array([r['h'] for r in points]);assert np.max(abs(np.diff(hs)-step))<1e-9;mid=(hs[:-1]+hs[1:])/2
  for arm in ['B0_raw','B3_raw','B5_raw','B5_zne','B5_sv']:
   for p in [0,.01,.05]:
    rr=[next(e['record'] for e in r['entries'] if e['arm']==arm and e['record']['p']==p) for r in points];aa=[np.load(ROOT/r['archive']) for r in rr];v=np.array([a['deterministic'] for a in aa]);dv=np.diff(v,axis=0)/step;metrics={'full_observable_change':np.linalg.norm(dv,axis=1),'absolute_mx_derivative':abs(dv[:,-1])}
    for name,y in metrics.items():
     ids=list(find_peaks(y)[0])+([0] if y[0]>y[1] else [])+([len(y)-1] if y[-1]>y[-2] else []);repeat={}
     for budget in ['10000','100000']:
      vals=np.array([a['samples_'+budget] for a in aa]);d=np.diff(vals,axis=0)/step;ys=np.linalg.norm(d,axis=2) if name=='full_observable_change' else abs(d[:,:,-1]);loc=mid[np.argmax(ys,axis=0)];repeat[budget]=dict(argmax_locations=loc.tolist(),empirical_quantiles=np.quantile(loc,[.025,.5,.975]).tolist(),interpretation='Measurement-repetition variability, separate from grid resolution and branch effects')
     curves.append(dict(kappa=k,step=step,arm=arm,p=p,metric=name,h_mid=mid.tolist(),values=y.tolist(),prep_pass=[r['prep_pass'] for r in rr],repeated_peak=repeat))
     for i in ids:peaks.append(dict(kappa=k,step=step,arm=arm,p=p,metric=name,support=[float(hs[i]),float(hs[i+1])],endpoint=i in [0,len(y)-1],height=float(y[i]),smoothing=None,interpolation=None))
dump(O/'all_arm_curves.json',curves);dump(O/'all_arm_peaks.json',peaks);print(len(curves),len(peaks))
