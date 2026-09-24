# Second-order quench dynamics

Disposition: newly_executed, except explicitly historical B0/ED inputs.

252 configurations,11 public times, two fixed product initial states. Exact evolution isolates Trotter error. Frozen time means and held-out h=.6,1.4 descriptive static association are in static_association.json; four held-out coordinates do not validate a phase classifier.

```json
{
  "configs": 252,
  "parameter_initial_pairs": 28,
  "times": 11,
  "max_error_at_dt": {
    "0": [
      0.0011242198301673844,
      0.0045212215348365515,
      0.018441403278329143
    ],
    "0.01": [
      0.5022389603663506,
      0.40176581899264635,
      0.29739885602425875
    ],
    "0.05": [
      0.7730343857929398,
      0.6466887418175092,
      0.5340290317710943
    ]
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_dynamics.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
