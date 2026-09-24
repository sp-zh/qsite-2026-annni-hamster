# Operational diagnostics v1 — actual ED-data run



All four baseline NPZ files were loaded and validated; no ED baseline was rerun. All outputs are finite-size diagnostics. Configuration was frozen before noise evaluation.



## Protocol

Full q is retained. Equivalent k and N−k peaks are averaged, not summed; near peaks lie within max(0.005, 10% of maximum). The CSV retains every near-maximum equivalence class. Flat mixed-state spectra consequently have many equivalent candidates.

Order-parameter negative derivatives and Mx derivatives use numpy.gradient(edge_order=2), h>0 only. All local maxima (including plateau centers) and one-sided endpoint maxima are saved. chiF/N remains at h_mid; NaN intervals touching h=0 remain missing. No smoothing or interpolation is applied. Derivative brackets are neighboring grid nodes; chiF brackets are its original pair of h nodes. These are resolution supports, not confidence intervals.

The auxiliary prototype check uses [m0², 2 mπ/2², Mx], Euclidean distances to analytic ferro [1,0,0], antiphase [0,1,0], plus [1/N,2/N,1], and mixed [1/N,2/N,0]. A label needs distance ≤0.45 and runner-up margin ≥0.10; otherwise uncertain. Mixed resemblance is degraded. These engineering thresholds are declared, not trained or tuned on noisy observations. Labels mean resemblance, not validated phase assignments. Scores subtract self background but are not clipped, so negative excess correlation remains visible.

All 12 N=8/12/16 controls returned their intended diagnostic. The maximally mixed state is degraded and is distinct from plus. protocol.json is the frozen copy.



## Observed full-wavevector behavior

- N=8: first sampled h with a non-π/2 mode strictly stronger than the π/2 mode: None. This is a discrete mode competition observation, not a phase boundary.

- N=12: first sampled h with a non-π/2 mode strictly stronger than the π/2 mode: 0.65. This is a discrete mode competition observation, not a phase boundary.

- N=16: first sampled h with a non-π/2 mode strictly stronger than the π/2 mode: 0.5. This is a discrete mode competition observation, not a phase boundary.



## Local peaks at κ=0.8 (all peaks retained in CSV)

- N=8, negative_order_derivative: h=0.600, support [0.550, 0.650], endpoint=False.

- N=8, mx_derivative: h=0.500, support [0.450, 0.550], endpoint=False.

- N=8, chi_f_per_site: h=0.525, support [0.500, 0.550], endpoint=False.

- N=12, negative_order_derivative: h=0.500, support [0.450, 0.550], endpoint=False.

- N=12, mx_derivative: h=0.500, support [0.450, 0.550], endpoint=False.

- N=12, chi_f_per_site: h=0.525, support [0.500, 0.550], endpoint=False.

- N=16, negative_order_derivative: h=0.450, support [0.400, 0.500], endpoint=False.

- N=16, negative_order_derivative: h=1.550, support [1.500, 1.600], endpoint=False.

- N=16, mx_derivative: h=0.450, support [0.400, 0.500], endpoint=False.

- N=16, chi_f_per_site: h=0.425, support [0.400, 0.450], endpoint=False.



## Comparison and limits

method_comparison.csv compares every local-change peak with the nearest same-N prototype transition interval. There is no requirement that a distance-to-control threshold coincide with a response peak; disagreement is preserved. No N=16 result labels N=8. Full-q plots separate weakening at fixed π/2 from growth of competitors. Neither observation alone establishes a floating phase. Finite-grid mode quantization, broad peaks, and analytic-prototype bias remain substantial limitations. No external phase reference curves were used.



## Reproduce

`.venv/bin/python scripts/run_diagnostics.py`

`.venv/bin/python -m pytest tests/test_diagnostics.py -q`
