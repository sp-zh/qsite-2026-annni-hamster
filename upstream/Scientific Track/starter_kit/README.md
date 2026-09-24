# Theory/Scientific Starter Kit

This folder contains the starter-kit code used by `starter.ipynb`.

- `annni.py`: ANNNI Hamiltonian construction in the repo's `Z/Z/X` convention
- `exact_diag.py`: exact-diagonalization helpers for small systems
- `observables.py`: finite-size order-parameter summaries
- `reference.py`: analytical overlay curves from the PennyLane ANNNI demo
- `noise_utils.py`: a small noisy ansatz demo using `DepolarizingChannel`
- `plotting.py`: coupling-graph plots, heatmaps, and a line-cut animation

The starter kit intentionally stops at reusable primitives. Teams still need to choose their own scan, classification, and analysis strategy.
