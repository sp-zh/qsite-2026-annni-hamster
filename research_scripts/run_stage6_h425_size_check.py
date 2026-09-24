"""Two registered larger-size controls in the released lane; no unbounded retry."""
import sys,subprocess,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
while True:
    guard();p=OUT/'verification/progress_free_lane_done.json'
    if p.exists() and json.loads(p.read_text())['completed']=='all':break
    time.sleep(15)
O=OUT/'floating_boundary_scan';registration=json.loads((O/'h425_N160_registration.json').read_text())
remaining=(datetime.fromisoformat(PLAN['deadline'])-datetime.now(timezone.utc)).total_seconds()
if remaining<5400:
    dump(O/'h425_size_not_run.json',dict(reason='Less than90minutes remain; preserve final verification budget',remaining_seconds=remaining,registration=registration))
else:
    worker=ROOT/'scripts/run_stage6_mps_bounded.py';assert sha(worker)==registration['worker_sha']
    rows=[];failures=[]
    for job in registration['jobs']:
        guard();base=O/'h425_size_jobs'/uid(dict(job=job,registration_sha=sha(O/'h425_N160_registration.json')));base.parent.mkdir(exist_ok=True)
        output=base.with_suffix('.result.json');jobfile=base.with_suffix('.job.json');dump(jobfile,dict(arguments=job,output=str(output)))
        progress('h425_size_running',job,'.venv/bin/python scripts/run_stage6_h425_size_check.py')
        if not output.exists():
            try:
                with base.with_suffix('.log').open('a') as f:
                    r=subprocess.run([str(ROOT/'.venv-tn/bin/python'),str(worker),'--jobfile',str(jobfile)],stdout=f,stderr=subprocess.STDOUT,timeout=registration['hard_timeout_per_job_seconds'])
                if r.returncode:raise RuntimeError(('MPS exit',r.returncode))
            except (subprocess.TimeoutExpired,RuntimeError) as error:
                failures.append(dict(arguments=job,error=str(error),disposition='executed_incomplete',log=str(base.with_suffix('.log').relative_to(ROOT))));dump(O/'h425_size_failures.json',failures)
        if output.exists():
            row=json.loads(output.read_text());assert sha(ROOT/row['archive'])==row['sha256'];rows.append(row);dump(O/'h425_size_index.json',rows)
    if rows:
        commands=[['scripts/analyze_stage6_mps.py','--task','h425_size'],['scripts/analyze_stage6_friedel.py','--task','h425_size'],['scripts/analyze_stage6_floating_evidence_v4.py'],['scripts/export_stage6_reference_v6.py'],['scripts/plot_stage6_reference_layers_v6.py']]
        for args in commands:
            with (OUT/'verification/h425_size_analysis.log').open('a') as f:
                r=subprocess.run([sys.executable,*args],stdout=f,stderr=subprocess.STDOUT)
            assert r.returncode==0,args
progress('h425_size_done','all','.venv/bin/python scripts/run_stage6_h425_size_check.py')
