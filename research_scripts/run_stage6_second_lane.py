import sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
while True:
 guard();p=OUT/'floating_boundary_scan/bounded_index.json';f=OUT/'floating_boundary_scan/bounded_failures.json';count=len(json.loads(p.read_text())) if p.exists() else 0;failed=len(json.loads(f.read_text())) if f.exists() else 0
 if count+failed>=36:break
 time.sleep(15)
with (OUT/'verification/mps_followup.log').open('a') as log:
 result=subprocess.run([str(ROOT/'.venv-tn/bin/python'),'scripts/run_stage6_mps_followup.py'],stdout=log,stderr=subprocess.STDOUT);assert result.returncode==0
while not (OUT/'confirmation/method_frozen.json').exists():guard();time.sleep(15)
commands=[
 ('n12_noise_freeze',['scripts/freeze_stage6_n12_noise.py']),
 ('n12_pilot',['scripts/run_stage6_candidates.py','--task','n12','--stop','2']),
 ('n12_main',['scripts/run_stage6_candidates.py','--task','n12']),
 ('B3_n12',['scripts/run_stage6_b3.py','--task','n12']),
 ('n12_window',['scripts/run_stage6_candidates.py','--task','n12_window']),
 ('B3_n12_window',['scripts/run_stage6_b3.py','--task','n12_window']),
 ('n12_noise_pilot',['scripts/run_stage6_end_to_end.py','--task','n12','--stop','1']),
 ('n12_noise',['scripts/run_stage6_end_to_end.py','--task','n12']),
 ('n12_192',['scripts/run_stage6_candidates.py','--task','n12_192']),
 ('B3_n12_192',['scripts/run_stage6_b3.py','--task','n12_192']),
 ('n12_assess',['scripts/analyze_stage6_candidates.py','--task','n12']),
 ('n12_192_assess',['scripts/analyze_stage6_candidates.py','--task','n12_192']),
 ('n12_window_assess',['scripts/analyze_stage6_candidates.py','--task','n12_window']),
 ('n12_noise_analyze',['scripts/analyze_stage6_end_to_end.py','--task','n12'])]
for name,args in commands:
 guard();progress('second_lane_running',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_second_lane.py')
 with (OUT/f'verification/queue_{name}.log').open('a') as f:result=subprocess.run([sys.executable,*args],stdout=f,stderr=subprocess.STDOUT);assert result.returncode==0,(name,result.returncode)
 progress('second_lane',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_second_lane.py')
print('Second scientific lane completed',flush=True)
