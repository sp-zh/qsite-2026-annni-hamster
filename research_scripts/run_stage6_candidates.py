import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_candidates import *
from annni.stage6_hybrid import components
parser=argparse.ArgumentParser();parser.add_argument('--task',default='development');parser.add_argument('--start',type=int,default=0);parser.add_argument('--stop',type=int);parser.add_argument('--seed',type=int);args=parser.parse_args()
task=args.task
if task=='development':points=json.loads((OUT/'failure_mechanisms/benchmark.json').read_text())['points'];methods=['C0','C1','C2','C3'];seed=101;n=8;budget=128
elif task=='validation':points=[dict(kappa=k,h=h) for k,h in PLAN['validation']];methods=['C0','C1','C2','C3'];seed=419;n=8;budget=128
else:
 frozen=json.loads((OUT/'confirmation/method_frozen.json').read_text());assert frozen['candidate_code']==sha(ROOT/'annni/stage6_candidates.py');assert frozen['runner_sha']==sha(__file__);assert frozen['hybrid_code']==sha(ROOT/'annni/stage6_hybrid.py')
 points=PLAN['confirmation'];methods=['C0']+frozen['methods'];seed=631;n=8;budget=128
 if task.startswith('n12'):
  points=json.loads((OUT/'n12_transfer/coordinates.json').read_text());methods=['C0','C1',frozen['physical_method']];methods=list(dict.fromkeys(methods));n=12;budget=192 if task=='n12_192' else 128
 if task=='n12_192':points=points[::3]
 if task=='n12_window':points=json.loads((OUT/'n12_transfer/window_coordinates.json').read_text())
 if task=='stability':points=[PLAN['confirmation'][i] for i in [0,8,16,24,32,40,48,56,64,72,80,88]]
 if task=='map':
  a=np.load(ROOT/'results/baseline/grid_n8.npz');points=[dict(kappa=float(k),h=float(h)) for k in a['kappa'] for h in a['h'] if h>0];methods=[frozen['physical_method']]
 if task=='low_map':points=[dict(kappa=k,h=h) for k in PLAN['atlas']['low_kappa'] for h in PLAN['atlas']['low_h']];methods=['C0',frozen['physical_method']]
 if task=='windows':points=json.loads((OUT/'reference_atlas/circuit_window_coordinates.json').read_text());methods=['C0',frozen['physical_method']]
seed=args.seed or seed
def compact(r):
 p=Path(r['archive']).with_suffix('.json');return dict({k:v for k,v in r.items() if k!='steps'},raw_record=str(p),raw_record_sha=sha(ROOT/p))
rows=[]
seen_archives={str(p.relative_to(ROOT)) for p in (OUT/'domain_wall_candidates/cache').glob('*.npz')}
for i,point in list(enumerate(points))[args.start:args.stop]:
 k,h=point['kappa'],point['h'];result=dict(n=n,kappa=k,h=h,task=task,region=point.get('region'),methods={})
 for method in methods:
  component_list=components(method,k,h,frozen['wall_component'] if method=='H6' else None);runs=[];events=[]
  for component in component_list:
   basis='physical' if component in ['C0','C1'] else 'wall';search='top4' if component in ['C1','C3'] else 'greedy';refs=PLAN['search']['refs_physical' if basis=='physical' else 'refs_wall']
   for ref in refs:
    t=time.perf_counter();r=adaptive(n,k,h,basis,ref,search,seed,budget,task);events.append(dict(archive=r['archive'],cache_hit_before_call=r['archive'] in seen_archives,call_seconds=time.perf_counter()-t,source_execution_seconds=r['seconds']));seen_archives.add(r['archive']);runs.append(r)
  chosen=select(runs);result['methods'][method]=dict(execution_events=events,components=component_list,selected=compact(chosen),run_keys=[r['key'] for r in runs],runs=[str((OUT/'domain_wall_candidates/cache'/ (uid(r['key'])+'.json')).relative_to(ROOT)) for r in runs]);print(task,i,method,k,h,round(sum(r['seconds'] for r in runs),2),flush=True)
 rows.append(result);dump(OUT/f'domain_wall_candidates/{task}_{seed}_{args.start}_index.json',rows);progress('candidates_'+task,len(rows),f'.venv/bin/python scripts/run_stage6_candidates.py --task {task} --start {args.start} --seed {seed}',last_index=i)
