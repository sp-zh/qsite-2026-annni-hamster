"""Explicit local continuation queue. Does not reset the frozen 12-hour deadline."""
import sys,json,time,subprocess,os,argparse
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';plan=json.loads((O/'experiment_plan.json').read_text());parser=argparse.ArgumentParser();parser.add_argument('--queue',choices=['fullmap','n12'],required=True);a=parser.parse_args()
def wait_for(path,count):
 while True:
  if datetime.now(timezone.utc)>=datetime.fromisoformat(plan['deadline']):raise TimeoutError('Deadline reached while awaiting prerequisite')
  if path.exists() and len(json.loads(path.read_text()))>=count:return
  time.sleep(30)
def run(script,*args):
 log=O/'verification'/(Path(script).stem+'.log')
 with log.open('a') as f:subprocess.run([sys.executable,str(R/script),*args],cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
if a.queue=='fullmap':
 wait_for(O/'end_to_end/core_index.json',94);run('scripts/run_stage5_e2e_full.py','--task','full_best')
else:
 wait_for(O/'selector_benchmark/n12_192/index.json',84);wait_for(O/'selector_benchmark/n12test/index.json',24);run('scripts/run_stage5_n12_noise.py');run('scripts/run_stage5_e2e_n12.py','--task','n12')
