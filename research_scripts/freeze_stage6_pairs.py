import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=OUT/'noise_diagnosability/pairs.json'
if p.exists():raise SystemExit('Retain frozen pairs')
windows=json.loads((OUT/'reference_atlas/window_reference.json').read_text());pairs=[]
for row in windows:
 if row['kappa']==.5:continue
 hs=np.array(row['h']);c=hs[len(hs)//2]
 for offset in [.0125,.025]:
  left=float(hs[np.argmin(abs(hs-(c-offset)))]);right=float(hs[np.argmin(abs(hs-(c+offset)))]);pairs.append(dict(type='RN_feature_sides',a=dict(kappa=row['kappa'],h=left,source_task='windows'),b=dict(kappa=row['kappa'],h=right,source_task='windows'),delta_h=right-left,feature=row['primary_feature'],independent_opposite_phase_labels=False))
for a,b,kind in [((0,.2),(.1,.2),'same_ferro_control'),((.8,.1),(1,.2),'same_antiphase_control'),((0,.2),(0,1.8),'far_ferro_paramagnetic_control'),((.8,.1),(.9,1.8),'far_antiphase_paramagnetic_control')]:pairs.append(dict(type=kind,a=dict(kappa=a[0],h=a[1],source_task='development'),b=dict(kappa=b[0],h=b[1],source_task='development'),independent_opposite_phase_labels=kind.startswith('far')))
dump(p,dict(timestamp=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),pairs=pairs,quantum='full density offline',measurement='equal completeX/Z bitstrings',budgets=[10000,100000,1000000],repeats=32,seed=62717,interpretation='Known-template binary oracle is not the deployed phase classifier; same-phase controls expose distinguishability unrelated to phase',freeze_before_main_noisy_data=True));print(len(pairs))
