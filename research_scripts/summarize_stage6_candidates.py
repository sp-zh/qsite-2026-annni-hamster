"""Paired coordinate-level preparation results, independent of phase labels.
No generation or selection is changed by this post-hoc evaluation.
"""
import sys,argparse,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_rows
from annni.stage6_assess import assess_run
parser=argparse.ArgumentParser();parser.add_argument('--task',default='confirmation');task=parser.parse_args().task
source=candidate_rows(task);rows=[]
if task=='confirmation':assert (OUT/'confirmation/confirmation_unsealed.json').exists()
legacy=[]
for p in (OUT/'legacy_b3').glob(task+('_*_index.json' if task=='stability' else '_index.json')):legacy+=json.loads(p.read_text())
if task=='stability':
 coordinates={(r['n'],r['kappa'],r['h']) for r in source}
 source += [r for r in candidate_rows('confirmation') if (r['n'],r['kappa'],r['h']) in coordinates]
 legacy += [r for r in json.loads((OUT/'legacy_b3/confirmation_index.json').read_text()) if (r['n'],r['kappa'],r['h']) in coordinates]
region_index={(x['kappa'],x['h']):x.get('region') for x in PLAN['confirmation']}
for point in source:
 n,k,h=point['n'],point['kappa'],point['h'];region=point.get('region') or region_index.get((k,h)) or ('low_field' if .4-1e-12<=k<=.6+1e-12 and h<=.35+1e-12 else 'other');methods=dict(point['methods']);seed=next(iter(methods.values()))['selected']['seed']
 if task in ['development','validation'] and (OUT/'confirmation/method_frozen.json').exists():
  from annni.stage6_candidates import select
  from annni.stage6_hybrid import components
  frozen=json.loads((OUT/'confirmation/method_frozen.json').read_text());names=components('H6',k,h,frozen['wall_component']);runs=[path for name in names for path in methods[name]['runs']];chosen=select([json.loads((ROOT/path).read_text()) for path in runs]);methods['H6']=dict(selected=chosen,runs=runs)
 old=next((r for r in legacy if r['n']==n and (r['kappa'],r['h'])==(k,h) and (task!='stability' or r['selected']['seed']==seed)),None)
 if old:methods['B3']=dict(selected=old['selected'],runs=old['runs'])
 for method,m in methods.items():
  metric=assess_run(m['selected']);runs=[json.loads((ROOT/r).read_text()) if isinstance(r,str) else r for r in m['runs']];available=any(assess_run(r)['candidate_exists'] for r in runs)
  rows.append(dict(task=task,n=n,kappa=k,h=h,region=region,method=method,seed=seed,candidate_pool_exists=available,search_seconds_standalone=sum(r['seconds'] for r in runs),search_nfev=sum(r['nfev'] for r in runs),search_pool_gradient_evaluations=sum(r.get('pool_gradient_evaluations',0) for r in runs),**{key:value for key,value in metric.items() if key not in ['seed','reference_results','candidates','observables','ed_observables']}))
summary=[]
for method in sorted({r['method'] for r in rows}):
 for region in ['all']+sorted({r['region'] for r in rows}):
  selected=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)]
  if not selected:continue
  summary.append(dict(method=method,region=region,runs=len(selected),coordinates=len({(r['n'],r['kappa'],r['h']) for r in selected}),candidate_pool_exists=sum(r['candidate_pool_exists'] for r in selected),observable_pass=sum(r['observable_pass'] for r in selected),state_pass=sum(r['state_pass'] for r in selected),joint_pass=sum(r['joint_pass'] for r in selected),reference_ambiguous=sum(r['reference_numerical_ambiguous'] for r in selected),optimizer_applicable=sum(r['optimization_applicable'] for r in selected),optimizer_success=sum(r['optimizer_success'] is True for r in selected),median_cnots=float(np.median([r['cnots'] for r in selected])),cnot_quartiles=np.quantile([r['cnots'] for r in selected],[0,.25,.5,.75,1]),median_depth=float(np.median([r['depth'] for r in selected])),median_parameters=float(np.median([r['parameter_count'] for r in selected])),median_all_gates=float(np.median([r['gate_count'] for r in selected])),median_fidelity=float(np.median([r['fidelity'] for r in selected])),median_delta_e=float(np.median([r['delta_e'] for r in selected])),worst_delta_e=max(r['delta_e'] for r in selected),search_seconds_standalone=sum(r['search_seconds_standalone'] for r in selected),search_nfev=sum(r['search_nfev'] for r in selected)))
paired=[]
for method in sorted({r['method'] for r in rows}-{'B3'}):
 for region in ['all']+sorted({r['region'] for r in rows}):
  subset=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)];pairs=[]
  for r in subset:
   old=next((x for x in rows if x['method']=='B3' and (x['n'],x['kappa'],x['h'],x['seed'])==(r['n'],r['kappa'],r['h'],r['seed'])),None)
   if old:pairs.append((r,old))
  if pairs:paired.append(dict(method=method,region=region,paired_runs=len(pairs),new_only_pass=sum(a['joint_pass'] and not b['joint_pass'] for a,b in pairs),B3_only_pass=sum(b['joint_pass'] and not a['joint_pass'] for a,b in pairs),both_pass=sum(a['joint_pass'] and b['joint_pass'] for a,b in pairs),neither_pass=sum(not a['joint_pass'] and not b['joint_pass'] for a,b in pairs),median_delta_cnots=float(np.median([a['cnots']-b['cnots'] for a,b in pairs]))))
O=OUT/('confirmation' if task in ['confirmation','stability'] else 'n12_transfer' if task.startswith('n12') else 'failure_mechanisms');dump(O/f'{task}_paired_summary.json',dict(rows=rows,summary=summary,paired=paired,cost_note='Standalone method search sums include shared component computations; actual unique execution cost must be deduplicated by raw archive hash. Seeds are independent repetitions; rows are not independent coordinates. Original state thresholds retained.'))
with (O/f'{task}_all_selected.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(task,[(r['method'],r['joint_pass'],r['runs']) for r in summary if r['region']=='all'])
