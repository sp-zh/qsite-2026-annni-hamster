"""Bounded progress ledger; no claims of detached continuation."""
import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
now=datetime.now(timezone.utc);records={p.stem:json.loads(p.read_text()) for p in (OUT/'verification').glob('progress_*.json')};active=[]
try:
 result=subprocess.run(['ps','-axo','pid,etime,%cpu,rss,command'],capture_output=True,text=True)
 if result.returncode==0:active=[line for line in result.stdout.splitlines() if 'python' in line.lower() and 'stage6' in line and 'snapshot_stage6' not in line]
 else:active=['Process listing unavailable under current sandbox: '+result.stderr.strip()]
except OSError as error:active=[str(error)]
row=dict(time=now.isoformat(),deadline=PLAN['deadline'],elapsed_seconds=(now-datetime.fromisoformat(PLAN['started_utc'])).total_seconds(),progress=records,process_snapshot=active,remaining_seconds=(datetime.fromisoformat(PLAN['deadline'])-now).total_seconds(),resource_policy='At most two heavy workers; BLAS/OMP one thread. 6GiB working-memory budget, not OS-enforced.')
dump(OUT/'verification/progress_snapshots'/f'{now:%Y%m%dT%H%M%SZ}.json',row)
print(now.isoformat(),len(records),'progress records')
