"""Pairwise attribution; successful oracle fits are not deployed VQE results."""
import sys,collections,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_assess import assess_run
new=json.loads((OUT/'failure_mechanisms/development_assessment.json').read_text());legacy=json.loads((OUT/'legacy_b3/development_index.json').read_text());fixed=json.loads((OUT/'failure_mechanisms/fixed_energy_restarts_index.json').read_text());oracle=json.loads((OUT/'failure_mechanisms/oracle_expressivity_index.json').read_text());rows=[]
for r in new:
 k,h=r['kappa'],r['h'];old=next(a for a in legacy if a['kappa']==k and a['h']==h);base=assess_run(old['selected']);pool=[assess_run(a) for a in old['runs']];methods=dict(r['methods'],B3=dict(base,candidate_pool_exists=any(x['candidate_exists'] for x in pool)));attributions=[]
 for m in ['B3','C3']:
  v=methods[m];restarts=[x for x in fixed if x['kappa']==k and x['h']==h and x['method']==m];fits=[x for x in oracle if x['kappa']==k and x['h']==h and x['method']==m];tags=[]
  if v.get('candidate_pool_exists') and not v['joint_pass']:tags.append('qualified_candidate_found_but_not_selected')
  if not v['joint_pass'] and any(x['joint_pass'] for x in restarts):tags.append('fixed_structure_energy_restart_repairs_failure')
  if not any(x['joint_pass'] for x in restarts) and any(x['joint_pass'] for x in fits):tags.append('fixed_structure_oracle_reachable_energy_optimization_limited' if not v['joint_pass'] else 'original_pass_but_independent_random_restarts_unstable')
  if fits and not any(x['joint_pass'] for x in fits):tags.append('bounded_oracle_fit_failed_not_impossibility_proof' if not v['joint_pass'] else 'oracle_fit_failed_despite_known_qualified_prepared_state')
  if not tags:tags.append('passed' if v['joint_pass'] else 'still_uncertain_or_budget_limited')
  attributions.append(dict(method=m,tags=tags,new_restart_pass_count=sum(x['joint_pass'] for x in restarts),restart_count=len(restarts),oracle_joint_pass=any(x['joint_pass'] for x in fits) if fits else None,oracle_tested=bool(fits)))
 if not methods['C0']['joint_pass'] and methods['C1']['joint_pass']:attributions.append(dict(method='C1',tags=['same_physical_references_pool_improved_search_effective']))
 if not methods['C0']['joint_pass'] and methods['C2']['joint_pass']:attributions.append(dict(method='C2',tags=['wall_basis_reference_pool_changes_effective_jointly_not_separately_identified']))
 if not methods['C2']['joint_pass'] and methods['C3']['joint_pass']:attributions.append(dict(method='C3',tags=['wall_same_references_pool_improved_search_effective']))
 rows.append(dict(n=8,kappa=k,h=h,region=r['region'],methods=methods,attributions=attributions));dump(OUT/'failure_mechanisms/attribution.json',rows)
flat=[dict(kappa=r['kappa'],h=r['h'],method=a['method'],attribution=';'.join(a['tags'])) for r in rows for a in r['attributions']]
with (OUT/'failure_mechanisms/attribution.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=flat[0]);w.writeheader();w.writerows(flat)
print('Attribution coordinates',len(rows));print(collections.Counter(t for r in rows for a in r['attributions'] for t in a['tags']))
