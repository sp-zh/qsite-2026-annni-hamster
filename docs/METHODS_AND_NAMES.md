# Method and evidence dictionary

| Code | Meaning | Cost / limits |
|---|---|---|
| B0 | Fixed six-layer Hamiltonian variational ansatz | N8:192 CNOT; NN ZZ, NNN ZZ, RX layers; angles2theta |
| B3 | Multi-reference low-CNOT energy-only adaptive Pauli rotations | Frozen energy/resource rule; equal-CNOT ties use energy, not variance |
| B5 | Stricter selected-candidate baseline | More stringent selection did not improve noisy correlations over B3 |
| C0/C1 | Stage6 physical-pool greedy / forward-search controls | C0 is not the historical B3 pipeline |
| H6 | Frozen regional union of physical and domain-wall candidates | Not six-layer HVA; extra decoding/reference gates counted |
| raw | Unmitigated estimate | X/Z joint bitstring settings |
| linear ZNE | Three-scale linear intercept | Historical alternative; not quadratic extrapolation |
| quadratic ZNE | Richardson weights15/8,-5/4,3/8 at folds1/3/5 | Actual local CNOT folding; all shots/scales counted |
| SV | Signed global-X symmetry verification | (O+OP)/(1+P); 30 N8 settings; no momentum correction |
| D1 | Frozen physical-prototype resemblance | C/SF redundancy retained in original block distance |
| D2 | Full-state mixed-state distance diagnostic | Full-state access is not a local-shot resource |
| D3 | Frozen PCA / clustering with control interpretation | Main labels: ferro-like, antiphase-like, paramagnetic-like, degraded, unassigned |
| D4/D5 | Frozen Stage6 observable-only detector alternatives | Implementation/configuration retained; performance is evaluated by cohort |

D3 is retained as the established baseline, not chosen using confirmation accuracy in this release. Original detector implementation is annni/upgrade_detection.py; later detector definitions remain in annni/stage6_detector.py and original source files. Exact names are tied to their archived configs, not newly fitted.

R0: independent supported interior region. RN: same-size ED finite-size feature. Rlarge: size-qualified ED/MPS physical support. D3 applied to ED is ideal diagnostic reference, not independent truth.

C(r)=sum_i<Zi Zi+r>/N; Mx=sum_i<Xi>/N; mq^2=sum_ij exp[iq(i-j)]<ZiZj>/N^2. All q=2pi k/N retained; C(0)=1 and SF self-background1/N. h=0 mixtures are separate; fidelity is squared overlap, chi_F=-log(F)/dh^2 on h_mid. No missing pure-state fidelity interval is filled.

A pointwise max correlation error differs from the 17-component MSE. The latter retains eight C, eight Fourier-related SF, one Mx with equal component weight, exactly as archived. ED target and circuit-p0 target are separate. Thirty-two repeats are repeated measurements, not independent physical coordinates.

Main maps use exact expectations, with one100k-repeat and equal-shots ZNE maps separately named. preparation_failed overlays retain colors; branch_sensitive is a separately audited window status, not guessed for the main grid.
