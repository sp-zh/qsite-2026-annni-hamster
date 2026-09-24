"""Reuse the second lane after N12; no third heavy numerical worker."""
import sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
def run(name,args):
 guard();progress('final_analysis_running',name,'.venv/bin/python scripts/run_stage6_final_analysis_queue.py')
 with (OUT/f'verification/final_{name}.log').open('a') as log:
  r=subprocess.run([sys.executable,*args],stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,(name,r.returncode)
 progress('final_analysis',name,'.venv/bin/python scripts/run_stage6_final_analysis_queue.py')
while True:
 guard();p=OUT/'verification/progress_second_lane.json'
 if p.exists() and json.loads(p.read_text())['completed']=='n12_noise_analyze' and (OUT/'end_to_end/mitigation_frozen.json').exists():break
 time.sleep(15)
for task in ['confirmation','stability','n12','n12_192','n12_window']:
 run('summary_'+task,['scripts/summarize_stage6_candidates.py','--task',task])
run('attribution',['scripts/analyze_stage6_attribution_v2.py'])
run('confirmation_detection',['scripts/analyze_stage6_confirmation_detection.py'])
run('noise_confirmation',['scripts/run_stage6_end_to_end.py','--task','confirmation'])
for task in ['confirmation','n12']:
 run('analysis_'+task,['scripts/analyze_stage6_end_to_end.py','--task',task])
 run('regions_'+task,['scripts/summarize_stage6_noise_regions.py','--task',task])
 run('scopes_'+task,['scripts/analyze_stage6_reference_scope_audit.py','--task',task])
run('n12_boundary',['scripts/analyze_stage6_n12_window.py'])
while True:
 guard();p=OUT/'verification/progress_main_queue.json'
 if p.exists() and json.loads(p.read_text())['completed'] in ['boundary_analysis','new_low_map','B3_low_map','noise_low_map','new_map','noise_map']:break
 time.sleep(15)
for name,args in [
 ('branch_switches',['scripts/analyze_stage6_branch_switches.py']),
 ('D2',['scripts/run_stage6_d2_windows.py']),
 ('detector_boundaries',['scripts/analyze_stage6_detector_boundaries.py']),
 ('variance_extension',['scripts/run_stage6_variance_extension.py']),
 ('identifiability',['scripts/analyze_stage6_identifiability.py']),
 ('cross_structure',['scripts/analyze_stage6_cross_structure.py'])]:run(name,args)
for task in ['validation','core','windows']:
 run('regions_'+task,['scripts/summarize_stage6_noise_regions.py','--task',task])
 run('scopes_'+task,['scripts/analyze_stage6_reference_scope_audit.py','--task',task])
progress('final_analysis_done','all','.venv/bin/python scripts/run_stage6_final_analysis_queue.py')
