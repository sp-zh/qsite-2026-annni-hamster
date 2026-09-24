"""Counterparts of actual B4 structure AND compilation-direction switches."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
noise=json.loads((OUT/'map/noise_index.json').read_text());assert len(noise)==420
lookup={(round(r['kappa'],6),round(r['h'],6)):r for r in noise};rows=[]
for interval in json.loads((OUT/'branches/index.json').read_text()):
 k=interval['kappa'];left=lookup[round(k,6),round(interval['left_h'],6)];right=lookup[round(k,6),round(interval['right_h'],6)];ra=left['B4_selection']['reverse'];rb=right['B4_selection']['reverse'];out=dict(kappa=k,left_h=interval['left_h'],right_h=interval['right_h'],reverse_left=ra,reverse_right=rb,direction_switch=ra!=rb,structure_switch=interval['actual_structure_switch'],actual_switch_pair_checked=True,opposite_direction_checked=False,endpoints=[],scope='Actual selected B4 identities transported to common coordinates by fixed-structure energy refits; not pre-existing scan chains')
 for end in interval['endpoints']:
  a=json.loads((ROOT/Path(end['a_state_archive']).with_suffix('.json')).read_text());b=json.loads((ROOT/Path(end['b_state_archive']).with_suffix('.json')).read_text());entries=[]
  for p in [0,.01,.05]:
   na=noise_record(a,p,reverse=ra);nb=noise_record(b,p,reverse=rb);oa=np.load(ROOT/na['archive']);ob=np.load(ROOT/nb['archive']);dv=vector(dict(correlations=oa['correlations'],structure_factor=oa['structure_factor'],mx=float(oa['mx'])))-vector(dict(correlations=ob['correlations'],structure_factor=ob['structure_factor'],mx=float(ob['mx'])))
   entries.append(dict(p=p,difference=dv.tolist(),sensitive=bool(max(abs(dv))>.02),a_archive=na['archive'],a_sha256=na['sha256'],b_archive=nb['archive'],b_sha256=nb['sha256']))
  out['endpoints'].append(dict(h=end['h'],a_state_archive=end['a_state_archive'],b_state_archive=end['b_state_archive'],a_params_sha=end['a_params_sha'],b_params_sha=end['b_params_sha'],both_prep_pass=end['both_prep_pass'],comparisons=entries))
 rows.append(out)
 if len(rows)%5==0:dump(OUT/'branches/b4_index.json',rows);print(len(rows),flush=True)
dump(OUT/'branches/b4_index.json',rows)
