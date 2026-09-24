"""Local completion queue; waits for real N12 outputs, never extends deadline."""
import json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';P=json.loads((O/'experiment_plan.json').read_text())
needed={'n12_scaling/noise_index.json':12,'end_to_end/n12_index.json':6}
while True:
 if datetime.now(timezone.utc)>=datetime.fromisoformat(P['deadline']):raise TimeoutError('Original run deadline reached')
 if all((O/p).exists() and len(json.loads((O/p).read_text()))==count for p,count in needed.items()):break
 time.sleep(30)
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(R/'.mplconfig'))
commands=[['bash','scripts/reproduce_stage5.sh','--report-only'],[sys.executable,'scripts/stage5_metadata.py'],[sys.executable,'-m','pytest','-q'],[sys.executable,'scripts/verify_stage5.py'],[sys.executable,'scripts/finalize_stage5.py']]
for i,cmd in enumerate(commands):
 print(datetime.now(timezone.utc).isoformat(),'Starting',cmd,flush=True)
 with (O/'verification'/f'final_queue_{i}.log').open('w') as f:subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
print('Numerics, notebook, final tests, metadata and ledger complete. Export QA and packaging remain.',flush=True)
