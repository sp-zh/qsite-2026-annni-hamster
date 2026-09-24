import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_detection import *
rows=json.loads((OUT/'development/index.json').read_text());validation=json.loads((OUT/'validation/index.json').read_text());x=[vector(observations(np.load(ROOT/r['methods']['B3']['archive'])['state'],8)) for r in rows]
config=train(x,8);out=OUT/'detection';out.mkdir(exist_ok=True)
if (out/'frozen.json').exists():assert json.loads((out/'frozen.json').read_text())==config
else:dump(out/'frozen.json',config)
freeze=dict(timestamp=datetime.now(timezone.utc).isoformat(),plan_sha=sha(OUT/'experiment_plan.json'),code_fingerprint=fp(),detection_sha=sha(out/'frozen.json'),validation_pass=sum(r['methods']['B3']['joint_pass'] for r in validation),validation_points=len(validation),parameters_changed=False,choice='B3 main + B4 equivalent-direction noise-energy selection; preserve 128 CNOT limit and all thresholds',cost_measurement=dict(development_seconds=sum(r['seconds'] for point in rows for r in point['candidates']),density_n8_example_seconds=.0675),budget_adjustment='Single measured-cost review: retain original allocation; N8 density affordable, benchmark N12 before choosing exact vs trajectories',B4='Two p0-equivalent directions; choose smaller p=.01 energy, pay extra pilot; all p fixed params. No ED eligibility selection; preparation mask reported.')
if not (OUT/'freeze.json').exists():dump(OUT/'freeze.json',freeze)
print(freeze['validation_pass'],freeze['validation_points'])
