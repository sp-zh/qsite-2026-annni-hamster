"""Exact-coordinate, exact-literal-circuit historical B5 controls. No substitutions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
points=json.loads((OUT/'failure_mechanisms/benchmark.json').read_text())['points']+[PLAN['confirmation'][i] for i in [0,8,16,24,32,40,48,56,64,72,80,88]];wanted={(p['kappa'],p['h']) for p in points};records={};sources=[]
for name in ['core_index','full_raw_index','full_best_index']:
 p=ROOT/f'results/stage5_v1/end_to_end/{name}.json';sources.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)))
 for point in json.loads(p.read_text()):
  if (point['kappa'],point['h']) not in wanted:continue
  for e in point['entries']:
   if not e['arm'].startswith('B5_'):continue
   r=e['record'];key=(point['kappa'],point['h'],r['p'],r['method'],uid(r['key']['gates']));records.setdefault(key,r)
rows=[]
for point in points:
 k,h=point['kappa'],point['h']
 try:arm=load(k,h,'B5',task='historical_map')
 except FileNotFoundError:rows.append(dict(**point,status='historical_B5_circuit_unavailable'));continue
 available=[]
 for p in [0,.01,.05]:
  for method in ['raw','zne','sv']:
   r=records.get((k,h,p,method,uid(arm['gates'])))
   if r is None:continue
   assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);available.append(dict(p=p,estimator=method,archive=r['archive'],sha256=r['sha256'],cost=r['cost'],replicates=a['samples_100000'].shape[0],MSE_ED_100k=float(np.mean((a['samples_100000']-a['ed'])**2)),MSE_own_p0_100k=float(np.mean((a['samples_100000']-a['ideal'])**2)),disposition='historical_reused_exact_coordinate_gates'))
 rows.append(dict(**point,status='matched' if available else 'no_matching_historical_measurements',circuit=arm['source_archive'],gates_sha=uid(arm['gates']),measurements=available))
dump(OUT/'end_to_end/B5_historical_matched.json',dict(rows=rows,sources=sources,rule='Only exact coordinates and literal gate-table identity, no approximate coordinate match or replacement structure. Historical seed/selection remains distinct from new B3/H6 independent runs. Missing common-cohort entries explicit.',new_measurements=0));print('Historical B5 matched',sum(bool(r.get('measurements')) for r in rows),'of',len(rows))
