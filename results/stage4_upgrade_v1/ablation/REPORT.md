# Method-factor and compilation ablations

Disposition: newly_executed, except explicitly historical B0/ED inputs.

Includes independent23-CNOT pilot, two-site pool, bounded matched-call HVA, pruning/reoptimization, same-state compilation direction/commuting order, and literal single-error injection. Extra noisy evaluations are charged. Pilot input ZIP unavailable, so no original-file reproduction claim.

```json
{
  "development": {
    "points": 18,
    "single_plus_cost_pass": 11,
    "median_cnots": 112.0
  },
  "heldout": {
    "points": 48,
    "single_plus_cost_pass": 39,
    "median_cnots": 112.0
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_ablation.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
