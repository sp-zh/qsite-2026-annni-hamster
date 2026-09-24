import sys,time,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from annni.stage6_common import *
while True:
 guard();p=OUT/'failure_mechanisms/validation_assessment.json'
 if p.exists() and len(json.loads(p.read_text()))==24:break
 time.sleep(15)
commands=[
 ('reference_dev',['scripts/build_stage6_evaluation_reference.py','--task','development']),
 ('reference_val',['scripts/build_stage6_evaluation_reference.py','--task','validation']),
 ('freeze',['scripts/freeze_stage6_methods.py']),
 ('new_confirmation',['scripts/run_stage6_candidates.py','--task','confirmation']),
 ('B3_confirmation',['scripts/run_stage6_b3.py','--task','confirmation']),
 ('reference_confirmation',['scripts/build_stage6_evaluation_reference.py','--task','confirmation']),
 ('assess_confirmation',['scripts/analyze_stage6_candidates.py','--task','confirmation']),
 ('stability743',['scripts/run_stage6_candidates.py','--task','stability','--seed','743']),
 ('stability857',['scripts/run_stage6_candidates.py','--task','stability','--seed','857']),
 ('B3_stability743',['scripts/run_stage6_b3.py','--task','stability','--seed','743']),
 ('B3_stability857',['scripts/run_stage6_b3.py','--task','stability','--seed','857']),
]
for name,args in commands:
 guard()
 if name=='freeze' and (OUT/'confirmation/method_frozen.json').exists():
  frozen=json.loads((OUT/'confirmation/method_frozen.json').read_text())
  assert frozen['candidate_code']==sha(ROOT/'annni/stage6_candidates.py') and frozen['runner_sha']==sha(ROOT/'scripts/run_stage6_candidates.py') and frozen['hybrid_code']==sha(ROOT/'annni/stage6_hybrid.py')
  continue
 with (OUT/f'verification/queue_{name}.log').open('a') as f:
  result=subprocess.run([sys.executable,*args],cwd=R,stdout=f,stderr=subprocess.STDOUT);assert result.returncode==0,(name,result.returncode)
 progress('confirmation_queue',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_confirmation_queue.py')
print('Confirmation queue finished',flush=True)
