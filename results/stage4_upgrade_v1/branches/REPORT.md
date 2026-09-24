# Actual structure/compilation switch audit

Disposition: newly_executed, except explicitly historical B0/ED inputs.

57 actual neighboring structure pairs. Transport uses explicit fixed-structure energy refits at common coordinates; this is not a pre-existing scan chain or merely an opposite-direction comparison. Both parameter and output hashes retained.

```json
[
  {
    "method": "B3",
    "p": 0,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 0,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  },
  {
    "method": "B3",
    "p": 0.01,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 51,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  },
  {
    "method": "B3",
    "p": 0.05,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 58,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  },
  {
    "method": "B4",
    "p": 0,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 0,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  },
  {
    "method": "B4",
    "p": 0.01,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 39,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  },
  {
    "method": "B4",
    "p": 0.05,
    "intervals": 57,
    "qualified_endpoint_comparisons": 103,
    "sensitive": 53,
    "meaning": "Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02"
  }
]
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_b4_branches.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
