"""Scientific status from actual evidence; execution completeness is separate."""
import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_rows,measurement_rows
def read(path,default=None):
    p=OUT/path
    return json.loads(p.read_text()) if p.exists() else default
counts={}
for task,expected in [('confirmation',96),('low_map',108),('map',420),('n12',36),('n12_window',16),('n12_192',12)]:
    counts['candidate_'+task]=dict(actual=len(candidate_rows(task)),requested=expected)
for task,expected in [('confirmation',96),('core',48),('windows',51),('low_map',108),('map',420),('n12',12)]:
    counts['noise_'+task]=dict(actual=len(measurement_rows((OUT/'end_to_end').glob(task+'_*_index.json'))),requested=expected)
missing={k:v for k,v in counts.items() if v['actual']!=v['requested']}
mps_version=next(v for v in [4,3,2] if (OUT/f'floating_boundary_scan/interval_evidence_v{v}.json').exists())
floating=read(f'floating_boundary_scan/interval_evidence_v{mps_version}.json',{})
boundary=read('end_to_end/boundary_coordinate_coverage.json',{}).get('rows',[])
n12=read('n12_transfer/n12_paired_summary.json',{}).get('summary',[])
atlas_rows=list(csv.DictReader((OUT/'reference_atlas/boundary_reference.csv').open()))
atlas_coverage=[]
for n in [8,12,16]:
    rr=[r for r in atlas_rows if int(r['n'])==n and r['feature']==('minus_dm0_dh' if float(r['kappa'])<.5 else 'minus_dmap_dh')]
    atlas_coverage.append(dict(n=n,requested_kappa_slices=len(rr),resolvable_named_order_features=sum(r['resolvable']=='True' for r in rr),unresolved_kappa=[float(r['kappa']) for r in rr if r['resolvable']!='True']))
decision=dict(run_id=PLAN['run_id'],generated_utc=datetime.now(timezone.utc).isoformat(),original_deadline=PLAN['deadline'],
    reference_atlas_status=dict(status='executed_layered_reference_with_unresolved_regions',physical_confirmation_labels='24/96; low-field4/48',RN_pattern_proxy_confirmation_labels='64/96',basis='R0/interior extensions, same-size PBC ED observables/responses, separately reported OBC evidence',scope='Not an independently established four-phase truth map.'),
    low_field_candidate_generation_status=dict(status='N8_improvement_with_high_cost_not_universal_replacement',confirmation_low_field=dict(coordinates=48,B3_candidate_exists=27,H6_candidate_exists=45,B3_joint_pass=27,H6_joint_pass=37,B3_observable_pass=28,H6_observable_pass=45,B3_median_CNOT=32,H6_median_CNOT=127),limitations=['Validation joint20/24 H6 versus22/24 B3','No demonstrated independent-seed stability improvement','Low-field objective calls increase by about7.45x','Eight qualified N8 candidates not selected; historical state failures retained']),
    boundary_reference_coverage=dict(reference_atlas=atlas_coverage,circuit_windows=dict(requested_kappa=[0,.3,.45,.5,.55,.8],resolvable=5,requested=6,unresolved=[.5]),scope='Same-size named RN features, not precise thermodynamic boundaries; additional Mx/fidelity/spectral diagnostics retain separate peaks.'),
    circuit_boundary_reconstruction_status=dict(status='p0_local_RN_progress_strong_noise_curve_failures',pure=dict(B3_matched=4,H6_matched=5,reference_resolvable=5,worst_matched_displacement=.0125),noisy_windows_executed=[.45,.55,.8],coverage_rows=boundary,limitations=['Missing three noisy windows remain in every budget denominator','Matched interior peak may coexist with stronger endpoint response','Strong-noise H6 low-field feature mismatch persists after ZNE','Full response distortion is reported separately from peak-position agreement']),
    new_confirmation_status=dict(status='new_coordinate_generation_and_evaluation_executed',coordinates=96,main_joint=dict(B3=66,C1=70,H6=77),noise=counts['noise_confirmation'],isolation='Candidate/detector freeze precedes confirmation generation/unseal; mitigation frozen separately using validation noise before noisy confirmation; no claims of unseen-phase extrapolation'),
    noise_failure_localization_status=dict(status='executed_bias_measurement_detector_and_cross_structure_controls',pairs=14,pair_method_p_records=84,same_coordinate_controls=26,exploratory_same_coordinate_growth_controls=4,findings=['Core exact bias MSE dominates finite-shot MSE','Known X/Z binary templates retain distinguishability at tested budgets','Same-coordinate different-circuit noise fingerprints confound phase interpretation','Actual saved growth checkpoints at identical Hamiltonian coordinates show large noise-induced order changes despite small p0 changes; gate/parameter jumps contribute to spurious response peaks','Some reference regions remain unlabelled; no detector is scored against invented truth']),
    strong_noise_identification_status=dict(status='partial_labelled_interior_mitigation_no_full_restoration',core=dict(coordinates=48,physical_labelled=13,D3_B3_raw_correct=10,D3_B3_quadratic_ZNE_correct_repeat_normalized=11.0625,D4_B3_raw_correct=2,D4_B3_quadratic_ZNE_correct=11,D4_H6_raw_correct=0,D4_H6_quadratic_ZNE_correct=0,p=.05,shots_per_repeat=100000,repeats=32),scope='No information-theoretic impossibility claim from rejection; no claim of whole-phase accuracy from binary oracle discrimination.'),
    floating_interval_evidence_status=dict(status='no_controlled_continuous_interval' if not floating.get('supported_samples',{}).get('supported_floating_sample') else 'discrete_supported_samples_not_continuous_band',evidence=floating,limitations=['OBC and PBC interpretations remain separate','N/chi/initial-state and stopping tests are distinct','Valid size conflicts retained, not fitted toward a theoretical line','chi512 timeout is not a physical exclusion result']),
    n12_transfer_status=dict(status='initial128CNOT_transfer_does_not_establish_advantage',main_summary=n12,window_summary=read('n12_transfer/n12_window_paired_summary.json',{}).get('summary',[]),window_response_scope='At kappa=.55, selected joint passes H6=0/16 versus B3=7/16; both have7observable passes. All p0 methods shift the principal response by+.0125 relative to identical-window ED. This does not establish a thermodynamic boundary.',extension=counts['candidate_n12_192'],noise=counts['noise_n12'],window=counts['candidate_n12_window'],scope='Frozen N8 rule; same-N ED, full16-point pure window versus6-point noisy window;192CNOT extension separately reported.'),
    scientific_limitations=['Independent physical labels do not cover the competition region','N8 low-field gains require substantially more executed gates and classical search','Noise resilience and state fidelity give different method rankings','New D4/D5 do not establish general strong-noise superiority to the simpler frozen D3 baseline','Frozen detector training partly uses finite-size pattern proxies','Peak-coordinate agreement can hide distorted or endpoint-dominated curves','Current OBC data do not establish a continuous floating interval or two tight transition brackets','No universal N12 difficult-region improvement established at128CNOT','Full simulator-state access and ideal ED measurement references are not free hardware resources'],
    submission_readiness=dict(status='reviewable_research_evidence_not_complete_four_phase_or_strong_noise_solution',package_verification='See external deliverables/STAGE6_CLEAN_EXTRACTION_CHECK.json; no claim from script existence alone',unexecuted_requested_counts=missing),
    execution_counts=counts,next_scientific_decision='Retain B3 and H6 as resource/accuracy tradeoffs. Do not replace B3 universally or infer thermodynamic phase boundaries from masked state passes. Address measured curve/circuit-noise failures and unresolved large-size evidence before stronger claims.')
decision['n12_transfer_status']['noise_subset_interpretation']=read('n12_transfer/noise_scope_interpretation.json')
decision['n12_transfer_status']['extension_summary']=read('n12_transfer/n12_192_paired_summary.json',{}).get('summary',[])
decision['n12_transfer_status']['same_coordinate_budget_comparison']=read('n12_transfer/paired_budget_128_192.json',{}).get('summary',[])
decision['descriptive_map_preparation']={task:read(f'n8_maps/{task}_selected_preparation_summary.json',{}).get('summary',[]) for task in ['map','low_map']}
decision['descriptive_map_area_metrics']={task:read(f'n8_maps/{task}_area_summary.json') for task in ['map','low_map']}
decision['strong_noise_identification_status']['confirmation_summary']=read('end_to_end/confirmation_summary.json')
decision['floating_interval_evidence_status']['criterion_bottlenecks']=read(f'floating_boundary_scan/evidence_bottlenecks_v{mps_version}.json')
side_samples=floating.get('supported_samples',{});anti=side_samples.get('supported_antiphase_sample',[]);para=side_samples.get('supported_paramagnetic_side_sample',[])
if anti and para and not side_samples.get('supported_floating_sample'):
 lower=max(anti);higher=[h for h in para if h>lower]
 if higher:decision['floating_interval_evidence_status']['unresolved_between_supported_side_samples']=dict(interval=[lower,min(higher)],scope='Window between controlled OBC side samples, not an identified continuous floating band or two separate transition brackets.')
decision['noise_failure_localization_status']['ideal_ED_detector_boundary_control']=read('end_to_end/ideal_ED_detector_boundaries.json',{}).get('summary',[])
decision['circuit_boundary_reconstruction_status']['detector_contrast_coverage']=read('end_to_end/detector_boundary_coverage.json')
dump(OUT/'decision.json',decision)
bonus=['# Stage 6 bonus and scope status','',f'Generated {decision["generated_utc"]}. Bonus evidence supports the core phase task; it is not a substitute for it.','',
'| Item | Actual evidence | Limitation |','|---|---|---|',
f'| N>=12 | {counts["candidate_n12"]["actual"]}/36 difficult+control coordinates; {counts["candidate_n12_192"]["actual"]}/12 resource-extension coordinates; {counts["noise_n12"]["actual"]}/12 noisy coordinates | No established128-CNOT difficult-region advantage; report192 separately |',
'| Multiple diagnostics | D1/D3 frozen baselines, D4 covariance/unique-SF, D5 wall histogram; D2 full-state windows where executed | D2 is not a local-shot estimator; reference coverage remains limited |',
'| Error mitigation | Common48-coordinate raw/linear ZNE/quadratic ZNE/signed SV, shared10k/100k total budgets,32 repetitions | Pointwise improvement does not guarantee response-boundary restoration |',
'| Floating evidence | Controlled kappa=.8 OBC slice, N/chi/initial-chain and fitting-window checks; all failure records retained | No continuous floating interval established by current evidence |',
'| Dynamics | Historical Stage4/5 results retained with protected-input regression | No new quench scan; not counted as newly executed Stage6 work |','',
'See `EVIDENCE_LEDGER.json`, `decision.json`, raw indices and the executed notebook for newly executed versus historical or unexecuted work.']
(OUT/'report/BONUS_STATUS.md').write_text('\n'.join(bonus)+'\n')
print('Decision generated; incomplete execution groups:',missing)
