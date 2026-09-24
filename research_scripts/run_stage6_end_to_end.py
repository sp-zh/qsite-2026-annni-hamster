import sys,argparse,fcntl
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_arms import *
from annni.stage6_estimators import measurement as measured
from annni.stage6_index_records import compact_measurement_record
from annni.stage6_checkpoint_index import save_measurement_prefix
parser=argparse.ArgumentParser();parser.add_argument('--task',default='core');parser.add_argument('--start',type=int,default=0);parser.add_argument('--stop',type=int);args=parser.parse_args();task=args.task;frozen=json.loads((OUT/'confirmation/method_frozen.json').read_text());new=frozen['physical_method'];n=8
# Serialize replay of the same output partition. This changes orchestration only:
# scientific cache keys, random streams, estimators and parameters are unchanged.
partition_lock=(OUT/f'verification/noise_partition_{task}_{args.start}.lock').open('a')
fcntl.flock(partition_lock,fcntl.LOCK_EX)
if task=='core':points=json.loads((OUT/'failure_mechanisms/benchmark.json').read_text())['points']+[PLAN['confirmation'][i] for i in [0,8,16,24,32,40,48,56,64,72,80,88]]
elif task=='confirmation':points=PLAN['confirmation']
elif task=='validation':points=[dict(kappa=k,h=h) for k,h in PLAN['validation']]
elif task=='windows':points=[r for r in json.loads((OUT/'reference_atlas/circuit_window_coordinates.json').read_text()) if r['kappa'] in [.45,.55,.8]]
elif task=='n12':points=json.loads((OUT/'n12_transfer/noise_coordinates.json').read_text());n=12
else:raise ValueError(task)
rows=[]
for i,point in list(enumerate(points))[args.start:args.stop]:
 k,h=point['kappa'],point['h'];entries=[];source=[]
 for name in ['B3',new]+(['B0'] if n==8 and task in ['core','validation'] else []):
  source_task=('development' if i<36 else 'confirmation') if task=='core' else point.get('source_task',task);armrow=hva(k,h) if name=='B0' else load(k,h,name,n,task=source_task);source.append(dict(method=name,archive=armrow['source_archive']))
  for p in [0,.01,.05]:
   for estimator in (list(dict.fromkeys(['raw',json.loads((OUT/'end_to_end/mitigation_frozen.json').read_text())['selected'][name]])) if task=='confirmation' else ['raw'] if name=='B0' or n==12 else ['raw','zne','zne_quadratic','sv']):
    r=measured(armrow,p,estimator);entries.append(dict(method=name,estimator=estimator,record=compact_measurement_record(r)));print(task,i,name,p,estimator,flush=True)
 rows.append(dict(n=n,**point,entries=entries,sources=source));save_measurement_prefix(OUT/f'end_to_end/{task}_{args.start}_index.json',rows);progress('noise_'+task,len(rows),f'.venv/bin/python scripts/run_stage6_end_to_end.py --task {task} --start {args.start}',last_index=i)
if task=='n12' and args.start==0 and args.stop==1 and rows:
 unique={p['archive']:p for point in rows for e in point['entries'] for p in e['record']['probability_records']}
 measured_seconds=sum(p['seconds'] for p in unique.values())
 dump(OUT/'n12_transfer/density_pilot_cost.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),coordinates=[dict(kappa=r['kappa'],h=r['h']) for r in rows],unique_physical_records=len(unique),summed_density_probability_seconds=measured_seconds,peak_rss_bytes=max(p['process_peak_rss_bytes'] for p in unique.values()),records=list(unique.values()),remaining_wall_seconds=(datetime.fromisoformat(PLAN['deadline'])-datetime.now(timezone.utc)).total_seconds(),naive_12_coordinate_seconds_estimate=12*measured_seconds,estimate_scope='Estimate only from one actual coordinate and its selected circuits; different CNOT counts and cache reuse can change cost substantially. Not an observed full-batch duration or a completion guarantee. Parameters, noise and N are unchanged.'))
