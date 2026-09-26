# Noise-Aware ANNNI Phase Diagnostics

Q-SITE 2026, Quantum Coalition Scientific Track

Team hamster

Shupei Zhang · Yangxin Zhou · Michael Li · Kathy Chen

## Overview

We investigate the periodic one-dimensional ANNNI model under target-only depolarizing noise after every CNOT. We compare energy-optimized low-CNOT preparation and cost-controlled error mitigation against exact-diagonalization references. We assess observable errors and phase diagnostics separately to determine what the results establish about phase boundaries.

## Required deliverables

[Executed notebook](submission.ipynb) · [Offline HTML](submission.html) · [3-page report](report.pdf) · [Presentation PDF](presentation.pdf) · [Editable PPTX](presentation.pptx) · [Speaker notes](speaker_notes.md)

The eight-slide presentation has a 6 min 10 sec speaking plan. Team-confirmed competition status: `submitted: true`, `dashboard_status: draft`. The authenticated dashboard controls finalization and presentation delivery.

## Main results

- On the descriptive 420-point N8 grid, replacing B0 with B3 reduces median CNOTs from 192 to 96. Mean pointwise maximum correlation error decreases from 0.2638 to 0.1432 at p=.01 and 0.4454 to 0.3666 at p=.05. Ideal joint preparation coverage decreases from 407/420 to 385/420. These errors measure observable reconstruction; phase-label accuracy is evaluated separately.
- On 45 frozen coordinates, at equal actual CNOT-shots, quadratic ZNE reduces ED-target observable-vector MSE from 0.017544297 to 0.001622712 at p=.01 (90.75%) and 0.105113706 to 0.078636114 at p=.05 (25.19%). SV gives 0.012352926 and 0.102311658. These reductions apply to observable MSE and do not establish improved phase-map accuracy.
- G = sum(shots × literal CNOT count). Raw/SV use 100,000 total shots per repeat; quadratic ZNE uses 33,334 to match G. This budget excludes wall-clock time, one-qubit gates, measurement settings and classical processing. ZNE reduces bias while increasing sampling error; at p=0 it worsens all 45 coordinate-mean errors.
- All six B3 response windows are executed (κ=0,.3,.45,.5,.55,.8); the κ=.5 reference fails the frozen peak-selection criterion. Observable-error reduction and feature matching give distinct results. The records include endpoint, competing-peak and branch-sensitive failures.

We compute these results from [frozen statistics](release_statistics.json), using only 2,718 active followup records. The archive also contains 648 excluded attempts, which are kept separate from the final statistics. MSE retains the original 17 equal-weight components and 32 measurement repeats; only six of the 45 coordinates have independent interior labels.

## Phase diagrams

These N8 PBC maps use raw B3 exact expectations and the frozen D3 diagnostic, with the same axes and legend. Colors show estimated phase-like regions whose labels have not been independently validated. Crosses mark failed preparations; unassigned and degraded outputs have separate labels.

| p=0 | p=.01 | p=.05 |
|---|---|---|
| ![p0](figures/phase_p0.png) | ![p.01](figures/phase_p001.png) | ![p.05](figures/phase_p005.png) |

Finite-shot and full-grid equal-shots mitigation comparisons are separate in the notebook. The 45-point equal-G cohort is not extrapolated into a full equal-G map.

## Methods

ED references retain finite-size and OBC/PBC distinctions. B0 is a fixed six-layer HVA. B3 uses multiple references for adaptive low-CNOT preparation, and B5 applies stricter candidate selection. H6 combines physical and domain-wall candidates within a frozen region; it is distinct from the six-layer HVA. Every actual CNOT receives target-only PennyLane-convention depolarization. Frozen D1 through D5 diagnostics, raw, linear/quadratic ZNE and signed SV retain their original definitions. [Methods](docs/METHODS.md) · [Evidence ledger](docs/EVIDENCE_LEDGER.md).

## Extensions and limits

N≥12 circuits, multiple detectors, mitigation, Trotterized dynamics and floating-phase investigation were executed. H6 improves low-field N8 candidate availability at substantially greater gate/search cost; N12 difficult/control selected passes are 23/36 for B3 and 17/36 for H6. The dynamics experiments quantify the tradeoff between smaller ideal discretization error and extra noisy CNOTs.

At p=.05, the raw B3 D3 map contains 384/420 degraded points. The κ=.8 OBC evidence contains zero supported floating samples and zero established transition brackets. These experiments establish observable reconstruction gains and finite-size diagnostic results. [Results and limitations](docs/RESULTS_AND_LIMITATIONS.md) · [Bonus evidence](docs/BONUS_STATUS.md).

## Reproduction

Install the matching isolated environment using [instructions and tested locks](docs/REPRODUCE.md). From the repository root:

```bash
.venv/bin/python scripts/execute_notebook.py
.venv/bin/python scripts/release.py verify-physics --quick
.venv/bin/python scripts/release.py verify-data
.venv/bin/python scripts/release.py redraw --out build/redraw
```

Default notebook execution rebuilds statistics and plots, then runs representative explicit-circuit and saved-count checks. Deep V1 audits all active counts. V3 (`verify-exact-replay`) requires a matching environment and records a mismatch as SKIPPED_ENV_MISMATCH. Only a completed replay can return PASS. Outputs go to `build/`; no 9GB archive or optional tensor download is required. The original PennyLane implementation and SDK crosscheck are also available.

## Repository contents

Historical result paths keep references to coordinates, parameters and gates resolvable. The directories below group the evidence by its original experiment.

- `results/baseline/`: N8 ED and N8/12/16 slices.
- `results/stage3_v1/`, `stage4_v1/`, `stage4_upgrade_v1/`: preparation, B0/B3 main results, diagnostics, mitigation and dynamics.
- `results/stage5_v1/`: candidate-selection checks and independent physical/transfer evidence.
- `results/stage6_v1/`: reference atlas, low-field/confirmation, N12, noise, controlled floating scan and failures.
- `results/stage6_followup_v1/`: all six windows, equal-shots/equal-G comparisons, active indices and original joint counts.
- `annni/`, `configs/`, `research_scripts/`, `tests/`: actual algorithms, settings and checks.
- `provenance/`: source/path maps, scientific hashes, optional asset manifest.

Optional large tensors and deep indices are available as [17 verified Release assets](https://github.com/sp-zh/qsite-2026-annni-hamster/releases/tag/v1.0.0). The release asset tag preserves the initial publication snapshot; the current complete submission is the `main` branch.

See [full archive note](docs/FULL_ARCHIVE_NOTE.md) for optional tensor/large-index assets and exact exclusions. Scientific directories retain their indexed layout so archived paths and hashes continue to resolve. The package excludes environments, old packaging ZIPs and credentials.

## Attribution

Upstream challenge and starter materials: [benmcdonough20/QSITE-2026-QuantumCoalition](https://github.com/benmcdonough20/QSITE-2026-QuantumCoalition), local snapshot in `upstream/`. Preserve its [MIT license](docs/third_party/QuantumCoalition-MIT.txt). No global license is assigned to original team work without a team decision. [Third-party notices](docs/THIRD_PARTY_NOTICES.md).
