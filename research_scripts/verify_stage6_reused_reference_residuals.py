"""Audit the archived historical vector after a new-sector-spectrum cross-check.
The original record's residual was computed before substituting an agreeing old
vector; retain it and explicitly verify the actually archived vector here.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.upgrade_gates import h_action
rows=[]
for p in (OUT/'reference_atlas/cache').glob('*.json'):
 r=json.loads(p.read_text())
 if r.get('disposition')!='historical_ground_state_reused_new_sector_spectrum':continue
 a=np.load(ROOT/r['archive']);s=a['state'];res=float(np.linalg.norm(h_action(s,r['n'],r['kappa'],r['h'])-r['energy']*s));gap=r['sector_gap'];ambiguous=bool(gap<=100*max(res,1e-14))
 rows.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],recorded_new_sector_vector_residual=r['residual'],actual_archived_historical_vector_residual=res,actual_residual_gap_ratio=res/gap,actual_reference_numerical_ambiguous=ambiguous,original_reference_numerical_ambiguous=r['reference_numerical_ambiguous'],archive=r['archive'],sha256=r['sha256']))
changed=[r for r in rows if r['actual_reference_numerical_ambiguous']!=r['original_reference_numerical_ambiguous']]
result=dict(timestamp=datetime.now(timezone.utc).isoformat(),rows=rows,archived_reused_states=len(rows),maximum_actual_residual=max(r['actual_archived_historical_vector_residual'] for r in rows),maximum_actual_residual_gap_ratio=max(r['actual_residual_gap_ratio'] for r in rows),changed_numerical_ambiguity=changed,scope='Derived explicit residual of the archived reused state. Original record residual is from the preceding independently solved sector vector. Both preserved; no state or reference threshold changed.')
dump(OUT/'verification/reference_reuse_residual_audit.json',result);print({k:v for k,v in result.items() if k not in ['rows','scope']});assert not changed
