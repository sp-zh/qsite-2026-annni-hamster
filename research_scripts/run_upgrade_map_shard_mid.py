"""Independent far-ahead map shard; same frozen key/config, isolated index.
The main runner later reuses the completed hashed records. No chain continuation.
"""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
O=OUT/'map_shard_mid_k';O.mkdir(exist_ok=True);rows=[];start=time.perf_counter()
for k,h in PLAN['final_map']:
 if not .6<=k<.8:continue
 main=json.loads((OUT/'map/progress.json').read_text());last=(main['last_kappa'],main['last_h'])
 # Never race the main worker on a coordinate. If it catches up, stop this shard.
 if last>=(k,h):continue
 if last[0]>=k-.05:
  print('Main worker approaching shard; stop before overlapping writes',flush=True);break
 candidates=[adaptive(8,k,h,ref,11,128,'cost',True,'map') for ref in PLAN['refs']]
 candidates=[{key:value for key,value in r.items() if key not in ['steps','checkpoints']}|dict(run_record=str(Path(r['archive']).with_suffix('.json'))) for r in candidates];rows.append(dict(n=8,kappa=k,h=h,methods={'B3':select(candidates)},candidates=candidates))
 if len(rows)%5==0:
  dump(O/'index.json',rows);print(len(rows),round(time.perf_counter()-start,2),flush=True)
dump(O/'index.json',rows);dump(O/'metadata.json',dict(config_sha256=sha(OUT/'experiment_plan.json'),source_fingerprint=fp(),scope='0.6<=kappa<0.8 map points, identical frozen protocol',elapsed_seconds=time.perf_counter()-start,cache_disposition='new computations; reused by main map runner',no_shared_index_mutation=True))
