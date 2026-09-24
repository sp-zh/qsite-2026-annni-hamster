import json,hashlib,time,sys,platform,resource
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage4_upgrade_v1';plan=json.loads((O/'experiment_plan.json').read_text());x={}
for task in ['development','validation','heldout','map','n12','mitigation','floating','dynamics','branches','detection']:
 d=O/task;x[task]={}
 for p in d.glob('*index.json'):
  a=json.loads(p.read_text());x[task][p.stem]=len(a)
 x[task]['next_command']={'floating':'.venv-tn/bin/python scripts/run_upgrade_floating.py --task refine','dynamics':'.venv/bin/python scripts/run_upgrade_dynamics.py','mitigation':'.venv/bin/python scripts/run_upgrade_mitigation.py','branches':'.venv/bin/python scripts/run_upgrade_branches.py','detection':'.venv/bin/python scripts/run_upgrade_detection.py'}.get(task,f'.venv/bin/python scripts/run_upgrade.py --task {task}')
now=datetime.now(timezone.utc);data=dict(timestamp=now.isoformat(),elapsed_seconds=(now-datetime.fromisoformat(plan['started_utc'])).total_seconds(),remaining_seconds=(datetime.fromisoformat(plan['deadline'])-now).total_seconds(),deadline=plan['deadline'],workpackages=x)
(O/'status.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
