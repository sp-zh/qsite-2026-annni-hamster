"""Keep continuous task observables separate from pure-state acceptance and labels."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
outputs=[]
for task,folder in [('development','failure_mechanisms'),('validation','failure_mechanisms'),('confirmation','confirmation'),('n12','n12_transfer'),('n12_192','n12_transfer')]:
 p=OUT/f'{folder}/{task}_paired_summary.json'
 if not p.exists():continue
 rows=json.loads(p.read_text())['rows'];groups={}
 for r in rows:
  for region in ['all',r['region']]:groups.setdefault((r['method'],region),[]).append(r)
 stats=[]
 for (method,region),rr in groups.items():
  metrics={}
  for field in ['epsilon_c','epsilon_sf','epsilon_mx','delta_e','fidelity']:
   v=np.array([r[field] for r in rr]);metrics[field]=dict(mean=float(v.mean()),median=float(np.median(v)),p95=float(np.quantile(v,.95)),minimum=float(v.min()),maximum=float(v.max()))
  stats.append(dict(method=method,region=region,coordinates=len(rr),observable_pass=sum(r['observable_pass'] for r in rr),state_pass=sum(r['state_pass'] for r in rr),joint_pass=sum(r['joint_pass'] for r in rr),observable_pass_state_fail=sum(r['observable_pass'] and not r['state_pass'] for r in rr),metrics=metrics))
 result=dict(task=task,source=str(p.relative_to(ROOT)),sha256=sha(p),rows=stats,scope='Descriptive fixed-coordinate statistics; p95 is an empirical error quantile, not a confidence bound. Observable fidelity does not itself establish independent physical phase labels. Original preparation thresholds unchanged.')
 dump(OUT/f'{folder}/{task}_observable_accuracy.json',result);outputs.append((task,len(stats)))
print(outputs)
