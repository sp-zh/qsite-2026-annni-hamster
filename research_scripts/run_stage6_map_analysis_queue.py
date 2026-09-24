"""Postprocess only after the N8 numerical lane has finished; no third heavy worker."""
import sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
while True:
 guard();p=OUT/'verification/progress_main_queue.json'
 if p.exists() and json.loads(p.read_text())['completed']=='noise_map':break
 time.sleep(15)
commands=[]
for task in ['low_map','map']:
 commands += [('analyze_'+task,['scripts/analyze_stage6_maps.py','--task',task]),('plot_'+task,['scripts/plot_stage6_maps.py','--task',task])]
for task in ['windows','low_map']:
 commands += [('summary_'+task,['scripts/summarize_stage6_candidates.py','--task',task]),('plot_candidates_'+task,['scripts/plot_stage6_candidates.py','--task',task])]
commands += [('boundary_coordinate_denominators',['scripts/summarize_stage6_boundary_denominators.py']),('plot_noise',['scripts/plot_stage6_noise.py'])]
for name,args in commands:
 guard();progress('map_analysis_running',name,'.venv/bin/python scripts/run_stage6_map_analysis_queue.py')
 with (OUT/f'verification/map_analysis_{name}.log').open('a') as log:
  r=subprocess.run([sys.executable,*args],stdout=log,stderr=subprocess.STDOUT);assert r.returncode==0,(name,r.returncode)
 progress('map_analysis',name,'.venv/bin/python scripts/run_stage6_map_analysis_queue.py')
progress('map_analysis_done','all','.venv/bin/python scripts/run_stage6_map_analysis_queue.py')
