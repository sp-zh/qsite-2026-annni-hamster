# Fixed-structure response controls

Disposition: newly_executed, except explicitly historical B0/ED inputs.

Two frozen structure anchors per kappa,20 fields. All local peaks and nested steps retained. Peak validation uses surrounding four-node preparation support; grid resolution intervals are not confidence intervals. Qualified kappa=.3 case has no resolved shift.

```json
{
  "points": 120,
  "noise_configs": 360
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_fixed_branches.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
