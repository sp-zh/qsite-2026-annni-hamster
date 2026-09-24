# Evidence ledger

## C1: B0 to B3 gate and correlation tradeoff

The cohort contains 420 descriptive N8 coordinates. Source: `results/stage4_upgrade_v1/matched_grid.csv`. Figure: `figures/resource_tradeoff.png`. B3 lowers noisy correlation error while reducing ideal preparation coverage. These results measure observable reconstruction, not phase accuracy.

## C2: Equal-CNOT-shots ZNE MSE reductions

The cohort covers 45 coordinates at 3 noise probabilities, with 32 repeats. Source: `results/stage6_followup_v1/B_index.json + active saved counts`. Figure: `figures/equal_resource.png`. Only 6 coordinates have independent labels, and the 17-component metric includes correlated components. G measures CNOT-shots rather than total execution cost.

## C3: Observable reconstruction and feature matching

The cohort covers 6 windows of 17 points at 3 noise probabilities, with 32 repeats. Source: `results/stage6_followup_v1/window_completion/curves.json + matches.json`. Figure: `figures/six_windows.png`. Observable reconstruction and feature matching give distinct results. Five references pass the frozen peak criterion; the records retain endpoint, branch and preparation flags.

## C4: Low-field H6 candidates and resource costs

The low-field cohort contains 48 of the 96 new confirmation coordinates. Source: `results/stage6_v1/confirmation/confirmation_all_selected.csv`. Figure: `figures/extensions.png`. H6 improves candidate availability at extra cost. The comparison also retains its negative transfer result on N12.

## C5: Floating-phase scan

The cohort is a multi-size OBC slice at kappa=.8. Source: `results/stage6_v1/floating_boundary_scan/interval_evidence_v4.json + evidence_map_v4.json`. Figure: `figures/floating_evidence.png`. The screened subset includes samples at .4/.425. The scan establishes zero supported floating samples and zero transition brackets.

## C6: Trotter and noise dynamics

The cohort contains archived product-state quenches. Source: `results/stage4_upgrade_v1/dynamics/*.npz`. Figure: `figures/dynamics.png`. These executed dynamics experiments measure Trotter and noise effects; they do not classify ground states.

Per-file hashes, run identifiers and literal archived parameters are in provenance/SOURCE_MAP.csv and the original indices.
