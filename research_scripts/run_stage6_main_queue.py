"""Sequential scientific queue after independent confirmation/stability. No silent background promise."""
import sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
while True:
 guard();p=OUT/'verification/progress_confirmation_queue.json'
 if p.exists() and json.loads(p.read_text())['completed']=='B3_stability857':break
 time.sleep(15)
commands=[
 ('noise_validation',['scripts/run_stage6_end_to_end.py','--task','validation']),
 ('analyze_noise_validation',['scripts/analyze_stage6_end_to_end.py','--task','validation']),
 ('freeze_mitigation',['scripts/freeze_stage6_mitigation.py']),
 ('noise_core',['scripts/run_stage6_end_to_end.py','--task','core']),
 ('analyze_noise_core',['scripts/analyze_stage6_end_to_end.py','--task','core']),
 ('new_windows',['scripts/run_stage6_candidates.py','--task','windows']),
 ('B3_windows',['scripts/run_stage6_b3.py','--task','windows']),
 ('noise_windows',['scripts/run_stage6_end_to_end.py','--task','windows']),
 ('identifiability',['scripts/run_stage6_identifiability.py']),
 ('analyze_noise_windows',['scripts/analyze_stage6_end_to_end.py','--task','windows']),
 ('boundary_analysis',['scripts/analyze_stage6_boundaries.py']),
 ('new_low_map',['scripts/run_stage6_candidates.py','--task','low_map']),
 ('B3_low_map',['scripts/run_stage6_b3.py','--task','low_map']),
 ('noise_low_map',['scripts/run_stage6_maps.py','--task','low_map']),
 ('new_map',['scripts/run_stage6_candidates.py','--task','map']),
 ('noise_map',['scripts/run_stage6_maps.py','--task','map']),
]
for name,args in commands:
 guard();progress('main_queue_running',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_main_queue.py')
 with (OUT/f'verification/queue_{name}.log').open('a') as f:
  r=subprocess.run([sys.executable,*args],stdout=f,stderr=subprocess.STDOUT);assert r.returncode==0,(name,r.returncode)
 progress('main_queue',name,'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_main_queue.py')
print('N8 scientific queue completed',flush=True)
