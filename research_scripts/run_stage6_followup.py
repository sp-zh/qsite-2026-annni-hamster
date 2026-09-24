import sys,argparse,time,fcntl
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
import annni.stage6_followup as engine
# Read-only parsed-input cache. No probability, allocation, RNG or estimator changes.
_read_uncached=engine.read
_input_cache={}
def cached_input_read(path):
 path=Path(path)
 if path.name not in ['config.json','inputs.json','historical_measurements.json']:
  return _read_uncached(path)
 key=(str(path),path.stat().st_mtime_ns)
 if key not in _input_cache:_input_cache[key]=_read_uncached(path)
 return _input_cache[key]
engine.read=cached_input_read
p=argparse.ArgumentParser();p.add_argument('--task',choices=['pilot','A','B'],required=True);a=p.parse_args();inputs=list(read(OUT/'inputs.json').values());refs=read(OUT/'window_reference.json');start=time.perf_counter()
lock=(OUT/f'verification/partition_{a.task}.lock').open('a')
fcntl.flock(lock,fcntl.LOCK_EX)
def save_index(rows):
 path=OUT/f'{a.task}_index.json'
 if path.exists():
  previous=read(path)
  if len(previous)>len(rows):
   if previous[:len(rows)]!=rows:raise ValueError('Scientific index prefix changed; inspect fingerprint before resume')
   return
 dump(path,rows)
if a.task in ['pilot','A']:
 ordered=[w for k in [0,.3,.5,.45,.55,.8] for w in refs if w['kappa']==k]
 points=[point(w['kappa'],float(h)) for w in ordered for h in w['h']]
 if a.task=='pilot':points=points[:1]
 modes=[('equal_shots',b) for b in cfg()['shots']]
else:
 coords={(x['kappa'],x['h']) for x in cfg()['representatives']};coords.update((w['kappa'],float(h)) for w in refs if w['kappa'] in cfg()['equal_gate_windows'] for h in w['h']);points=[point(k,h) for k,h in sorted(coords)];modes=[('equal_shots',100000)]+[('equal_gate',b) for b in cfg()['equal_gate_base_budgets']]
rows=[]
for i,row in enumerate(points):
 records=[]
 for mode,budget in modes:
  for p in cfg()['p']:
   for method in ['raw','zne_quadratic','sv']:
    r=measure(row,p,method,mode,budget);records.append(str((OUT/'measurements'/f"{uid(r['key'])}.json").relative_to(ROOT)))
 rows.append(dict(point_id=row['id'],kappa=row['kappa'],h=row['h'],records=records));save_index(rows);dump(OUT/'verification/progress.json',dict(task=a.task,completed_coordinates=len(rows),requested_coordinates=len(points),elapsed_seconds=time.perf_counter()-start,updated_utc=datetime.now(timezone.utc).isoformat(),resume=f'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_stage6_followup.py --task {a.task}'))
 print(a.task,i+1,len(points),row['kappa'],row['h'],round(time.perf_counter()-start,2),flush=True)
dump(OUT/f'verification/{a.task}_completion.json',dict(status='complete',coordinates=len(points),seconds=time.perf_counter()-start,time=datetime.now(timezone.utc).isoformat()))
