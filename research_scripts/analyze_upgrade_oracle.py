"""Explicit post-hoc ED oracle upper bound; never used by the deployed selector."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
rows=[]
for task in ['development','heldout','map','n12']:
 index=json.loads((OUT/task/'index.json').read_text())
 for point in index:
  candidates=[r for r in point['candidates'] if r['method']=='cost'];checks=[]
  for r in candidates:
   raw=json.loads((ROOT/Path(r['archive']).with_suffix('.json')).read_text())
   checks += [dict(ref=r['ref'],source=r['archive'],**c) for c in raw['checkpoints'] if c['joint_pass']]
  oracle=min(checks,key=lambda c:(c['cnots'],c['energy'])) if checks else None;winner=point['methods']['B3']
  rows.append(dict(task=task,n=point['n'],kappa=point['kappa'],h=point['h'],deployable_cnots=winner['selected']['cnots'],deployable_pass=winner['joint_pass'],oracle_any_pass=oracle is not None,oracle_min_cnots=None if oracle is None else oracle['cnots'],oracle_ref=None if oracle is None else oracle['ref'],oracle_source=None if oracle is None else oracle['source'],oracle_uses_ED=True,not_a_validated_selector=True))
dump(OUT/'oracle_upper_bound.json',rows)
with open(OUT/'oracle_upper_bound.csv','w') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print('Post-hoc oracle bounds written separately')
