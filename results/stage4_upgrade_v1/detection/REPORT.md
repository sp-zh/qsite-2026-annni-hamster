# Three diagnostic mechanisms

Disposition: newly_executed, except explicitly historical B0/ED inputs.

D1 observables, D2 squared Uhlmann on noisy slices, D3 frozen PCA/clustering. Analytic controls, Binder comparison, fixed branches and whole-bitstring shot sensitivity are saved. No independent finite-grid phase truth: error rates are undefined, not zero. See mechanism_comparison.json and comparison.csv.

```json
[
  {
    "task": "development",
    "method": "B1",
    "p": 0,
    "points": 18,
    "prep_pass": 11,
    "D1_rejected": 6,
    "D3_rejected": 1,
    "D1_D3_agreement": 11,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B1",
    "p": 0.01,
    "points": 18,
    "prep_pass": 11,
    "D1_rejected": 12,
    "D3_rejected": 3,
    "D1_D3_agreement": 9,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B1",
    "p": 0.05,
    "points": 18,
    "prep_pass": 11,
    "D1_rejected": 18,
    "D3_rejected": 17,
    "D1_D3_agreement": 17,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B2",
    "p": 0,
    "points": 18,
    "prep_pass": 2,
    "D1_rejected": 1,
    "D3_rejected": 1,
    "D1_D3_agreement": 18,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B2",
    "p": 0.01,
    "points": 18,
    "prep_pass": 2,
    "D1_rejected": 1,
    "D3_rejected": 1,
    "D1_D3_agreement": 18,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B2",
    "p": 0.05,
    "points": 18,
    "prep_pass": 2,
    "D1_rejected": 12,
    "D3_rejected": 2,
    "D1_D3_agreement": 8,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B3",
    "p": 0,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 6,
    "D3_rejected": 0,
    "D1_D3_agreement": 10,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B3",
    "p": 0.01,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 12,
    "D3_rejected": 4,
    "D1_D3_agreement": 10,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B3",
    "p": 0.05,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 18,
    "D3_rejected": 16,
    "D1_D3_agreement": 16,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B4",
    "p": 0,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 6,
    "D3_rejected": 0,
    "D1_D3_agreement": 10,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B4",
    "p": 0.01,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 12,
    "D3_rejected": 4,
    "D1_D3_agreement": 10,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "development",
    "method": "B4",
    "p": 0.05,
    "points": 18,
    "prep_pass": 14,
    "D1_rejected": 18,
    "D3_rejected": 16,
    "D1_D3_agreement": 16,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B1",
    "p": 0,
    "points": 48,
    "prep_pass": 33,
    "D1_rejected": 3,
    "D3_rejected": 0,
    "D1_D3_agreement": 44,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B1",
    "p": 0.01,
    "points": 48,
    "prep_pass": 33,
    "D1_rejected": 18,
    "D3_rejected": 2,
    "D1_D3_agreement": 32,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B1",
    "p": 0.05,
    "points": 48,
    "prep_pass": 33,
    "D1_rejected": 47,
    "D3_rejected": 45,
    "D1_D3_agreement": 46,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B2",
    "p": 0,
    "points": 48,
    "prep_pass": 4,
    "D1_rejected": 0,
    "D3_rejected": 0,
    "D1_D3_agreement": 48,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B2",
    "p": 0.01,
    "points": 48,
    "prep_pass": 4,
    "D1_rejected": 0,
    "D3_rejected": 0,
    "D1_D3_agreement": 48,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B2",
    "p": 0.05,
    "points": 48,
    "prep_pass": 4,
    "D1_rejected": 15,
    "D3_rejected": 0,
    "D1_D3_agreement": 33,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B3",
    "p": 0,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 3,
    "D3_rejected": 0,
    "D1_D3_agreement": 44,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B3",
    "p": 0.01,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 20,
    "D3_rejected": 2,
    "D1_D3_agreement": 30,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B3",
    "p": 0.05,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 47,
    "D3_rejected": 41,
    "D1_D3_agreement": 42,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B4",
    "p": 0,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 3,
    "D3_rejected": 0,
    "D1_D3_agreement": 44,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B4",
    "p": 0.01,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 20,
    "D3_rejected": 2,
    "D1_D3_agreement": 30,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "heldout",
    "method": "B4",
    "p": 0.05,
    "points": 48,
    "prep_pass": 42,
    "D1_rejected": 47,
    "D3_rejected": 41,
    "D1_D3_agreement": 42,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B3",
    "p": 0,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 16,
    "D3_rejected": 0,
    "D1_D3_agreement": 382,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B3",
    "p": 0.01,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 130,
    "D3_rejected": 15,
    "D1_D3_agreement": 305,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B3",
    "p": 0.05,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 413,
    "D3_rejected": 384,
    "D1_D3_agreement": 391,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B4",
    "p": 0,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 16,
    "D3_rejected": 0,
    "D1_D3_agreement": 382,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B4",
    "p": 0.01,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 130,
    "D3_rejected": 14,
    "D1_D3_agreement": 304,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  },
  {
    "task": "map",
    "method": "B4",
    "p": 0.05,
    "points": 420,
    "prep_pass": 385,
    "D1_rejected": 413,
    "D3_rejected": 384,
    "D1_D3_agreement": 391,
    "independent_error_rate": null,
    "reason": "No independent finite-grid phase labels; agreement is not accuracy"
  }
]
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_detection.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
