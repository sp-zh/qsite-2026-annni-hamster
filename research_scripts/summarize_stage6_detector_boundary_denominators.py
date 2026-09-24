"""All requested slices at every detector/estimator/budget; repeats are not slices."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
source=OUT/'end_to_end/detector_boundary_comparison.json';rows=json.loads(source.read_text())
protocol=json.loads((OUT/'end_to_end/boundary_matching_protocol.json').read_text())
requested=protocol['all_requested_kappa'];reference={r['kappa']:r['reference_resolvable'] for r in rows}
keys=sorted({(r['method'],r['p'],r['estimator'],r['detector']) for r in rows});result=[]
for key in keys:
    for budget in [None,100000]:
        slices=[]
        for k in requested:
            rr=[r for r in rows if (r['method'],r['p'],r['estimator'],r['detector'])==key and r['budget']==budget and r['kappa']==k]
            executed=[r for r in rr if r.get('result') is not None]
            assert len(executed) in ([0,1] if budget is None else [0,32])
            count=len(executed);errors=[abs(r['position_error']) for r in executed if r['matched']]
            all_errors=[abs(r['position_error']) for r in executed if r['position_error'] is not None and reference[k]]
            status=dict(collections.Counter(r['status'] for r in rr)) if rr else {'D5_high_order_wall_histogram_not_measured_in_SV' if key[-1]=='D5' and key[-2]=='sv' else 'complete_window_not_executed':1}
            slices.append(dict(kappa=k,reference_resolvable=reference[k],exact_curve_executed=bool(count) if budget is None else None,
                measurement_repeats=count if budget is not None else 0,
                estimate_fraction=sum(r['algorithm_estimatable'] for r in executed)/count if count and reference[k] else 0.,
                match_fraction=sum(r['matched'] for r in executed)/count if count else 0.,
                conditional_mean_matched_error=float(np.mean(errors)) if errors else None,
                worst_matched_error=max(errors) if errors else None,worst_all_primary_error=max(all_errors) if all_errors else None,
                status_counts=status,matched_interval_widths=[r['result']['primary']['interval_high']-r['result']['primary']['interval_low'] for r in executed if r['matched']]))
        resolvable=[r for r in slices if r['reference_resolvable']]
        result.append(dict(method=key[0],p=key[1],estimator=key[2],detector=key[3],budget=budget,
            requested_physical_slices=len(slices),reference_resolvable_physical_slices=len(resolvable),reference_fraction=len(resolvable)/len(slices),
            mean_estimate_fraction_given_reference=float(np.mean([r['estimate_fraction'] for r in resolvable])),
            mean_match_fraction_given_reference=float(np.mean([r['match_fraction'] for r in resolvable])),
            total_measurement_window_repeats=sum(r['measurement_repeats'] for r in slices),slices=slices))
dump(OUT/'end_to_end/detector_boundary_coverage.json',dict(version=2,source=str(source.relative_to(ROOT)),sha256=sha(source),rows=result,
    scope='All six requested physical kappa slices and five resolvable same-size named RN references retained in every budget group. Only three noisy windows executed. Each measured window has32repetitions; an unmeasured window has zero, not one fictitious measurement. D5/SV wall features were not measured. Matching thresholds and raw detector curves unchanged.'))
print('Detector boundary physical-slice groups',len(result))
