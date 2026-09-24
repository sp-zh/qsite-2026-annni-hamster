"""Simulator-only D2, complements measured D1; all switches/quality explicit."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.signal import find_peaks
from annni.stage5_adapt import *
from annni.stage5_noise import noise_record
from annni.upgrade_detection import uhlmann_squared,peak_support_mask
O=OUT/'end_to_end';index=json.loads((OUT/'selector_benchmark/windows/index.json').read_text());curves=[];peaks=[]
for k,hs in PLAN['windows']:
 points=sorted([r for r in index if abs(r['kappa']-k)<1e-10],key=lambda r:r['h']);hs=np.array([r['h'] for r in points]);mid=(hs[:-1]+hs[1:])/2
 for arm in ['B3','B5']:
  for p in [0,.01,.05]:
   matrices=[];values=[];ids=[];quality=[]
   for point in points:
    row=point[arm];rec=noise_record(row,p,keep=True);rho=np.load(ROOT/rec['archive'])['rho'];matrices.append(rho);values.append(vector(observations(rho,8)));ids.append([row['ref'],row['selected']['words']]);quality.append(row['joint_pass'])
   F=np.array([uhlmann_squared(a,b) for a,b in zip(matrices[:-1],matrices[1:])]);chi=-np.log(np.maximum(F,1e-300))/np.diff(hs)**2;dv=np.linalg.norm(np.diff(values,axis=0),axis=1)/np.diff(hs);switch=[a!=b for a,b in zip(ids[:-1],ids[1:])];curve=dict(kappa=k,arm=arm,p=p,h=hs.tolist(),h_mid=mid.tolist(),fidelity_squared=F.tolist(),chi=chi.tolist(),observable_change=dv.tolist(),preparation_pass=quality,structure_switch=switch,state_access=True,shots_charged=False,interpretation='Full simulator density cross-check, not measured within shot budget');curves.append(curve)
   for name,y in [('D1_change',dv),('D2_chi',chi)]:
    indices=list(find_peaks(y)[0])+([0] if y[0]>y[1] else [])+([len(y)-1] if y[-1]>y[-2] else [])
    for i in indices:peaks.append(dict(kappa=k,arm=arm,p=p,metric=name,support=[float(hs[i]),float(hs[i+1])],midpoint=float(mid[i]),height=float(y[i]),endpoint=i in [0,len(y)-1],quality_support=bool(peak_support_mask(quality)[i]),structure_switch=switch[i],smoothing=None,step=.025))
   dump(O/'state_access_curves.json',curves);dump(O/'state_access_peaks.json',peaks);print(k,arm,p,flush=True)
