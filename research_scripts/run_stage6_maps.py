import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_arms import *
from annni.stage6_estimators import measurement as measured
from annni.stage6_index_records import compact_measurement_record
parser=argparse.ArgumentParser();parser.add_argument('--task',default='map');parser.add_argument('--start',type=int);parser.add_argument('--stop',type=int);a=parser.parse_args();task=a.task;f=json.loads((OUT/'confirmation/method_frozen.json').read_text());mf=json.loads((OUT/'end_to_end/mitigation_frozen.json').read_text());new=f['physical_method']
if task=='map':
 baseline=np.load(ROOT/'results/baseline/grid_n8.npz');points=[dict(kappa=float(k),h=float(h)) for k in baseline['kappa'] for h in baseline['h'] if h>0]
else:points=[dict(kappa=k,h=h) for k in PLAN['atlas']['low_kappa'] for h in PLAN['atlas']['low_h']]
partition=OUT/'n8_maps/map_execution_partitions.json'
if a.start is None:
 a.start=0
 if task=='map' and partition.exists():
  part=json.loads(partition.read_text())['primary'];a.start=part['start'];a.stop=part['stop'] if a.stop is None else a.stop
rows=[]
for i,point in list(enumerate(points))[a.start:a.stop]:
 entries=[];sources=[]
 for method in ['B3',new]:
  r=load(point['kappa'],point['h'],method,task='historical_map' if method=='B3' and task=='map' else task);sources.append(dict(method=method,archive=r['source_archive'],state_disposition='historical_reused' if method=='B3' and task=='map' else 'newly_executed'))
  for p in [0,.01,.05]:
   for estimator in dict.fromkeys(['raw',mf['selected'][method]]):
    m=measured(r,p,estimator);entries.append(dict(method=method,estimator=estimator,record=compact_measurement_record(m)))
 rows.append(dict(n=8,**point,entries=entries,sources=sources));dump(OUT/f'end_to_end/{task}_{a.start}_index.json',rows);print(task,i+1,flush=True);progress(task+'_noise',len(rows),f'.venv/bin/python scripts/run_stage6_maps.py --task {task} --start {a.start}',last_index=i)
