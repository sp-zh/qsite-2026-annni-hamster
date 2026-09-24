"""Use the released N8 lane; never add a third primary numerical worker."""
import sys,subprocess,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
while True:
    guard();p=OUT/'verification/progress_main_queue.json'
    if p.exists() and json.loads(p.read_text())['completed']=='noise_map':break
    time.sleep(15)
def execute(name,command):
    guard();progress('free_lane_running',name,'.venv/bin/python scripts/run_stage6_free_lane.py')
    with (OUT/f'verification/free_lane_{name}.log').open('a') as f:
        r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0,(name,r.returncode)
    progress('free_lane',name,'.venv/bin/python scripts/run_stage6_free_lane.py')
execute('confirmation_noise',[sys.executable,'scripts/run_stage6_end_to_end.py','--task','confirmation'])
O=OUT/'floating_boundary_scan';registration=json.loads((O/'final_continuation_registration.json').read_text())
remaining=(datetime.fromisoformat(PLAN['deadline'])-datetime.now(timezone.utc)).total_seconds()
if remaining<3600:
    dump(O/'final_continuation_not_run.json',dict(reason='Less than one hour remains; protect final verification and packaging',remaining_seconds=remaining,registration=registration))
else:
    job=registration['arguments'];worker=ROOT/'scripts/run_stage6_mps_bounded.py'
    assert sha(worker)==registration['worker_sha']
    assert sha(ROOT/job['resume'])==registration['resume_sha']
    base=O/'final_continuation_jobs'/uid(registration);base.parent.mkdir(exist_ok=True)
    output=base.with_suffix('.result.json');jobfile=base.with_suffix('.job.json')
    dump(jobfile,dict(arguments=job,output=str(output)))
    if not output.exists():
        try:
            with base.with_suffix('.log').open('a') as f:
                r=subprocess.run([str(ROOT/'.venv-tn/bin/python'),str(worker),'--jobfile',str(jobfile)],stdout=f,stderr=subprocess.STDOUT,timeout=registration['hard_timeout_seconds'])
            if r.returncode:raise RuntimeError(('MPS exit',r.returncode))
        except (subprocess.TimeoutExpired,RuntimeError) as error:
            dump(O/'final_continuation_failures.json',[dict(arguments=job,error=str(error),disposition='executed_incomplete',log=str(base.with_suffix('.log').relative_to(ROOT)))])
    if output.exists():
        row=json.loads(output.read_text());assert sha(ROOT/row['archive'])==row['sha256']
        dump(O/'final_continuation_index.json',[row])
        for script in ['analyze_stage6_mps.py','analyze_stage6_friedel.py']:
            execute(script,[sys.executable,'scripts/'+script,'--task','final_continuation'])
        execute('evidence_v3',[sys.executable,'scripts/analyze_stage6_floating_evidence_v3.py'])
        execute('atlas_v5',[sys.executable,'scripts/export_stage6_reference_v5.py'])
        execute('atlas_v5_plot',[sys.executable,'scripts/plot_stage6_reference_layers_v5.py'])
progress('free_lane_done','all','.venv/bin/python scripts/run_stage6_free_lane.py')
