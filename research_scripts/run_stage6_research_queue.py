import sys,time,subprocess,os,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from annni.stage6_common import *
def run(name,args):
 guard();log=OUT/'verification'/f'queue_{name}.log'
 with log.open('a') as f:
  r=subprocess.run([sys.executable,*args],cwd=R,stdout=f,stderr=subprocess.STDOUT);assert r.returncode==0,(name,log)
 progress('queue',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_research_queue.py')
while True:
 guard();p=OUT/'domain_wall_candidates/development_101_0_index.json'
 if p.exists() and len(json.loads(p.read_text()))==36:break
 time.sleep(15)
for name,args in [
 ('B3_development',['scripts/run_stage6_b3.py','--task','development']),
 ('fixed_energy',['scripts/run_stage6_fixed_optimization.py']),
 ('oracle',['scripts/run_stage6_fixed_optimization.py','--oracle']),
 ('new_validation',['scripts/run_stage6_candidates.py','--task','validation']),
 ('B3_validation',['scripts/run_stage6_b3.py','--task','validation']),
 ('assess_development',['scripts/analyze_stage6_candidates.py','--task','development']),
 ('assess_validation',['scripts/analyze_stage6_candidates.py','--task','validation']),
]:run(name,args)
print('Development and validation complete; freeze analysis required.',flush=True)
