# Methods and evidence definitions

| Code | Meaning | Cost and scope |
|---|---|---|
| B0 | Fixed six-layer Hamiltonian variational ansatz | N8: 192 CNOTs; NN ZZ, NNN ZZ and RX layers; angles 2 theta |
| B3 | Multi-reference, energy-only adaptive Pauli rotations for low-CNOT preparation | Frozen energy/resource rule; energy breaks equal-CNOT ties, without a variance criterion |
| B5 | Baseline with stricter candidate selection | Stricter selection did not improve noisy correlations over B3 |
| C0/C1 | Stage6 physical-pool greedy / forward-search controls | C0 differs from the historical B3 pipeline |
| H6 | Frozen regional union of physical and domain-wall candidates | Distinct from six-layer HVA; costs include decoding and reference gates |
| raw | Unmitigated estimate | X/Z joint bitstring settings |
| linear ZNE | Linear intercept fitted at three scales | Archived separately from quadratic extrapolation |
| quadratic ZNE | Richardson weights 15/8,-5/4,3/8 at folds 1/3/5 | Local CNOT folding; costs include all shots and scales |
| SV | Signed global-X symmetry verification | (O+OP)/(1+P); 30 N8 settings; no momentum correction |
| D1 | Frozen physical-prototype resemblance | Original block distance includes C/SF redundancy |
| D2 | Full-state mixed-state distance diagnostic | Requires full-state access beyond local-shot resources |
| D3 | Frozen PCA / clustering interpreted through controls | Labels: ferro-like, antiphase-like, paramagnetic-like, degraded, unassigned |
| D4/D5 | Frozen Stage6 observable-only detector alternatives | Archived implementation and configuration; performance evaluated by cohort |

D3 is the established baseline. This release does not select it using confirmation accuracy or refit the archived detectors. The original detector implementation is annni/upgrade_detection.py; later definitions are in annni/stage6_detector.py and the original source files. Method names refer to their archived configurations.

R0 denotes an independently supported region interior. RN denotes a same-size ED finite-size feature. Rlarge denotes ED/MPS physical support qualified by system size. Applying D3 to ED produces an ideal diagnostic reference whose labels still require independent physical validation.

C(r)=sum_i<Zi Zi+r>/N; Mx=sum_i<Xi>/N; mq^2=sum_ij exp[iq(i-j)]<ZiZj>/N^2. We retain all q=2pi k/N, with C(0)=1 and SF self-background 1/N. The h=0 mixtures are treated separately. Fidelity is squared overlap, and chi_F=-log(F)/dh^2 is evaluated on h_mid. Missing pure-state fidelity intervals remain unfilled.

Pointwise maximum correlation error and the 17-component MSE measure different quantities. The MSE gives equal weight to eight C components, eight Fourier-related SF components and one Mx component, as in the archive. We report errors against ED and against the circuit-p0 target separately. The thirty-two repeats measure each physical coordinate repeatedly.

Main maps use exact expectations. Maps from one 100k repeat and from equal-shots ZNE are named separately. The preparation_failed overlays preserve the detector colors. Window audits determine branch_sensitive status; that status is not inferred for the main grid.
