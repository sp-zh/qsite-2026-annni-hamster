# Equal-shot ZNE and symmetry verification

Disposition: newly_executed, except explicitly historical B0/ED inputs.

15 coordinates, two p, folds1/3/5,30 SV measurement settings, total10k/100k shots and32 independent repetitions. Values are unclipped. Target is own clean circuit; bias, variance and MSE are distinct.

```json
{
  "raw_p0.01": {
    "mean_mse_10k": 0.02150192398022671,
    "mean_mse_100k": 0.0215825103310356,
    "points": 15,
    "bias_improved": 0
  },
  "zne_p0.01": {
    "mean_mse_10k": 0.011889009560301499,
    "mean_mse_100k": 0.011837935840010425,
    "points": 15,
    "bias_improved": 15
  },
  "sv_p0.01": {
    "mean_mse_10k": 0.01494700117844392,
    "mean_mse_100k": 0.014725527792063096,
    "points": 15,
    "bias_improved": 15
  },
  "raw_p0.05": {
    "mean_mse_10k": 0.13579989393956918,
    "mean_mse_100k": 0.13592399264603697,
    "points": 15,
    "bias_improved": 0
  },
  "zne_p0.05": {
    "mean_mse_10k": 0.1292168165363294,
    "mean_mse_100k": 0.12922278134678758,
    "points": 15,
    "bias_improved": 15
  },
  "sv_p0.05": {
    "mean_mse_10k": 0.13216900804256532,
    "mean_mse_100k": 0.1318957364632733,
    "points": 15,
    "bias_improved": 15
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_mitigation.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
