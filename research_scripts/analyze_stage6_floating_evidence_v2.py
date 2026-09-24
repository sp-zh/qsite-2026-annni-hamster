"""Stricter scientific interpretation; retain v1 and every conflicting size."""
import sys,copy,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';original=json.loads((O/'evidence_map.json').read_text());rows=[]
for source in original:
 r=copy.deepcopy(source);r['v1_status']=source['status']
 conflicts=[]
 for m in r['metrics']:
  if m['n']>=96 and m['solver_stopping_pass'] and m['K_fit_valid'] and m['K_window_stable'] and not all(.25<k<.5 for k in m['K_values']):
   conflicts.append(dict(n=m['n'],chi=m['chi'],initial=m['initial'],K_values=m['K_values'],source=m['source']))
 r['cross_size_K_conflicts']=conflicts
 if r['status']=='supported_floating_sample' and conflicts:r['status']='finite_size_crossover_unresolved'
 r['v2_scope']='All converged N>=96 with valid, window-stable Friedel fits can block floating support if K lies outside the stated convention. A conflict is evidence of unresolved size dependence, not proof of a different thermodynamic phase. Original v1 status is retained.'
 rows.append(r)
dump(O/'evidence_map_v2.json',rows)
supported={name:[r['h'] for r in rows if r['status']==name] for name in ['supported_antiphase_sample','supported_floating_sample','supported_paramagnetic_side_sample']}
a=supported['supported_antiphase_sample'];f=supported['supported_floating_sample'];p=supported['supported_paramagnetic_side_sample']
summary=dict(version=2,timestamp=datetime.now(timezone.utc).isoformat(),source_sha=sha(O/'evidence_map.json'),code_sha=sha(__file__),supported_samples=supported,lower_transition_bracket=[max(x for x in a if x<min(f)),min(f)] if f and any(x<min(f) for x in a) else None,upper_transition_bracket=[max(f),min(x for x in p if x>max(f))] if f and any(x>max(f) for x in p) else None,candidate_floating_samples=[r['h'] for r in rows if r['status'].startswith('candidate_floating')],unresolved_samples=[r['h'] for r in rows if r['status']=='finite_size_crossover_unresolved'],downgraded_samples=[dict(h=r['h'],old=r['v1_status'],new=r['status'],conflicts=r['cross_size_K_conflicts']) for r in rows if r['status']!=r['v1_status']],scope='Discrete controlled OBC samples. Brackets span supported sides and unresolved points; no continuous floating interval or rigorous thermodynamic exclusion is inferred. No circuit/detector retraining, mask or selection change follows this scientific evidence revision.')
dump(O/'interval_evidence_v2.json',summary)
flat=[dict(kappa=.8,h=r['h'],v1_status=r['v1_status'],status=r['status'],K_conflict_sizes=';'.join(map(str,sorted({m['n'] for m in r['cross_size_K_conflicts']}))),solver_stops=r['all_required_solver_stops'],strict_bond_initial=r['strict_bond_and_initial_agreement']) for r in rows]
with (O/'evidence_map_v2.csv').open('w') as file:
 writer=csv.DictWriter(file,fieldnames=flat[0]);writer.writeheader();writer.writerows(flat)
print(summary)
