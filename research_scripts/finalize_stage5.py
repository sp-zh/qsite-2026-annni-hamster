"""Completion gates, scientific claim ledger and reproducible project entry point."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,sha,dump
required={'selector_benchmark/test/index.json':72,'selector_benchmark/n12test/index.json':24,'selector_benchmark/n12_192/index.json':84,'end_to_end/core_index.json':94,'end_to_end/refined_index.json':40,'end_to_end/full_best_index.json':420,'end_to_end/full_raw_index.json':420,'n12_scaling/noise_index.json':12,'end_to_end/n12_index.json':6,'floating_validation/index.json':39,'dynamics_validation/index.json':72}
for path,count in required.items():assert len(json.loads((OUT/path).read_text()))==count,(path,count)
st=json.loads((OUT/'submission/statistics.json').read_text());floating=json.loads((OUT/'floating_validation/evidence_update.json').read_text());n12=json.loads((OUT/'n12_scaling/analysis.json').read_text());audit=json.loads((OUT/'verification/result_audit.json').read_text());assert audit['passed']
ledger='''# EVIDENCE_LEDGER - Stage 5

| Claim | Computed evidence | Raw records / figure | Limits |
|---|---|---|---|
| S0 sometimes selects a failing state despite an available passing circuit | selection_audit/fixed_candidates.csv; selection_audit/summary.json; selection_audit/failure_details.json | selector_benchmark/audit/index.json; actual Stage4 cache paths within each candidate | ED is retrospective audit only; not deployed selection |
| New test improves 60/72 to 62/72; S1 achieves same count | submission/selection.csv | selector_benchmark/test/index.json, frozen/unsealed hashes; submission/figures/selection.png | Same fixed candidate sets; not unique evidence for symmetry advantage |
| The 31-CNOT counterexample fails fidelity while passing all observable tolerances | selection_audit/counterexample.json, selection_audit/failure_details.json | Original gate parameters and full C/SF/Mx; fixed-eight spectral overlap auxiliary | F near .5 alone does not establish a wrong phase label; actual frozen S1/S2 select98 CNOT, not the minimal passing32 |
| T magnitude, P and variance do not certify a ground state | tests/test_stage5.py; selection_audit/SYMMETRY_CONVENTIONS.md | Explicit nonzero-momentum and same-sector-excited counterexamples | S2 remains ideal-state-assisted design, no free output projection |
| B5 raises clean coverage slightly but loses B3 noise advantage | n8_maps/comparison.json | All420 ×3p noise archives; submission/figures/noise_comparison.png | Full-domain and paired populations, all failures retained |
| Equal-shot mitigation gives limited strong-noise anchor restoration | submission/end_to_end.csv, submission/paired.csv, submission/risk_coverage.csv | end_to_end/core_index.json; full joint counts/covariances; submission/figures/end_to_end.png |12 fixed physical anchors;32 measurement repeats, not384 independent parameter points; no whole-grid truth labels |
| Validation selects ZNE for the full descriptive map | end_to_end/mitigation_frozen.json | end_to_end/validation_index.json; end_to_end/full_best_index.json; n8_maps/maps.npz | Validation-only choice; test_v2 not used to tune estimator |
| Local peaks depend on branch, diagnostic and resolution | end_to_end/all_arm_curves.json, end_to_end/all_arm_peaks.json, end_to_end/fixed_peak_summary.json, end_to_end/fixed_shots_analysis.json | branches and branches_refined counterpart archives; state_access curves; submission/figures/local_fixed.png | D2 exact-density access is outside shot budget; grid supports are not statistical intervals; targeted fixed-shot case selection was exploratory |
| N12 selector and resource effects are distinct | n12_scaling/analysis.json |128 old/new candidate sets;192 paired runs; n12_scaling/noise_index.json and end_to_end/n12_index.json | Same seed/prefix is not independent restarting; failed preparations included |
| New OBC data tests prior floating evidence | floating_validation/evidence_update.json, floating_validation/neighbor_checks.json, floating_validation/control_checks.json, floating_validation/size_extension_analysis.json | N128 centers, N96/128 neighbors, raw correlations/entropy/sweeps/checkpoints; submission/figures/floating_neighbors.png | Numeric settings frozen; composite aggregation disclosed as post-start evidence review. No continuous interval or small-PBC label transfer |
| Finer Trotter steps can increase noisy error | dynamics_validation/analysis.json |72 new configs, raw time series and two actually recomputed old sequences; submission/figures/dynamics.png | Six new quench coordinates, no broad classification or dynamical-transition claim |

All paths above are relative to results/stage5_v1 unless explicitly marked as project tests or old Stage4 records. Every archived result records whether it was newly executed or reused by matching physical gates/parameters/backend. Downloaded full-text papers are omitted from redistribution; source access records remain.
'''
import re
for name in sorted(set(re.findall(r'(?:selection_audit|selector_benchmark|submission|end_to_end|n8_maps|n12_scaling|floating_validation|dynamics_validation)/[A-Za-z0-9_./-]+\.(?:json|csv|png|npz|md)',ledger)),key=len,reverse=True):
 assert (OUT/name).exists(), ('Missing ledger reference',name)
 ledger=ledger.replace(name,f'[{name}]({name})')
(OUT/'EVIDENCE_LEDGER.md').write_text(ledger)
bonus='''# BONUS_STATUS - historical and new evidence kept separate

| Bonus / contribution | Historical Stage4 | Stage5 actually executed | Remaining limitation |
|---|---|---|---|
| N>=12 circuit extension |60 preparations,12 representative three-p densities |24 new test points; paired60+24 at128/192;12 paired noise coordinates;6 finite-shot mitigation coordinates | No full N12 noisy map; fixed-budget failures remain |
| Multiple methods | ED/VQE, D1/D2/D3 and Binder | Nonoracle selector comparisons; same-coordinate five-arm D1/D3; D2 and fixed branches; N12 dimension-specific frozen PCA | Detectors are finite-size diagnostic protocols, not exact four-phase truth |
| Mitigation | ZNE/SV15-point study |94 core +40 refined coordinates ×3p; equal10k/100k budgets,32 repeats; validation24; full420 ZNE and matched raw shots; N12 SV | Strong-noise restoration limited; mitigation does not remove preparation bias |
| Floating physics | Three old centers had post-computation finite-window support | N128 centers/two inits/two chi; six neighboring fields atN96/128; critical/gapped controls; new block-validation checks | Discrete OBC evidence; composite aggregation not fully preregistered; finite-size/extrapolation remains |
| Dynamics |252 executed configurations |72 new configs and two direct old regressions | Short-time observables, not a proven classifier or thermodynamic dynamical boundary |

The predeclared N160 extension at (1,.7) actually completed at chi128/256 from one initial state, with c windows1.08340/1.05468. Its chi512 trigger was not reached. A measured hardware translation-projector protocol was not implemented. Chi512 follows only the recorded trigger; its actual request/index files determine whether it was needed and executed.
'''
(OUT/'BONUS_STATUS.md').write_text(bonus)
decision=dict(timestamp=datetime.now(timezone.utc).isoformat(),implementation_validation=dict(status='PASS',evidence='verification/result_audit.json and final tests'),selection_improvement=dict(status='LIMITED_GAIN_WITH_TAIL_FAILURES',new_test='60/72 ->62/72; S1 also62/72',deployment='NO-GO for unconditional S2/B5 replacement'),end_to_end_recovery=dict(status='LIMITED_ANCHOR_RECOVERY',full_map='37 anchors ×32: at p.05 D1 B5 raw0 -> ZNE96 correct; D3 raw96 -> ZNE97. No wrong accepted in this anchor set, remaining trials rejected.',p01='B3 and B5 already recover all12 anchors at100k; no added anchor coverage',p05='D1: B5 ZNE64/384 correct versus raw0. D3: B3 raw192/384 versus B5 raw/ZNE/SV64/384. All0 wrong in these12 anchors. Detector-specific partial recovery, not superiority to best old combination or full-map recovery'),n12=dict(status='COMPLETED_PAIRED_RESOURCE_TEST',summary=n12['summary'],scope='128/192 and selector effects,12 paired three-p coordinates,6 mitigation coordinates'),floating=dict(status='DISCRETE_EVIDENCE_REVIEW',center_grades=[dict(kappa=r['kappa'],h=r['h'],grade=r['new_grade']) for r in floating['rows']],preregistration_limit='Composite aggregation clauses disclosed after start; numeric settings frozen'),submission_readiness=dict(status='NUMERICAL_PACKAGE_READY_EXPORT_QA_REQUIRED',note='PDF/PPTX/notebook and fresh ZIP verification gates recorded separately; not a claim of visual rendering before QA'),full_phase_map_claim='NO-GO',hardware_advantage_claim=False)
dump(OUT/'decision.json',decision)
readme='''# Q-SITE 2026 ANNNI Scientific Track

Stage 5 is the current reproducible research package: [report](results/stage5_v1/REPORT.md), [executed notebook](results/stage5_v1/submission/submission.ipynb), [evidence ledger](results/stage5_v1/EVIDENCE_LEDGER.md), [decision](results/stage5_v1/decision.json).

The new selector improves preparation acceptance slightly, but its extra gates worsen raw noise relative to B3. Same-shot anchor outcomes, failed preparations, finite-size physics and state-access costs are retained. Results are local simulations, not hardware or a certified thermodynamic four-phase map.

## Existing locked environments

```sh
bash scripts/reproduce_stage5.sh --verify
bash scripts/reproduce_stage5.sh --report-only
bash scripts/reproduce_stage5.sh --resume
```

`--verify` does not optimize or simulate a full map. `--report-only` regenerates numerical summaries, figures and the notebook from saved data. `--resume` validates the original Stage5 deadline and fingerprints; it refuses to silently create a new12-hour budget. An explicit new run/config is required after the deadline. `ANNNI_PYTHON=/absolute/path/to/python` can point verification to an equivalent locked environment.

## Clean environment setup

```sh
uv venv --python 3.14.5 .venv
uv pip install --python .venv/bin/python -r requirements.lock.txt
uv venv --python 3.12.14 .venv-tn
uv pip install --python .venv-tn/bin/python -r requirements-tn.lock.txt
bash scripts/reproduce_stage5.sh --verify
```

Scientific execution used Python3.14.5 / PennyLane0.44.1 / NumPy2.5.3 / SciPy1.18.1. Tensor networks use isolated Python3.12.14 / TeNPy1.1.1. Lockfiles were not upgraded. PDF export uses a separate reportlab/pypdf runtime and slides use OfficeCLI; these presentation tools do not change the scientific environment. Fresh ZIP verification uses the existing locked interpreter on freshly extracted source/data, not an unclaimed fresh dependency installation.

## Paths and preserved history

- `results/stage5_v1`: new run, frozen plan, all candidate histories/selected parameters, literal gate keys, finite-shot joint counts, figures and reports.
- `results/stage4_upgrade_v1`: actual complete Stage4 upgrade, immutable historical input.
- `results/stage4_v1`: earlier local diagnostic campaign, also preserved.
- `results/stage3_v1` and `results/baseline`: historical HVA and ED data.
- `upstream`: original challenge snapshot; untouched.

Raw numerical JSON can contain Python-compatible NaN for undefined initial sweep differences; use the supplied Python readers. NPZ missing-state markers are preserved and must not be replaced by zeros.

PBC is used for N8/12 circuits; OBC is used for MPS. Wire0 is the most significant bit. All discrete q and the structure-factor self term are retained. Parameters stay fixed across noise levels. Every executed CNOT receives target-only depolarization, including reference preparation and ZNE folds; direct NN/NNN ring connections are assumed. No twenty-qubit Computational Track routing constraint is imported.

Full-text downloaded papers are not redistributed. Source URLs/access records and all required numerical inputs are included. See `deliverables/ZIP_VERIFICATION_STAGE5.json` and the SHA256 file for actual package/extraction checks. The previous README is retained at `results/stage5_v1/verification/README_before.md`.
'''
(ROOT/'README.md').write_text(readme)
# Freeze all new MPS numeric/raw/checkpoint files without touching old snapshots.
files={str(p.relative_to(ROOT)):sha(p) for p in (OUT/'floating_validation').iterdir() if p.suffix in ['.npz','.pkl'] or (p.suffix=='.json' and p.name.startswith('n') and 'chi' in p.name)};dump(OUT/'floating_validation/archive_manifest.json',dict(files=files,scope='new raw observables, per-run sweep logs and actual MPS checkpoints; derived analyses are separately covered by package manifest'))
print('Completion gates passed; ledger, decisions and README written')
