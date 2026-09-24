"""Expanded failure attribution with retained warm, random, oracle and growth evidence."""
import sys,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'failure_mechanisms';optional=lambda name:json.loads((O/name).read_text()) if (O/name).exists() else []
fixed=optional('fixed_energy_restarts_index.json');warm=optional('energy_continuation_index.json');oracle=optional('oracle_expressivity_index.json');growth=optional('growth_audit.json');rows=[]
for task in ['development','validation','confirmation']:
 folder=O if task!='confirmation' else OUT/'confirmation';p=folder/f'{task}_paired_summary.json'
 if not p.exists():continue
 selected=json.loads(p.read_text())['rows']
 for r in selected:
  k,h,m=r['kappa'],r['h'],r['method'];rr=[x for x in fixed if (x['kappa'],x['h'],x['method'])==(k,h,m)] if task=='development' else [];ww=[x for x in warm if (x['kappa'],x['h'],x['method'])==(k,h,m)] if task=='development' else [];oo=[x for x in oracle if (x['kappa'],x['h'],x['method'])==(k,h,m)] if task=='development' else [];gg=[x for x in growth if (x['kappa'],x['h'],x['method'])==(k,h,m)] if task=='development' else []
  any_growth=any(x['all_saved_candidate_joint_pass_count'] for x in gg);pool=r['candidate_pool_exists'];tags=[]
  if r['reference_numerical_ambiguous']:tags.append('reference_numerical_ambiguous')
  if not r['joint_pass'] and pool:tags.append('qualified_checkpoint_candidate_found_but_not_selected')
  if not r['joint_pass'] and not pool and any_growth:tags.append('qualified_saved_growth_or_probe_not_in_selected_checkpoint_pool')
  if not r['joint_pass'] and any(x['joint_pass'] for x in rr):tags.append('same_structure_independent_energy_restart_effective')
  if not r['joint_pass'] and any(x['joint_pass'] for x in ww):tags.append('same_structure_warm_energy_continuation_effective')
  if not r['joint_pass'] and any(x['joint_pass'] for x in oo) and not any(x['joint_pass'] for x in rr+ww):tags.append('fixed_structure_oracle_reachable_energy_optimization_limited')
  if not r['joint_pass'] and oo and not any(x['joint_pass'] for x in oo):tags.append('bounded_oracle_failed_not_mathematical_inexpressivity')
  if not r['joint_pass'] and r['source_stop'] in ['cnot_budget','parameter_cap','parameter_cap160','budget','parameter_budget']:tags.append('recorded_resource_cap_reached')
  if not tags:tags=['selected_pass' if r['joint_pass'] else 'still_uncertain']
  rows.append(dict(task=task,n=r['n'],kappa=k,h=h,method=m,region=r['region'],joint_pass=r['joint_pass'],observable_pass=r['observable_pass'],state_pass=r['state_pass'],candidate_checkpoint_exists=pool,all_saved_growth_or_probe_exists=any_growth if gg else None,random_restart_runs=len(rr),random_restart_pass=sum(x['joint_pass'] for x in rr),warm_continuations=len(ww),warm_pass=sum(x['joint_pass'] for x in ww),oracle_runs=len(oo),oracle_pass=sum(x['joint_pass'] for x in oo),actual_stop=r['source_stop'],cnots=r['cnots'],delta_e=r['delta_e'],fidelity=r['fidelity'],tags=tags,source=r['source']))
dump(O/'attribution_v2.json',dict(rows=rows,tag_counts=dict(collections.Counter(t for r in rows for t in r['tags'])),scope='Overlapping mechanism evidence, not mutually exclusive causes. Oracle only12 development coordinates, never confirmation generation. Failed bounded fitting does not establish inexpressivity. Warm continuation is not an independent seed. All-growth audit is post-hoc and never selects deployed circuits.'))
with (O/'attribution_v2.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows([{**r,'tags':';'.join(r['tags'])} for r in rows])
print('attribution v2 selected rows',len(rows))
