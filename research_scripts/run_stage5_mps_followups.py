"""Sequential followups of the active MPS campaign, within the original deadline."""
import sys,json,time,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';P=json.loads((O/'experiment_plan.json').read_text())
while not (O/'floating_validation/index.json').exists() or len(json.loads((O/'floating_validation/index.json').read_text()))<39:
 if datetime.now(timezone.utc)>=datetime.fromisoformat(P['deadline']):raise TimeoutError('Main MPS prerequisite exceeded original budget')
 time.sleep(30)
def run(exe,script):
 print('Starting',script,datetime.now(timezone.utc).isoformat(),flush=True)
 with (O/'verification'/(Path(script).stem+'.log')).open('a') as f:subprocess.run([str(R/exe),str(R/script)],cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
run('.venv/bin/python','scripts/analyze_stage5_floating.py')
run('.venv-tn/bin/python','scripts/run_stage5_chi512.py')
run('.venv-tn/bin/python','scripts/run_stage5_size_extension.py')
if (O/'floating_validation/size_extension_index.json').exists():run('.venv/bin/python','scripts/analyze_stage5_size_extension.py')
print('MPS followups complete',flush=True)
