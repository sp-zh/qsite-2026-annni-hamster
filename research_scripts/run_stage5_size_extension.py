"""One predeclared optional N160 check of the known (1,.7) size anomaly."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_stage5_floating import run,O,dump,PLAN,np
cfg=json.loads((O/'size_extension_plan.json').read_text());index=O/'size_extension_index.json'
if index.exists() and len(json.loads(index.read_text()))>=2:
 rows=json.loads(index.read_text())
else:
 assert len(json.loads((O/'index.json').read_text()))==39
 requests=json.loads((O/'chi512_requests.json').read_text());follow=json.loads((O/'chi512_index.json').read_text());assert len(follow)==len(requests)
 remaining=(datetime.fromisoformat(PLAN['deadline'])-datetime.now(timezone.utc)).total_seconds()
 if remaining<7200:
  dump(O/'size_extension_status.json',dict(executed=False,reason='Fewer than2h remain; optional extension not started',remaining_seconds=remaining));sys.exit(0)
 rows=[]
 for chi in cfg['chi']:
  rows.append(run(cfg['n'],*cfg['point'],chi,cfg['initial']));dump(index,rows)
a=np.load(Path(__file__).resolve().parents[1]/rows[0]['archive']);b=np.load(Path(__file__).resolve().parents[1]/rows[1]['archive']);de=abs(rows[0]['energy']-rows[1]['energy'])/cfg['n'];dc=float(max(abs(a['central_raw']-b['central_raw'])));ds=float(max(abs(a['entropy']-b['entropy'])));trigger=de>=1e-5 or dc>=.01 or ds>=.03
if trigger and len(rows)<3:
 remaining=(datetime.fromisoformat(PLAN['deadline'])-datetime.now(timezone.utc)).total_seconds()
 if remaining>=3600:rows.append(run(cfg['n'],*cfg['point'],512,cfg['initial']));dump(index,rows)
dump(O/'size_extension_status.json',dict(executed=True,completed=len(rows),bond_comparison_128_256=dict(delta_e_per_site=de,delta_c=dc,delta_entropy=ds),chi512_triggered=trigger,chi512_executed=len(rows)==3,scope='One predeclared extra size for known old c anomaly, one optimization path; distinct from main two-initial-state validation.'))
