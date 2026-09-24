"""Coordinate-level coverage; never count 32 repeats as 32 physical slices."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=OUT/'end_to_end/boundary_comparison.json';rows=json.loads(p.read_text());groups={}
protocol=json.loads((OUT/'end_to_end/boundary_matching_protocol.json').read_text())
requested=protocol['all_requested_kappa']
reference_by_k={r['kappa']:r['reference_resolvable'] for r in rows if r['estimator']=='pure_circuit'}
for r in rows:groups.setdefault((r['method'],r['p'],r['estimator'],r['budget']),[]).append(r)
result=[]
for key,group in groups.items():
 byk={}
 for r in group:byk.setdefault(r['kappa'],[]).append(r)
 slices=[]
 for k in sorted(requested):
  rr=byk.get(k,[])
  if not rr:
   slices.append(dict(kappa=k,reference_resolvable=reference_by_k[k],measurement_repeats=0,estimate_fraction=0.,match_fraction=0.,conditional_mean_matched_error=None,worst_matched_error=None,worst_all_primary_error=None,status_counts={'not_executed_complete_window':1},matched_interval_widths=[]))
   continue
  reference=rr[0]['reference_resolvable'];assert all(r['reference_resolvable']==reference for r in rr)
  errs=[abs(r['position_error']) for r in rr if r.get('matched')];allerrs=[abs(r['position_error']) for r in rr if r.get('position_error') is not None and reference]
  slices.append(dict(kappa=k,reference_resolvable=reference,measurement_repeats=len(rr) if key[-1] is not None else 0,estimate_fraction=sum(reference and r['algorithm_estimatable'] for r in rr)/len(rr),match_fraction=sum(r['matched'] for r in rr)/len(rr),conditional_mean_matched_error=float(np.mean(errs)) if errs else None,worst_matched_error=max(errs) if errs else None,worst_all_primary_error=max(allerrs) if allerrs else None,status_counts=dict(collections.Counter(r['status'] for r in rr)),matched_interval_widths=[r.get('interval_width') for r in rr if r.get('matched')]))
 refs=[s for s in slices if s['reference_resolvable']]
 result.append(dict(method=key[0],p=key[1],estimator=key[2],budget=key[3],requested_physical_slices=len(slices),reference_resolvable_physical_slices=len(refs),reference_fraction=len(refs)/len(slices),mean_estimate_fraction_given_reference=float(np.mean([s['estimate_fraction'] for s in refs])) if refs else None,mean_match_fraction_given_reference=float(np.mean([s['match_fraction'] for s in refs])) if refs else None,total_measurement_window_repeats=sum(s['measurement_repeats'] for s in slices),slices=slices))
dest=OUT/'end_to_end/boundary_coordinate_coverage.json'
if dest.exists() and not (OUT/'end_to_end/boundary_coordinate_coverage_v1.json').exists():
 old=json.loads(dest.read_text())
 if 'version' not in old:dump(OUT/'end_to_end/boundary_coordinate_coverage_v1.json',old)
dump(dest,dict(version=2,source=str(p.relative_to(ROOT)),sha256=sha(p),rows=result,note='Six requested physical kappa slices; only three have the prescribed complete noisy windows. Missing windows stay in every budget-specific denominator. Each measured slice has32 separate full-window experiments. Matched-only errors are explicitly conditional; all primary errors and failures are retained. RN feature positions, not thermodynamic phase boundaries.',correction='v1 grouped finite-shot rows before adding missing windows, incorrectly reporting3 requested slices for finite-shot groups. v2 explicitly enumerates all6 predeclared slices at every budget; original v1 retained. No peak, detector, matching rule or raw result changed.'))
print(len(result),'coordinate-level boundary summaries')
