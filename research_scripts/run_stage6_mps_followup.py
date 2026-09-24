"""One bounded follow-up slice, preserving failed and time-shelved DMRG runs."""
import sys,subprocess,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';worker=ROOT/'scripts/run_stage6_mps_bounded.py'
# Frozen refinement grid based on coarse q/decay/response and independent literature guidance,
# not selection for c closest to1. Two sides and finite-N trends included.
jobs=[]
for h in [.3125,.3375,.375,.425,.45,.475,.4875]:
 for n in [96,128]:jobs.append(dict(n=n,k=.8,h=h,chi=128,initial='plus',sweeps=32,max_seconds=360))
for h in [.45,.475]:
 for initial in ['plus','antiphase']:jobs.append(dict(n=128,k=.8,h=h,chi=256,initial=initial,sweeps=32,max_seconds=480))
jobs.append(dict(n=160,k=.8,h=.4,chi=256,initial='plus',sweeps=32,max_seconds=600))
for chi in [128,256]:jobs.append(dict(n=192,k=.8,h=.5,chi=chi,initial='plus',sweeps=32,max_seconds=600))
# Controlled resume of a relevant nonconverged branch; same initial chain, not a new repeat.
jobs.append(dict(n=128,k=.8,h=.4,chi=256,initial='plus',sweeps=24,max_seconds=600))
jobs.insert(0,jobs.pop()) # Prioritize completing the already sampled h=.4 initial-chain control.
for initial in ['plus','antiphase']:
 jobs.insert(1,dict(n=96,k=.8,h=.4,chi=256,initial=initial,sweeps=32,max_seconds=360))
# Larger-size checks precede the finest optional upper-edge points under the same90min cap.
def priority(j):
 if j['h']==.4 and j['n'] in [96,128]:return 0
 if j['h'] in [.3125,.3375]:return 1
 if j['h'] in [.425,.45,.475] and j['chi']==128:return 2
 if j['h']==.45 and j['chi']==256:return 3
 if j['n']>=160:return 4
 if j['h']==.375:return 5
 if j['h']==.475:return 6
 return 7
jobs.sort(key=priority)
plan=dict(created=datetime.now(timezone.utc).isoformat(),jobs=jobs,wall_cap_seconds=5400,reason='Fill lower .30-.35 and upper .40-.50 windows, examine intermediate .375/.425, compare two independent product-state chains at .45/.475; targeted N160 at .4 and N192 at .5 distinguish finite N from chi, especially the old(.8,.5) center with c near1 but unstable/noncritical Friedel fits. No extra isolated floating-center scan.',worker_sha=sha(worker))
p=O/'followup_plan.json'
if p.exists():old=json.loads(p.read_text());assert old['jobs']==jobs and old['worker_sha']==sha(worker)
else:dump(p,plan)
start=time.perf_counter();rows=[];failures=[];oldrows=json.loads((O/'bounded_index.json').read_text())
for job in jobs:
 if time.perf_counter()-start>plan['wall_cap_seconds']-min(job['max_seconds'],300):
  dump(O/'followup_stop.json',dict(reason='bounded_followup_wall_cap',remaining_jobs=jobs[len(rows)+len(failures):],seconds=time.perf_counter()-start));break
 guard();args=dict(job)
 if job['initial']=='plus':
  sources=[r for r in oldrows+rows if r['n']==job['n'] and r['h']==job['h'] and r['initial']=='plus' and r['chi']<=job['chi']]
  if sources:args['resume']=max(sources,key=lambda r:r['chi'])['checkpoint']
 key=dict(arguments=args,worker_sha=sha(worker));path=O/'followup_jobs'/uid(key);path.parent.mkdir(exist_ok=True);output=path.with_suffix('.result.json');jobfile=path.with_suffix('.job.json');dump(jobfile,dict(arguments=args,output=str(output)))
 if output.exists():r=json.loads(output.read_text());assert r['key']['code']==sha(worker) and sha(ROOT/r['archive'])==r['sha256']
 else:
  progress('mps_followup',len(rows),'.venv-tn/bin/python scripts/run_stage6_mps_followup.py',running_job=args)
  try:
   with path.with_suffix('.log').open('a') as f:result=subprocess.run([sys.executable,str(worker),'--jobfile',str(jobfile)],stdout=f,stderr=subprocess.STDOUT,timeout=job['max_seconds']+180)
   if result.returncode:raise RuntimeError(str(result.returncode))
   r=json.loads(output.read_text())
  except (subprocess.TimeoutExpired,RuntimeError) as error:
   failures.append(dict(job=args,error=str(error),log=str(path.with_suffix('.log').relative_to(ROOT)),disposition='executed_incomplete'));dump(O/'followup_failures.json',failures);continue
 rows.append(r);dump(O/'followup_index.json',rows);print('followup',len(rows),r['n'],r['h'],r['chi'],r['solver_stopping_pass'],flush=True)
dump(O/'followup_failures.json',failures);progress('mps_followup_done',len(rows),'.venv-tn/bin/python scripts/run_stage6_mps_followup.py',seconds=time.perf_counter()-start,failures=len(failures))
