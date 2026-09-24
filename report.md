# Noise-Aware ANNNI Phase Diagnostics

Low-CNOT preparation, error mitigation, and their limits

Team hamster: Shupei Zhang, Yangxin Zhou, Michael Li, Kathy Chen

## Model and approach

We study the periodic axial next-nearest-neighbor Ising chain H = -sum ZZ(nn) + kappa sum ZZ(nnn) - h sum X, J1=1. Competing interactions complicate state preparation and phase identification at low field. We evaluate state accuracy and observable errors separately from the evidence for phase boundaries. The N=8 circuits cover 420 positive-field coordinates. N=12 circuits and larger matrix-product-state (MPS) calculations with open boundaries extend the study across system sizes and boundary conditions.

## Preparation, noise and diagnostics

B0 is a fixed six-layer Hamiltonian variational ansatz. B3 adaptively grows energy-optimized Pauli rotations from multiple reference states and selects a circuit using a frozen energy/resource rule. After every executed CNOT, its target receives D_p(rho)=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ). This includes CNOTs used for reference preparation and folding. The explicit gate implementation preserves the recorded connectivity and wire-0-MSB convention. We measure the full C(r), all discrete structure factors and Mx. Frozen D3 uses PCA and clustering to classify resemblance to reference patterns; it supplies a diagnostic label rather than independent phase truth.

## Fewer CNOTs, lower preparation coverage

Replacing B0 with B3 reduces median CNOTs from 192 to 96, while ideal joint preparation passes fall from 407/420 to 385/420. At p=.01, the mean pointwise maximum correlation error falls from 0.2638 to 0.1432, with improvement at 402/420 coordinates. These values measure correlation reconstruction, not phase-classification accuracy. A joint pass requires delta e <= .001 per spin, C/SF/Mx errors <= .02 and squared ED fidelity >= .99.

## Comparison at equal CNOT-shots

We compare raw estimates, quadratic zero-noise extrapolation (ZNE) and global-X symmetry verification (SV) on 45 fixed coordinates, with 32 measurement repeats. Each method has the same per-coordinate budget G=sum(shots x literal CNOTs). Raw and SV use 100,000 shots; ZNE uses 33,334 across folds 1/3/5, with weights 15/8,-5/4,3/8. SV estimates (O+OP)/(1+P) using all required signed joint settings. Matching G controls CNOT-weighted shot cost. Measurement settings and one-qubit costs remain outside this budget.

## Observable errors and the zero-noise control

The ED-target MSE gives equal weight to the same 17 components: eight C, eight Fourier-related SF, and Mx. At p=.01, raw/ZNE/SV give 0.01754430/0.00162271/0.01235293; at p=.05 they give 0.10511371/0.07863611/0.10231166. ZNE lowers mean MSE by 90.75% and 25.19%, respectively, and improves the coordinate-mean error at all 45 points. At p=0, it worsens all 45. The reduction in bias comes with higher sampling MSE. Only six points have independent interior labels, so the 45-point result measures observable reconstruction rather than phase accuracy.

## Response-feature matching

We execute all six 17-point windows at kappa=0,.3,.45,.5,.55,.8 using identical grids and frozen matching rules. The .5 reference fails the frozen peak-selection criterion. The other five references describe finite-size RN features, not thermodynamic critical points. At p=.05 and 100k equal shots, raw estimates match 2.96875/5 window equivalents across repeats, compared with 2.875/5 for ZNE. The records retain endpoint domination, competing peaks, preparation errors and branch sensitivity. These results show why observable MSE and finite-size feature matching need separate evaluation.

## Low-field preparation and transfer

H6 combines physical and domain-wall candidates in a frozen union. On the N8 low-field cohort, candidate availability rises from 27/48 to 45/48 and selected joint passes from 27/48 to 37/48. This improvement costs more: median CNOTs rise from 32 to 127, and objective calls increase by 7.45x. On the N12 difficult/control transfer set, B3 passes 23/36 and H6 passes 17/36. H6 therefore improves the N8 low-field result at greater cost but reduces the pass count on this N12 cohort.

## Floating-phase search and extensions

The controlled kappa=.8 OBC slice supports an antiphase sample at h=.3 and a paramagnetic-side sample at h=.7. At h=.4/.425, the size, entropy and Friedel diagnostics disagree. The final evidence contains zero supported floating samples and zero established transition brackets. Bond-dimension convergence checks numerical stability; phase identification depends on gap and correlation-length scaling. The chi=512 run reached its time limit, which provides no basis for excluding a phase. The archived dynamics quantify Trotter and noise effects. The notebook also contains the multiple-detector and N12 experiments, all drawn from the frozen dataset.

## Conclusions and reproduction

Lower-gate preparation and cost-controlled mitigation improve observable reconstruction in these experiments. Reliable phase-boundary inference remains a separate requirement. We distinguish R0 region interiors, RN same-size diagnostics and Rlarge evidence qualified by system size. The main figures and statistics rebuild from the bundled numerical data and joint counts. The package also includes lightweight explicit-gate and SDK checks, with separate results for V1 deterministic saved-data verification, V2 physical checks and V3 exact random replay under its specified environment contract.

References: Q-SITE 2026 Scientific Track, snapshot 57f9a537 (local upstream/); Tang et al., qubit-ADAPT-VQE, arXiv:1911.10205; ANNNI tensor-network study, arXiv:2402.11022; floating-phase DMRG, arXiv:cond-mat/0702676; symmetry verification, arXiv:1807.10050. Published XX/Z conventions are related to ZZ/X by local Hadamards; boundaries and sizes are not interchangeable.
