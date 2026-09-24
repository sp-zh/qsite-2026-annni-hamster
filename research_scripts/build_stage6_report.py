"""Research report from executed result files; missing work remains explicit."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *

def read(path,default=None):
    p=OUT/path
    return json.loads(p.read_text()) if p.exists() else default
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(map(str,r))+' |' for r in rows]])
def number(x):
    return 'not executed' if x is None else f'{x:.6g}'
def candidate(task):
    folder='failure_mechanisms' if task in ['development','validation'] else 'confirmation' if task in ['confirmation','stability'] else 'n12_transfer'
    return read(f'{folder}/{task}_paired_summary.json',{})
now=datetime.now(timezone.utc).isoformat()
ledger=read('report/EVIDENCE_LEDGER.json',{})
resources=read('verification/resource_summary.json',{})
mps_version=next(v for v in [4,3,2] if (OUT/f'floating_boundary_scan/interval_evidence_v{v}.json').exists())
atlas_version=next(v for v in [6,5,4] if (OUT/f'reference_atlas/reference_regions_v{v}.json').exists())
floating=read(f'floating_boundary_scan/interval_evidence_v{mps_version}.json',{})
coverage=read('end_to_end/boundary_coordinate_coverage.json',{}).get('rows',[])
binary=read('noise_diagnosability/interpretation.json',{}).get('summary',[])
cross=read('noise_diagnosability/cross_structure_summary.json',{}).get('summary',[])
lines=['# ANNNI Stage 6: research results and limits','',f'Run `{PLAN["run_id"]}`. Report generated {now}. Original deadline {PLAN["deadline"]}.','',
'This report distinguishes state preparation, observable reconstruction, finite-size response features, and independently supported physical phase interiors. A preparation pass is not a phase label. A matched response coordinate is not sufficient evidence for a thermodynamic boundary. All numerical experiments are classical simulations; no quantum advantage, physical hardware execution or complete strong-noise recovery is claimed.','',
'## Scientific findings','',
'The new wall-basis construction improves N8 low-field candidate availability and selected-state acceptance on independent new coordinates, at substantially greater circuit and classical-search cost. It does not dominate B3 on validation, noisy reconstruction, or the initial N12 transfer. The frozen H6 rule is a regional union of physical and wall candidates, **not** the historical six-layer HVA.','',
'The independent reference atlas supplies conservative interior labels and named same-size ED response features. It leaves substantial competition-region label uncertainty. Exact circuit curves, finite-shot measurements and detector outputs are evaluated against those separate targets. Strong-noise failures include preparation-dependent bias and detector mismatch; retained binary-template information does not establish universal phase identifiability.','',
'## Executed scope and provenance','',
'[Evidence ledger](EVIDENCE_LEDGER.md), [machine-readable ledger](EVIDENCE_LEDGER.json), [metadata](../metadata.json), [methods](METHODS.md), and [unique execution costs](../verification/resource_summary.json) contain the reproducible inventory. Shared H6/C0 searches, quadratic/linear ZNE counts and historical results are not counted as independent new executions. Raw elapsed times overlapping recorded laptop sleep remain flagged; they are not clean CPU-efficiency comparisons.','']
lines.append(table(['Work','Actual index rows','Requested','Disposition'],[(x['name'],x.get('count','see source'),x.get('expected','—'),x['disposition']) for x in ledger.get('items',[]) if x.get('expected')]))
lines+=['','## Independent reference and evaluation targets','',
'R0 and explicitly qualified finite-field extensions identify supported interiors; RN retains same-size continuous observables and predeclared finite-size response features; OBC MPS evidence is reported separately as Rlarge. The exact transverse Ising control at kappa=0 has bulk critical h=1. No literature curve is used to paint an entire truth map. C(r) and SF are Fourier-related, not two independent votes. Binder, transverse response, fidelity susceptibility, relevant-sector spectra and size trends provide additional evidence.','',
'[Reference regions v4](../reference_atlas/reference_regions_v4.csv), [features](../reference_atlas/reference_features.csv), [boundary reference v4](../reference_atlas/boundary_reference_v4.csv), [analytic Ising control](../reference_atlas/analytic_Ising_reference.json).','',
'At positive h, connected negative off-diagonal Hamiltonian entries justify a unique positive ground state in the even-parity, zero-momentum sector. Residuals are checked against relevant sector splittings; this is not a projection of a VQE state. The archived historical N8 vectors were independently checked: all 261 reused reference vectors had residual <=2.145e-14. Full-space ordered-state cat splitting is not automatically a transition gap. h=0 retains its original incoherent classical mixture and missing pure-state fidelity intervals.','',
'The predeclared principal order-response reference is resolvable on14/15 N8 kappa slices and5/6 slices each at N12 and N16; kappa=.5 is unresolved. Other response, fidelity and spectral features remain distinct. At kappa=.8 the coarse principal feature is h=.575/.5/.4 for N8/12/16, demonstrating strong size dependence rather than a size-independent critical line. The separate fine circuit-window target uses its own identical-coordinate ED calculation.','',
'Confirmation physical-interior coverage is 24/96 coordinates, including only 4/48 low-field coordinates. RN pattern-proxy coverage is 64/96. Frozen detector training included 9 physical and 11 RN-proxy development labels, with 8 physical and 15 proxy validation labels. The original broad training-metadata wording is qualified by the saved scope audit; no post-confirmation relabelling/retraining is presented as a method improvement. New-coordinate testing measures interpolation within studied parameter regions, not unseen-phase extrapolation.','',
'## Candidate generation, ablations and cost','',
'The domain-wall identity and exhaustive N8/N12 reversible mapping are tested. The wall register retains the global spin bit and even periodic wall parity. Literal preparation and decoding CNOTs are charged and noisy. The variational objective remains the full ANNNI Hamiltonian. Restricted wall-number-conserving mixers are not used as complete ansatzes. Top-4 bounded forward search is compared with greedy growth; the development-only ED-fidelity fits are isolated oracle diagnostics. No oracle selects a confirmation circuit.','']
cr=[]
for task in ['development','validation','confirmation','n12','n12_192']:
    for r in candidate(task).get('summary',[]):
        if r['region']=='all':cr.append([task,r['method'],r['coordinates'],r['candidate_pool_exists'],r['observable_pass'],r['state_pass'],r['joint_pass'],r['median_cnots'],r['search_nfev']])
lines.append(table(['Dataset','Method','Coordinates','Qualified candidate exists','Observable pass','State pass','Joint pass','Median CNOT','Objective calls'],cr))
lines+=['','Region-specific confirmation and transfer results:','']
cr=[]
for task in ['confirmation','n12','n12_192']:
    for r in candidate(task).get('summary',[]):
        if r['region']!='all' and r['method'] in ['B3','C1','H6']:cr.append([task,r['region'],r['method'],r['coordinates'],r['candidate_pool_exists'],r['observable_pass'],r['joint_pass'],r['median_cnots']])
lines.append(table(['Dataset','Region','Method','Coordinates','Candidate exists','Observable pass','Joint pass','Median CNOT'],cr))
lines+=['',
'On N8 low-field confirmation, H6 has 18 newly passing and 8 regressing coordinates relative to B3. Median executed CNOTs rise from 32 to 127; low-field objective calls rise from 678,228 to 5,050,938. This is an equal-cap comparison, not a demonstrated equal-executed-cost breakthrough. Saved <=64/96/128-CNOT checkpoint joint counts are H6 15/18/37 and B3 26/26/27 out of 48; lower checkpoints were not independently reoptimized.','',
'Eight N8 low-field H6 failures have a qualified saved candidate, but the deployed energy/resource rule selects a near-half-fidelity, parity-even, translation-broken branch with accurate listed observables. Such cases retain their original state failure. The 12-coordinate, three-seed stability experiment gives two-of-three joint success at 10/12 for both B3 and H6; H6 all-three success is 9/12 versus B3 10/12. Improved stability is not established.','',
'[Paired ablations](../failure_mechanisms/paired_ablations.json), [failure attribution](../failure_mechanisms/attribution_v2.json), [N8 selection diagnosis](../confirmation/selection_failure_diagnosis.json), [N12 attribution](../n12_transfer/n12_failure_mechanisms.json), [observable errors](../confirmation/confirmation_observable_accuracy.json). Fixed-energy restarts, energy continuations and oracle fits retain failures. A failed bounded search is not proof of mathematical inexpressibility.','',
'## Response reconstruction and coverage','',
'All six predeclared kappa slices remain requested; same-size ED resolves five. Kappa=.5 remains unresolved. No nearest-reference arbitrary-peak matching, interpolation, smoothing or thermal-limit interpretation is introduced. Position errors below are conditional on the frozen named-feature match; missing and mismatched curves remain in the accompanying denominator.','']
br=[]
for r in coverage:
    if r['estimator']=='pure_circuit' or (r['p'] in [.01,.05] and r['budget']==100000 and r['estimator'] in ['raw','zne_quadratic']):
        br.append([r['method'],r['p'],r['estimator'],r['budget'],r['requested_physical_slices'],r['reference_resolvable_physical_slices'],number(r['mean_match_fraction_given_reference'])])
lines.append(table(['Method','p','Estimator','Shots/repeat','Requested slices','Resolvable reference','Mean match fraction / resolvable reference'],br))
lines+=['',
'Pure N8 curves match 4/5 resolvable slices for B3 and 5/5 for H6, with worst matched displacement .0125. All 17 B3 kappa=0 states pass joint preparation checks, yet the unsmoothed response has a competing peak and is unresolved under the frozen rule. Conversely, the recorded low-field antiphase cat control has F approximately .5 while passing the specified observables. Neither fidelity direction guarantees phase-task success.','',
'Only kappa=.45,.55,.8 have complete noisy windows. Each finite-shot window consists of 17 coordinates, with 32 independent full-window repetitions at each budget. Missing noisy windows remain in all budget-specific denominators; a v1 grouping omission was corrected in coverage v2, with the original retained.','',
'The frozen rule chooses the largest interior peak. A larger endpoint peak can coexist with an official match. At p=.05, raw B3 has 64 such matched-but-endpoint-dominated repetitions across the two low-field windows; these are not claimed as reliable physical-boundary recovery. H6 has low-field feature mismatches even at exact expectations. Quadratic ZNE can improve pointwise MSE without repairing a response feature. [Full curves](../end_to_end/figures/RN_noisy_response_curves.png), [coverage v2](../end_to_end/boundary_coordinate_coverage.json), [secondary endpoint/curve audit](../end_to_end/response_robustness.json), [state/task counterexamples](../failure_mechanisms/state_vs_task_counterexamples_v2.json), [actual branch comparisons](../failure_mechanisms/actual_branch_switches.json). The secondary audit is descriptive, not a newly validated replacement detector.','',
'## Noise failure ladder, detection and mitigation','',
'The ladder includes perfect ED observables, ideal ED finite shots, literal p0 circuit, noisy exact expectations, noisy finite shots and same-budget mitigation. ED distributions are ideal classical information references, not free hardware StatePrep. D2 requires full density-matrix access and is separately costed. D4 removes Fourier-redundant inputs and retains a covariance metric; D5 uses wall-number distribution and Mx. Neither is allowed coordinates, p or gate count as a phase-label shortcut.','',
'Historical B5 has exact-coordinate, exact-gate-table archived measurement matches at25/48 core coordinates;23 are explicitly unavailable. These are reused records with their old seeds/selection, not new Stage6 measurements or a complete48-point matched comparison. [B5 exact-match provenance](../end_to_end/B5_historical_matched.json).','',
'Validation alone selected quadratic ZNE for subsequent noisy confirmation, after the earlier candidate/detector freeze. Raw, linear ZNE, quadratic ZNE and signed SV remain side by side on the common core. The same total 10k/100k shots is split over all settings/scales; quadratic and linear fits share raw counts. All preparation, decode and folded CNOTs receive the prescribed target channel. Estimates are not clipped to look physical.','']
nr=[]
for task in ['core','confirmation','n12']:
    for key,r in read(f'end_to_end/{task}_summary.json',{}).items():
        if '_p0.05_100000' in key:nr.append([task,key,r['physical_coordinates'],number(r['MSE_ED_mean']),number(r['MSE_own_p0_mean']),r['total_shots'],r['total_gate_shots']])
lines.append(table(['Dataset','Arm p=.05,100k','Coordinates','MSE to ED','MSE to own p0','All-repeat shots','All-repeat CNOT-shots'],nr))
core_summary=read('end_to_end/core_summary.json',{})
dr=[]
for method in ['B3','H6']:
 for estimator in ['raw','zne','zne_quadratic','sv']:
  row=core_summary.get(f'{method}_{estimator}_p0.05_100000')
  if not row:continue
  values=[]
  for detector in ['D1','D3','D4','D5']:
   counts=row['label_repeat_counts'][detector]['physical_label'];values.append('unmeasured' if counts.get('unmeasured') else f"{counts.get('correct',0)/32:.4g}/13")
  dr.append([method,estimator,*values])
lines+=['','All frozen detector comparisons on the same13 independently labelled core coordinates (correct coordinate-equivalents after normalizing32 repeats):','']
lines.append(table(['Preparation','Estimator','D1','D3','D4','D5'],dr))
lines+=['','The old simple D3 raw detector already gives10/13 correct for B3 at p=.05, versus2/13 for new D4 and1/13 for new D5. D3 with quadratic ZNE gives11.0625/13 repeat-normalized correct coordinates. Thus D4/D5 do not establish a general strong-noise improvement over the frozen simple baseline. Their full outputs and failures are retained; the D4 raw-to-ZNE gain must not be presented as superiority to all old detectors. No post-test per-point detector switching is deployed.','']
lines+=['',
'On the 48-coordinate core, only 13 coordinates have independent physical-interior labels. B3 raw versus quadratic ZNE D4 results are 2/13 versus 11/13 correct at p=.05; H6 is 0/13 for both. The other 35 coordinates remain unlabelled, not automatically wrong. This is a local labelled-interior comparison, not full-map accuracy. Quadratic ZNE uses approximately three times the gate-weighted cost of raw at equal shots.','',
'The signed MSE decomposition keeps preparation, noise, sampling and cross terms separate. At p=.05/100k, B3 exact bias MSE is .0703458 and sampling-about-exact MSE is 1.41e-6; H6 values are .138851 and 1.56e-6. Increasing shots cannot remove this dominant bias. This alone does not distinguish recoverable detector bias from lost state information. [Signed decomposition](../end_to_end/core_error_decomposition.json).','',
'Four exploratory same-coordinate saved-growth controls give direct evidence for circuit-resource artifacts. At (kappa,h)=(.45,.0875), changing the actual saved checkpoint from31 to63 CNOTs changes m0 squared by -.001502 at p0, but -.231956 at p=.05; subtracting the p0 difference leaves -.230454. At (.55,.1),32 versus64 CNOTs changes the antiphase structure factor by -.000519 at p0 and -.105150 at p=.05. The Hamiltonian, seed and reference are held fixed; both parameters and structure change, so this is not an isolated one-gate causal effect. These controls support a preparation-resource contribution to spurious noisy response peaks, not a physical transition. They were selected after inspecting the windows and are explicitly exploratory, not blind confirmation or a new deployed selector. [Actual gates, parameters and controls](../failure_mechanisms/gate_jump_controls.json).','',
'Fourteen fixed binary pairs retain measured X/Z differences. Every 100k and 1M oracle query had zero observed errors among 64 queries per pair/method/p; this is not a zero-risk bound or a deployable phase classifier. Classical distribution distance never exceeds quantum trace distance. At p=.05, median DQ/TV is B3 .169896/.104636 and H6 .090142/.055750. All strong-noise pair groups include equal or rejecting frozen detector outputs despite oracle distinction.','',
'Twelve pairs lie on opposite sides of an RN feature and are not independently established opposite phases; equal class labels for such a pair are not automatically an error. Only two far-interior controls have independently supported opposite labels, and their results are separately grouped rather than extrapolated to near-boundary discrimination.','',
'Same-coordinate controls expose a confound: among 21 coordinates with both p0 fidelities >=.99, B3/H6 median trace distance changes from .00756 at p0 to .13544 at p=.05, and D4 outputs disagree at five coordinates. Retained differences can encode preparation-specific noise. It would be incorrect to call every rejected point information-theoretically impossible, or every distinguishable pair a correctly identified phase. [Binary results](../noise_diagnosability/interpretation.json), [cross-structure controls](../noise_diagnosability/cross_structure_summary.json).','',
'## Descriptive maps and N12 transfer','']
mr=[]
for task in ['low_map','map']:
    c=read(f'n8_maps/{task}_coverage.json',{})
    mr.append([task,c.get('executed_coordinates','not executed'),c.get('requested_coordinates',108 if task=='low_map' else 420)])
lines.append(table(['Map','Executed coordinates','Requested'],mr))
low_area=read('n8_maps/low_map_area_summary.json',{}).get('full',{}).get('methods',{})
if low_area:
 lines+=['','Low-field area-weighted ED-target MSE,32 independent repeats at100k total shots each:','']
 lowrows=[]
 for p in [0,.01,.05]:
  for method in ['B3','H6']:
   raw=low_area.get(f'{method}_{p}_raw',{});zne=low_area.get(f'{method}_{p}_zne_quadratic',{})
   lowrows.append([method,p,number(raw.get('MSE_ED_area_weighted')),number(zne.get('MSE_ED_area_weighted'))])
 lines.append(table(['Method','p','Raw MSE','Frozen quadratic-ZNE MSE'],lowrows))
 lines+=['','The low-field descriptive grid has100% executed area. Its main-map conservative physical-label rule assigns no independent discrete labels in this rectangle: detector colors are pattern outputs, not phase accuracy. Preparation joint-pass area is56.71% for B3 and75.14% for H6, different from unweighted point fractions because h spacing is nonuniform. H6 improves p0 observable MSE but has worse p=.01/.05 MSE even after mitigation. Independent confirmation physical coverage is reported separately above.','']
lines+=['',
'On the108-point low-field descriptive grid, selected joint acceptance is B3=72/108, C0=62/108 and H6=78/108; H6 observable acceptance is91/108 versus B3=72/108. H6 gains20 and loses14 joint passes. Gains concentrate at kappa<=.5, including11/12 versus3/12 at kappa=.5; selected-state regressions remain on the kappa>.5 side. Both B3/H6 median actual CNOTs are127 on this particular grid, but objective calls are1,501,203 versus10,965,334. These are unweighted point counts, not area-weighted phase accuracy or a second blind confirmation. [Per-slice counts and curves](../n8_maps/low_field_slice_accuracy.json).','',
'Map comparisons are descriptive and separate from confirmation. Unequal grids use intersected Voronoi-cell area weights and are not pooled by point count. A single 100k-shot map and the mean of 32 such maps have different total cost. Historical B3 map states are explicitly reused; H6 states and new noise/measurement records retain their provenance. [Map area summaries](../n8_maps/), [N12 same-size window](../n12_transfer/window_boundary_comparison.json).','',
'The initial N12 budget is 128 CNOTs at 24 difficult and 12 interior coordinates; a fixed 12-coordinate 192-CNOT extension is reported separately. The frozen N8 pool/selection is transferred without ED retuning. The full p0 local window has 16 coordinates; only six were preselected for noisy-window calculation, with an identical sparse ED reference. Those six points do not constitute a full-resolution noisy curve.','',
'The separate kappa=.55 N12 window gives H6 joint0/16 versus B3/C0/C1 joint7/16. All four methods pass observables on7/16. H6 selects near-half-fidelity branches on the first seven points despite qualified alternatives; the remaining nine lack a qualified saved candidate. Every method places the principal p0 response at h=.09375, one .0125 step above same-window ED at .08125 (reference interval [.075,.0875]). This is a finite-size feature displacement, not a thermodynamic boundary estimate. [Full unmasked curves and all-q comparison](../n12_transfer/figures/n12_full_window.png).','',
'## Controlled OBC slice and floating evidence','',
f'Current v2 supported samples: `{floating.get("supported_samples","not available")}`. Candidate floating samples: `{floating.get("candidate_floating_samples","not available")}`. Lower/upper transition brackets: `{floating.get("lower_transition_bracket")}` / `{floating.get("upper_transition_bracket")}`.','',
'The kappa=.8 scan covers h=.10 through .80, with N64 coarse data, N96/128 independent-chain controls, targeted N160/N192 and chi128/256 checks, and the failed chi512 continuation retained. Signed central-pair correlations preserve actual pair sets, oscillations and raw/connected distinctions. Ordered-platform, algebraic and exponential models use comparable data and held-out distance blocks. OBC central charge is freely fitted; profile-Friedel K follows the primary-paper operator mapping.','',
'At h=.4, N128 K approximately .36 conflicts with valid N160 values approximately .54/.56; h=.475 also has an N96/N128 conflict. At h=.5, increasing size gives K outside the proposed floating range despite central charge near one. These conflicts prevent those points from being called established floating interiors. The historical (.8,.5) and (1,.7) candidate-center interpretations require downgrade to near-boundary/crossover qualification. Old (.6,.2) data remain historical support, not a newly scanned second slice.','',
'The new Friedel analysis of historical N128 checkpoints gives window values .421/.417 at (.6,.2), but1.670/2.000 at (.8,.5), with a bound hit and poor residuals, and1.275/1.459 at (1,.7), with window instability and one poor fit. The latter are not reliable thermodynamic K estimates and do not prove a gapped phase. [Historical-checkpoint reanalysis](../floating_boundary_scan/historical_centers_friedel.json) is explicitly separate from newly executed MPS optimization.','',
'A chi512 timeout is a resource/solver outcome, not evidence excluding a floating phase. Solver stopping, chi agreement, initial-state agreement and N trends remain separate fields. Current finite sizes cannot generally exclude a very large-correlation-length gapped crossover. Do not connect isolated candidates into a continuous phase band. [Evidence v2](../floating_boundary_scan/interval_evidence_v2.json), [signed correlation and spectrum data](../floating_boundary_scan/), [Friedel sensitivity](../floating_boundary_scan/friedel_sensitivity.json).','',
'## Verification, reproducibility and remaining scientific work','',
'Actual test logs, protected-input hashes and scientific-payload hashes are under [verification](../verification/). The final executed [notebook](stage6_research.ipynb) reads archived runs and explicitly recomputes a lightweight literal-circuit check. It does not pretend to rerun the full experiment. Package extraction verification has its own external receipt; a packaging script or manifest alone is not evidence of successful clean extraction.','',
'From the combined extracted project, run `ANNNI_PYTHON=/absolute/path/to/locked/python bash scripts/reproduce_stage6.sh --verify`. Use `--redraw` for figures. Original numerical commands in `verification/progress_*.json` remain resumable only before the unchanged deadline; later research must register a new run rather than silently resetting this run.','',
'The principal unresolved issues are noise-sensitive circuit selection/structure changes, incomplete competition-region physical labels, lack of demonstrated N12 difficult-region advantage at 128 CNOTs, and insufficient controlled size/convergence evidence for a continuous floating interval. The valid N8 low-field candidate improvement and local mitigation results are retained despite these failures. No whole-region masking, threshold relaxation or post-test oracle switching is credited as a solution.','']
text='\n'.join(lines)+'\n'
confirmation_noise=read('end_to_end/confirmation_summary.json',{})
if confirmation_noise:
 assert all(r['physical_coordinates']==96 for r in confirmation_noise.values())
 rr=[]
 for key,r in confirmation_noise.items():
  if key.endswith('_p0.05_100000'):
   rr.append([key,*[number(r['label_repeat_counts'][d]['physical_label'].get('correct',0)/32) for d in ['D1','D3','D4','D5']]])
 block='\nThe complete96-coordinate noisy confirmation has24independently labelled coordinates. At p=.05 and100k totalshots per repetition, correct coordinate-equivalents after normalizing32repetitions are:\n\n'
 block+=table(['Frozen preparation / estimator','D1 /24','D3 /24','D4 /24','D5 /24'],rr)
 block+='\n\nB3 benefits from the validation-selected quadratic estimator, while H6 remains worse at strong noise. D3 remains competitive with or better than the new detectors. The other72coordinates are not assigned invented physical labels; RN-proxy agreement and regional macro scores are reported separately. [Full confirmation ladder](../end_to_end/confirmation_regional_ladder.json), [all detector comparison](../end_to_end/figures/confirmation_all_detector_comparison.png).\n\n'
 text=text.replace('## Descriptive maps and N12 transfer',block+'## Descriptive maps and N12 transfer')
d2=read('end_to_end/D2_full_state_windows.json',[])
if d2:
 block='\nD2 was actually evaluated on18complete curves: three windows, two preparations and three noise levels. Its reference is the same-window ED fidelity susceptibility, which is distinct from the order-response feature used above:\n\n'
 block+=table(['kappa','Preparation','p','ED feature resolvable','D2 feature resolvable','Position displacement'],[[r['kappa'],r['method'],r['p'],r['ED_peak']['resolvable'],r['peak']['resolvable'],number(r['position_error'])] for r in d2])
 block+='\n\nThis full-density-matrix diagnostic does not repair the strong-noise curves automatically: at kappa=.8, p=.05 the B3/H6 offsets are+.1125/+.1000. In low-field H6 curves noise creates competing structure-related features. A detected fidelity peak is not automatically a physical transition; [unmasked curves](../end_to_end/figures/D2_full_state_response_curves.png) retain all gate and parameter switches. Full state access is not included in10k/100k local-measurement budgets.\n\n'
 text=text.replace('## Noise failure ladder, detection and mitigation',block+'## Noise failure ladder, detection and mitigation')
if (OUT/'verification/confirmation_prefix_race_correction.json').exists():
 text+='\nA cached-replay index race was caught before final reporting: an intermediate confirmation analysis read15points while the completed96-point index was being replayed. The raw96-coordinate measurements remained intact. The intermediate15-point tables are preserved under `verification/confirmation_prefix_race_preserved/`; the index writer now refuses to shrink an existing completed prefix and verifies its scientific fingerprints, and full-cohort analysis asserts its required denominator. Final confirmation tables were recomputed from the stable96-point source. This changes orchestration/derived summaries only, not circuits, detectors, noise or measurements. See `verification/confirmation_prefix_race_correction.json`.\n'
paired_budget=read('n12_transfer/paired_budget_128_192.json',{})
if paired_budget:
 block='\nOn the exact12-coordinate N12 resource-extension subset, B3 joint acceptance rises10/12 to11/12 from cap128 to192, while H6 rises8/12 to10/12. The gains are in the four antiphase-band coordinates: B3 goes3/4 to4/4 and H6 goes2/4 to4/4. The four low-field coordinates in this registered stride all have h=.013; B3 remains3/4 and H6 remains2/4. Thus the extra budget repairs some band candidates, but neither improves low-field acceptance nor establishes an H6 advantage. H6 median selected CNOTs on the12points rise127 to192, versus B3 63.5 to64. These are separate bounded searches with the same seed/rule, not guaranteed monotone continuations of an identical circuit. [Exact-coordinate budget comparison](../n12_transfer/paired_budget_128_192.json).\n\n'
 text=text.replace('## Controlled OBC slice and floating evidence',block+'## Controlled OBC slice and floating evidence')
map_preparation=read('n8_maps/map_selected_preparation_summary.json',{})
if map_preparation:
 block='\nThe original420-coordinate descriptive map retains the historical B3 circuits and compares them with newly generated H6 circuits. These selected-state counts are separate from independent confirmation and from phase-label accuracy:\n\n'
 block+=table(['Region','Method','Coordinates','Observable pass','State pass','Joint pass'],[[r['region'],r['method'],r['coordinates'],r['observable_pass'],r['state_pass'],r['joint_pass']] for r in map_preparation['summary']])
 block+='\n\nThe rectangular subregions can overlap and their point counts must not be added. Nonuniform-grid area statistics are reported separately. [Selected preparation counts](../n8_maps/map_selected_preparation_summary.json).\n\n'
 area=read('n8_maps/map_area_summary.json',{}).get('full',{}).get('methods',{})
 if area:
  block+=table(['Full-map method / p / estimator','ED-target area MSE','Independent-label area coverage'],[[key,number(r['MSE_ED_area_weighted']),number(r['reference_label_coverage'])] for key,r in area.items()])
  block+='\n\nThe420-point map shows a small p0 preparation gain, but H6 has higher raw error at both nonzero noise levels. The supported-label area is only28.29%; colors elsewhere are detector outputs rather than verified phase labels. These mean-square errors average32independent100k-shot repetitions at each coordinate; the plotted single100k realization is distinguished from the3.2million-shot mean.\n\n'
 text=text.replace('## Controlled OBC slice and floating evidence',block+'## Controlled OBC slice and floating evidence')
side_samples=floating.get('supported_samples',{})
anti=side_samples.get('supported_antiphase_sample',[]);para=side_samples.get('supported_paramagnetic_side_sample',[])
if anti and para and not side_samples.get('supported_floating_sample'):
 lower=max(anti);higher=[h for h in para if h>lower]
 if higher:text+=f'\nThe unresolved window between independently controlled OBC side samples is h=[{lower:g},{min(higher):g}] at kappa=.8. This describes the interval between the supported antiphase and paramagnetic-side samples; without a supported intervening floating sample it cannot be split into two separately identified transition brackets. It is not a claim that the whole window is floating.\n'
ideal=read('end_to_end/ideal_ED_detector_boundaries.json',{})
detector_coverage=read('end_to_end/detector_boundary_coverage.json',{})
if ideal:
 block='\nThe ideal-information control feeds exact same-N ED features to the already-frozen detector, then compares its prototype-contrast response with the independently named physical-observable RN feature:\n\n'
 block+=table(['Detector','Requested / resolvable slices','Matched slices','Worst matched displacement'],[[r['detector'],f"{r['requested_physical_slices']} / {r['reference_resolvable_physical_slices']}",r['matched_slices'],number(r['worst_matched_error'])] for r in ideal['summary']])
 block+='\n\nD5 misses kappa=0 even with perfect ED information; this is a detector limitation before preparation or noise. D4 matches the five resolvable features, but its worst .0375 displacement exceeds the .0125 grid step and must not be described as exact reconstruction. Kappa=.5 remains reference-unresolved. [All ideal-information curves](../end_to_end/figures/ideal_ED_detector_response_controls.png).\n\n'
 if detector_coverage:
  dr=[]
  for r in detector_coverage['rows']:
   if r['p'] in [.01,.05] and r['budget']==100000 and r['estimator'] in ['raw','zne_quadratic']:
    dr.append([r['method'],r['p'],r['estimator'],r['detector'],r['requested_physical_slices'],r['reference_resolvable_physical_slices'],number(r['mean_match_fraction_given_reference'])])
  block+=table(['Preparation','p','Estimator','Detector','Requested','Resolvable','Mean match fraction / resolvable'],dr)
  block+='\n\nEvery detector/budget group retains all six requested slices, five resolvable references and the three unexecuted noisy windows. Repetitions are normalized within each physical slice. This prototype-response metric is separate from direct observable-response reconstruction and from independent phase-label accuracy. [Full detector coverage](../end_to_end/detector_boundary_coverage.json).\n\n'
 text=text.replace('## Noise failure ladder, detection and mitigation',block+'## Noise failure ladder, detection and mitigation')
translation=read('failure_mechanisms/translation_sector_diagnostic.json',{})
if translation:
 trs=[]
 for task in sorted({r['task'] for r in translation['rows']}):
  rr=[r for r in translation['rows'] if r['task']==task]
  trs.append([task,len(rr),number(min(r['momentum_weights'][0] for r in rr)),number(min(r['conditional_T0_fidelity_diagnostic'] for r in rr))])
 block='\nOffline full-state momentum decomposition was applied to every H6 observable-pass/state-fail case in these completed cohorts:\n\n'
 block+=table(['Cohort','Cases','Minimum T0 weight','Minimum conditional T0 fidelity'],trs)
 block+='\n\nThis supports the translation-branch explanation for near-half fidelity. Weighted momentum-sector energies and translation-averaged observables reconstruct the unprojected values within1e-9. Global-spin parity verification does not project onto translation momentum and therefore cannot be credited with repairing this preparation defect. These mathematical projected components are not prepared circuits or a deployable repair, and their conditional fidelity is not substituted for the original state acceptance. Their energy expectations are not an exact low-energy spectrum. All original failures remain failures. [Offline diagnostic](../failure_mechanisms/translation_sector_diagnostic.json).\n\n'
 if (OUT/'failure_mechanisms/reference_translation_controls.json').exists():
  block+='Four literal parameter-free reference-circuit controls at(kappa,h)=(.55,.01) isolate an initial-state difference: physical antiphase preparation has T0 weight1 and fidelity .999834/.999752 for N8/N12, whereas the decoded alternating-wall reference has T0 weight.5 and fidelity .499917/.499876. Their energy and all listed C/SF/Mx observables agree within1e-12; both pass the observable thresholds. Actual CNOT counts are6 versus7 atN8 and10 versus11 atN12. The wall reference is a global-spin-flip pair rather than the full translation orbit. This is a concrete reference-design limitation, not proof that the adaptive pool cannot reach the desired state, and no projected output is credited as a prepared state. [Gates and unprojected states](../failure_mechanisms/reference_translation_controls.json).\n\n'
 text=text.replace('## Controlled OBC slice and floating evidence',block+'## Controlled OBC slice and floating evidence')
n12_noise=read('n12_transfer/noise_scope_interpretation.json',{})
if n12_noise:
 block='\nThe12preselected noisy coordinates contain six main-cohort points and six window points, not the full36-coordinate transfer sample. The registered stride selected low-field interior controls and no high-field paramagnetic control: this is a difficult-region noise test, not all-phase N12 coverage. At100k total shots per repetition and32repetitions, the results are:\n\n'
 block+=table(['Preparation','p','ED-target MSE','Own-p0 MSE'],[[r['method'],r['p'],number(r['MSE_ED']),number(r['MSE_own_p0'])] for r in n12_noise['noise']])
 block+='\n\nH6 has lower ED-target MSE on this subset at p0/.01 but higher MSE at p.05. The B3 p0 mean is dominated by the retained(.507,.013) failure: its preparation MSE is .34545 versus H6 .000390. H6 actually selects the physical C0 branch here (128CNOTs versus B3 10), so this is not evidence isolating a wall-basis benefit. Both still fail the original state and observable acceptance; fidelity improves from about7.8e-6 to .395. This is a concrete continuous-observable improvement, not a universal N12 advantage or a newly passing point; the other difficult coordinates and original failures remain in the tables. At p=.05 exact bias dominates sampling-about-exact MSE (about0.9e-6 B3 and1.1e-6 H6). In the sparse6-point window, the p.05 H6 peak remains at .09375, but its response amplitude is only about9.1% of the same-grid ED peak. B3 instead places the peak at .05625, displaced by-.0375; the frozen matching tolerance still accepts it. Both use grid intervals of width .0375. These are coarse RN feature comparisons, not restored thermodynamic boundaries; the finer16-point p0 reference remains separate. [Sparse-window evidence](../n12_transfer/noise_scope_interpretation.json); [all-q noise comparison](../n12_transfer/figures/n12_all_q_noise.png).\n\n'
 text=text.replace('## Controlled OBC slice and floating evidence',block+'## Controlled OBC slice and floating evidence')
if mps_version>=3:
 text=text.replace('Current v2 supported samples',f'Current v{mps_version} supported samples').replace('Evidence v2',f'Evidence v{mps_version}').replace('interval_evidence_v2.json',f'interval_evidence_v{mps_version}.json')
 text+='\nA single pre-registered h=.425 antiphase-chain continuation is included in evidence v3. Its original stopping-limited predecessor and evidence v2 remain archived. This updates large-size physical interpretation only, not frozen candidate/detector selection or confirmation labels. See `floating_boundary_scan/final_continuation_index.json` and its raw stopping fields.\n'
if atlas_version>=5:
 text=text.replace('Reference regions v4',f'Reference regions v{atlas_version}').replace('reference_regions_v4',f'reference_regions_v{atlas_version}').replace('boundary reference v4',f'boundary reference v{atlas_version}').replace('boundary_reference_v4',f'boundary_reference_v{atlas_version}')
if mps_version>=4:
 text+='\nEvidence v4 additionally includes the pre-registered N160, h=.425 independent plus/antiphase size checks, with all outcomes and failed stopping retained. This directed size test was registered before the N128 continuation outcome; it does not select a point by closeness of fitted central charge to one. See `floating_boundary_scan/h425_size_index.json`.\n'
 text+='\nBoth N160 initial chains meet the original solver stopping tolerances (397.16s plus,318.67s antiphase). Their Friedel fits hit the upper parameter bound in both windows: the recorded value2 is an invalid bounded-fit output, not a measured physical K. The free OBC c fits are about1.293 and1.348, versus about1.00–1.07 at N128; including the registered oscillation correction leaves the N160 values about1.2928/1.3478. Onlychi256 was tested at N160,h=.425: stopping and initial-chain agreement do not themselves establish bond-dimension convergence there. Power-law predictive fits improve over their competitors at N160, but these model and size sensitivities do not establish a controlled floating interval or exclude a very-long-correlation-length gapped crossover. No additional MPS expansion was launched.\n'
bottlenecks=read(f'floating_boundary_scan/evidence_bottlenecks_v{mps_version}.json',{})
if bottlenecks:
 target=next(r for r in bottlenecks['rows'] if r['h']==.425)
 text+='\nFor h=.425 the legacy candidate-status wording must not be read as an assertion that every control failed. The actual unmet evidence gates are: '+', '.join(target['unmet_floating_evidence_gates'])+'. The N128 continuation now meets its stopping rule. Its two-chain observables agree, but the power model does not exceed the ordered competitor by the frozen10percent held-out-error margin in every window. That margin is an engineering discriminator, not a statistical significance test or evidence excluding a phase. Larger-size results remain separate below.\n\n'
 text+=table(['N','chi','Initial chain','Stopping passed','K windows','Unmet signature checks'],[[r['n'],r['chi'],r['initial'],r['solver_stopping_pass'],','.join(number(x) for x in r['K']),'; '.join(r['failed_signature_checks']) or 'none'] for r in target['signatures']])+'\n'
 text+=f'\n[Expanded frozen-criterion explanations](../floating_boundary_scan/evidence_bottlenecks_v{mps_version}.json). These explanations do not change any archived phase status or threshold.\n'
(OUT/'report/REPORT.md').write_text(text)
print('Report generated from current executed files at',now)
