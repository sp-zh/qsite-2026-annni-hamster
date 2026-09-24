"""Targeted remaining convergence controls, before the N12 lane begins."""
import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';worker=ROOT/'scripts/run_stage6_mps_bounded.py';available=[]
for task in ['bounded','followup']:
 p=O/f'{task}_index.json'
 if p.exists():available+=json.loads(p.read_text())
jobs=[dict(n=128,k=.8,h=.4,chi=256,initial='antiphase',sweeps=24,max_seconds=300),dict(n=128,k=.8,h=.35,chi=512,initial='plus',sweeps=24,max_seconds=600)]
jobs += [dict(n=128,k=.8,h=.425,chi=256,initial=initial,sweeps=24,max_seconds=300) for initial in ['plus','antiphase']]
rows=[];failures=[]
for job in jobs:
 guard();sources=[r for r in available if r['n']==job['n'] and r['h']==job['h'] and r['initial']==job['initial'] and r['chi']<=job['chi']];source=max(sources,key=lambda r:(r['chi'],available.index(r))) if sources else None;args=dict(job,**({'resume':source['checkpoint']} if source else {}));key=dict(arguments=args,worker_sha=sha(worker));base=O/'control_jobs'/uid(key);base.parent.mkdir(exist_ok=True);output=base.with_suffix('.result.json');jobfile=base.with_suffix('.job.json');dump(jobfile,dict(arguments=args,output=str(output)))
 if output.exists():r=json.loads(output.read_text());assert sha(ROOT/r['archive'])==r['sha256']
 else:
  progress('mps_controls',len(rows),'.venv-tn/bin/python scripts/run_stage6_mps_controls.py',running_job=args)
  try:
   with base.with_suffix('.log').open('a') as log:result=subprocess.run([sys.executable,str(worker),'--jobfile',str(jobfile)],stdout=log,stderr=subprocess.STDOUT,timeout=job['max_seconds']+180)
   if result.returncode:raise RuntimeError(str(result.returncode))
   r=json.loads(output.read_text())
  except (RuntimeError,subprocess.TimeoutExpired) as error:failures.append(dict(arguments=args,error=str(error),disposition='executed_incomplete'));dump(O/'controls_failures.json',failures);continue
 rows.append(r);dump(O/'controls_index.json',rows);print('control',job,r['solver_stopping_pass'],flush=True)
dump(O/'controls_failures.json',failures);progress('mps_controls_done',len(rows),'.venv-tn/bin/python scripts/run_stage6_mps_controls.py')
