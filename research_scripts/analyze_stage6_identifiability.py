"""Interpret binary distinguishability separately from physical phase classification."""
import sys,collections,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
path=OUT/'noise_diagnosability/identifiability.json';data=json.loads(path.read_text());rows=[]
for r in data:
 oracle={x['shots_per_query']:x for x in r['oracle_measurement']};pred=r['predictions'];same={d:pred[0][d]['label']==pred[1][d]['label'] for d in ['D4','D5']};uncertain={d:any(x[d]['label'] in ['uncertain','degraded'] for x in pred) for d in ['D4','D5']}
 if oracle[1000000]['error_rate']>=.25:scope='Current_XZ_measurement_binary_query_unresolved_at_1M_in_32_repetitions'
 elif oracle[100000]['error_rate']==0 and any(same[d] or uncertain[d] for d in same):scope='Known_binary_measurement_templates_distinguish_while_some_frozen_outputs_do_not'
 else:scope='Binary_differences_measurable_no_global_phase_accuracy_inference'
 rows.append(dict(pair_index=r['pair_index'],pair_type=r['pair'].get('kind',r['pair'].get('type','unspecified')),method=r['method'],p=r['p'],trace_distance=r['trace_distance'],XZ_total_variation=r['xz_joint_total_variation'],classical_minus_quantum=r['xz_joint_total_variation']-r['trace_distance'],known_binary_single_copy_optimal_error=r['optimal_known_binary_single_copy_error'],oracle_error_10k=oracle[10000]['error_rate'],oracle_error_100k=oracle[100000]['error_rate'],oracle_error_1M=oracle[1000000]['error_rate'],D4_same_output=same['D4'],D5_same_output=same['D5'],D4_any_reject=uncertain['D4'],D5_any_reject=uncertain['D5'],interpretation=scope,counts=r['counts_archive']))
summary=[]
for row,source in zip(rows,data):row['independent_opposite_phase_labels']=bool(source['pair'].get('independent_opposite_phase_labels',False))
for method,p in sorted({(r['method'],r['p']) for r in rows}):
 subset=[r for r in rows if (r['method'],r['p'])==(method,p)];summary.append(dict(method=method,p=p,pairs=len(subset),median_DQ=float(np.median([r['trace_distance'] for r in subset])),median_TV=float(np.median([r['XZ_total_variation'] for r in subset])),min_TV=min(r['XZ_total_variation'] for r in subset),oracle_mean_error_100k=float(np.mean([r['oracle_error_100k'] for r in subset])),oracle_mean_error_1M=float(np.mean([r['oracle_error_1M'] for r in subset])),interpretation_counts=dict(collections.Counter(r['interpretation'] for r in subset))))
by_scope=[]
for method,p,supported in sorted({(r['method'],r['p'],r['independent_opposite_phase_labels']) for r in rows}):
 subset=[r for r in rows if (r['method'],r['p'],r['independent_opposite_phase_labels'])==(method,p,supported)]
 by_scope.append(dict(method=method,p=p,independent_opposite_phase_labels=supported,pairs=len(subset),median_DQ=float(np.median([r['trace_distance'] for r in subset])),median_TV=float(np.median([r['XZ_total_variation'] for r in subset])),oracle_mean_error_100k=float(np.mean([r['oracle_error_100k'] for r in subset])),scope='Far interior controls; do not extrapolate to nearby transition pairs' if supported else 'RN feature-side pairs; equal class labels are not automatically classification errors'))
dump(OUT/'noise_diagnosability/interpretation.json',dict(rows=rows,summary=summary,summary_by_pair_scope=by_scope,scope='Known two-state template discrimination. RN-feature pairs are not automatically opposite physical phases: equal detector labels can be appropriate within one physical phase. Zero errors among64 binary queries is not a zero-risk guarantee. Nonidentical circuits do not define one common channel, so contraction is not assumed. Full-state DQ has separate resource category. No unconditional strong-noise information-loss claim follows from a classifier rejection. Retained binary differences can partly reflect preparation-specific noise fingerprints; same-coordinate cross-structure controls are saved separately.',criteria='Before pair execution: oracle1M error>=.25 is unresolved for this measured binary protocol; zero observed100k errors plus equal/rejected detector outputs demonstrates retained template information, not a trained universal phase classifier.'))
with (OUT/'noise_diagnosability/interpretation.csv').open('w') as f:writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
print(summary)
