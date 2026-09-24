import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.signal import find_peaks
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
from annni.upgrade_detection import *
from annni.diagnostics import diagnose
O=OUT/'detection';cfg=json.loads((O/'frozen.json').read_text());rows=[]
for task in ['development','heldout','map']:
 path=OUT/task/'noise_index.json'
 if not path.exists():continue
 for point in json.loads(path.read_text()):
  for method,entries in point['methods'].items():
   for record in entries:
    a=np.load(ROOT/record['archive']);v=vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx'])))
    rows.append(dict(task=task,kappa=point['kappa'],h=point['h'],method=method,p=record['p'],prep_pass=record['prep_joint_pass'],**predict(v,cfg),old_three_feature=diagnose(a['structure_factor'],float(a['mx']))['label']))
dump(O/'predictions.json',rows)
controls_result=[]
for name,v in zip(['ferro_cat','antiphase_cat','plus','fully_mixed'],controls(8)):controls_result.append(dict(control=name,**predict(v,cfg)))
dump(O/'controls.json',controls_result)
# Noisy Uhlmann on fixed 3 main slices, full matrices recomputed by frozen circuits.
index=json.loads((OUT/'map/index.json').read_text());curves=[];peaks=[]
for k in [0,.3,.8]:
 chosen=sorted([p for p in index if abs(p['kappa']-k)<1e-12],key=lambda p:p['h']);hs=np.array([p['h'] for p in chosen])
 for noise in [0,.01,.05]:
  matrices=[];vs=[];identities=[];statuses=[]
  for point in chosen:
   r=point['methods']['B3'];nr=noise_record(r,noise,keep=True);rho=np.load(ROOT/nr['archive'])['rho'];matrices.append(rho);vs.append(vector(observations(rho,8)));identities.append(dict(ref=r['ref'],words=r['selected']['words'],params_sha=r['sha256']));statuses.append(r['joint_pass'])
  f=np.array([uhlmann_squared(a,b) for a,b in zip(matrices[:-1],matrices[1:])]);chi=-np.log(np.maximum(f,1e-300))/np.diff(hs)**2;v=np.array(vs);dv=np.linalg.norm(np.diff(v,axis=0),axis=1)/np.diff(hs)
  switches=[identities[i]['ref']!=identities[i+1]['ref'] or identities[i]['words']!=identities[i+1]['words'] for i in range(len(hs)-1)]
  mid=(hs[:-1]+hs[1:])/2;curve=dict(kappa=k,p=noise,h=hs.tolist(),h_mid=mid.tolist(),squared_fidelity=f.tolist(),chi_f=chi.tolist(),full_observable_change_rate=dv.tolist(),preparation_pass=statuses,structure_switch=switches,scope='pointwise selected circuits; simulator state access, switches flagged not interpreted as critical boundaries',normalization='squared Uhlmann',step=.1)
  curves.append(curve)
  for name,y in [('D1_change',dv),('D2_chi',chi)]:
   ids=list(find_peaks(y)[0]);ids+=([0] if y[0]>y[1] else [])+([len(y)-1] if y[-1]>y[-2] else [])
   for i in ids:peaks.append(dict(kappa=k,p=noise,metric=name,h=float(mid[i]),support=[float(hs[i]),float(hs[i+1])],endpoint=i in [0,len(y)-1],step=.1,structure_switch=switches[i],both_prep_pass=statuses[i] and statuses[i+1],smoothing=None))
  dump(O/'fidelity_curves.json',curves);dump(O/'peaks.json',peaks)
# Independent finite-size Binder comparison: new sparse ED only a small Ising control slice.
if not (O/'binder.json').exists():
 binder=[]
 for n in [8,12,16]:
  chain=Chain(n);mz=chain.z.mean(1)
  for h in [.8,.9,1.,1.1,1.2]:
   s=chain.ground_state(0,h);m2=float(s.probabilities@(mz**2));m4=float(s.probabilities@(mz**4));binder.append(dict(n=n,kappa=0,h=h,mz2=m2,mz4=m4,binder=1-m4/(3*m2*m2),bc='PBC',definition='scalar ferro 1-<Mz^4>/(3<Mz^2>^2)',disposition='newly_executed'))
 dump(O/'binder.json',binder)
