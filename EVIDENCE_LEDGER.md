# Evidence ledger

## C1: B0 to B3 gate/correlation tradeoff

Cohort: 420 descriptive N8 coordinates. Source: `results/stage4_upgrade_v1/matched_grid.csv`. Figure: `figures/resource_tradeoff.png`. Limit: Lower noisy correlation error sacrifices ideal coverage; not phase accuracy.

## C2: Equal-CNOT-shots ZNE MSE reductions

Cohort: 45 coordinates x3p x32 repeats. Source: `results/stage6_followup_v1/B_index.json + active saved counts`. Figure: `figures/equal_resource.png`. Limit: Only6 independent labels;17 correlated components; G not total cost.

## C3: Observable gains do not guarantee feature recovery

Cohort: 6 windows x17 points x3p x32 repeats. Source: `results/stage6_followup_v1/window_completion/curves.json + matches.json`. Figure: `figures/six_windows.png`. Limit: 5 reference-resolvable; endpoint/branch/preparation flags retained.

## C4: Low-field H6 candidate improvement at extra cost

Cohort: 48 of96 new confirmation coordinates. Source: `results/stage6_v1/confirmation/confirmation_all_selected.csv`. Figure: `figures/extensions.png`. Limit: Not equal-cost; N12 negative transfer retained.

## C5: Floating interval not established

Cohort: kappa=.8 OBC multi-size slice. Source: `results/stage6_v1/floating_boundary_scan/interval_evidence_v4.json + evidence_map_v4.json`. Figure: `figures/floating_evidence.png`. Limit: Candidate .4/.425; no independent transition brackets.

## C6: Executed Trotter/noise dynamics extension

Cohort: archived product-state quenches. Source: `results/stage4_upgrade_v1/dynamics/*.npz`. Figure: `figures/dynamics.png`. Limit: Not ground-state classification.

Per-file hashes/run identifiers and literal archived parameters are in provenance/SOURCE_MAP.csv and the original indices.
