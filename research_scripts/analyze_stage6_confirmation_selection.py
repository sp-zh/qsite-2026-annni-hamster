"""Post-unseal diagnosis only; does not change the selected circuits."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_rows
from annni.stage6_assess import assess_run
assert (OUT/'confirmation/confirmation_unsealed.json').exists()
summary=json.loads((OUT/'confirmation/confirmation_paired_summary.json').read_text())['rows']
selected={(r['kappa'],r['h']):r for r in summary if r['method']=='H6' and r['candidate_pool_exists'] and not r['joint_pass']}
out=[]
for point in candidate_rows('confirmation'):
 coordinate=(point['kappa'],point['h'])
 if coordinate not in selected:continue
 row=selected[coordinate];qualified=[];all_references=[]
 for path in point['methods']['H6']['runs']:
  raw=json.loads((ROOT/path).read_text());assessment=assess_run(raw)
  all_references.append(dict(source=path,basis=raw['basis'],reference=raw['ref'],selected_energy=raw['selected']['energy'],selected_cnots=raw['selected']['cnots'],joint_pass=assessment['joint_pass']))
  for c in assessment['candidates']:
   if c['joint_pass']:qualified.append(dict(source=path,basis=raw['basis'],reference=raw['ref'],**c))
 assert qualified
 best=min(qualified,key=lambda x:x['energy']);minimum=min(x['selected_energy'] for x in all_references)
 out.append(dict(kappa=coordinate[0],h=coordinate[1],deployed=row,qualified_checkpoints=qualified,reference_outputs=all_references,best_qualified_energy=best['energy'],qualified_energy_minus_deployed_per_site=(best['energy']-row['energy'])/row['n'],deployed_energy_minus_pool_minimum_per_site=(row['energy']-minimum)/row['n'],diagnosis='A qualified saved checkpoint exists, but the frozen energy/resource rule selects a different literal state. Inspect energy differences and translation expectation: F~1/2 with P~1,T~0 and accurate translation-averaged observables is consistent with choosing one near-degenerate translation branch, not loss of normalization. No alternate state is deployed here.'))
dump(OUT/'confirmation/selection_failure_diagnosis.json',dict(rows=out,coordinates=len(out),scope='Post-unseal descriptive evidence. ED-qualified alternatives are oracle diagnostic upper bounds, not a new selector or confirmation retuning. Historical thresholds are unchanged.'))
print('Diagnosed qualified-but-unselected coordinates',len(out))
