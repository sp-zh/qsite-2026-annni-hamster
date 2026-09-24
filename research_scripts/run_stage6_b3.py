import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_legacy import adaptive,select
parser=argparse.ArgumentParser();parser.add_argument('--task',default='development');parser.add_argument('--seed',type=int);args=parser.parse_args();task=args.task
if task=='development':points=json.loads((OUT/'failure_mechanisms/benchmark.json').read_text())['points'];seed=101;n=8;budget=128
elif task=='validation':points=[dict(kappa=k,h=h) for k,h in PLAN['validation']];seed=419;n=8;budget=128
elif task=='stability':points=[PLAN['confirmation'][i] for i in [0,8,16,24,32,40,48,56,64,72,80,88]];seed=args.seed or 743;n=8;budget=128
elif task=='confirmation':points=PLAN['confirmation'];seed=631;n=8;budget=128
elif task in ['n12','n12_192']:points=json.loads((OUT/'n12_transfer/coordinates.json').read_text());seed=631;n=12;budget=192 if task=='n12_192' else 128
elif task=='n12_window':points=json.loads((OUT/'n12_transfer/window_coordinates.json').read_text());seed=631;n=12;budget=128
elif task=='windows':points=json.loads((OUT/'reference_atlas/circuit_window_coordinates.json').read_text());seed=631;n=8;budget=128
elif task=='low_map':points=[dict(kappa=k,h=h) for k in PLAN['atlas']['low_kappa'] for h in PLAN['atlas']['low_h']];seed=631;n=8;budget=128
else:raise ValueError(task)
if task=='n12_192':points=points[::3]
seed=args.seed or seed
def compact(r):
 p=Path(r['archive']).with_suffix('.json');return dict({k:v for k,v in r.items() if k!='steps'},raw_record=str(p),raw_record_sha=sha(ROOT/p))
rows=[]
seen_archives={str(p.relative_to(ROOT)) for p in (OUT/'legacy_b3/adaptive/cache').glob('*.npz')}
for i,p in enumerate(points):
 runs=[];events=[]
 for ref in ['plus','ghz','antiphase']:
  t=time.perf_counter();r=adaptive(n,p['kappa'],p['h'],ref,seed,budget=budget,group=task);events.append(dict(archive=r['archive'],cache_hit_before_call=r['archive'] in seen_archives,call_seconds=time.perf_counter()-t,source_execution_seconds=r['seconds']));seen_archives.add(r['archive']);runs.append(r)
 chosen=select(runs);rows.append(dict(n=n,**p,selected=compact(chosen),runs=[compact(r) for r in runs],execution_events=events));dump(OUT/f'legacy_b3/{task}{"_"+str(seed) if task=="stability" else ""}_index.json',rows);print(task,i+1,round(sum(r['seconds'] for r in runs),2),flush=True)
