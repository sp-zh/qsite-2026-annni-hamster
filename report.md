# Noise-Aware ANNNI Phase Diagnostics

Low-CNOT preparation, error mitigation, and their limits

**Team hamster — Shupei Zhang, Yangxin Zhou, Michael Li, Kathy Chen**

## Problem and physical protocol

We study the periodic axial next-nearest-neighbor Ising chain H = -sum ZZ(nn) + kappa sum ZZ(nnn) - h sum X, J1=1. Competition between interactions makes low-field preparation and phase-feature interpretation difficult. We separate state accuracy, observable accuracy, and phase-diagram evidence. N=8 circuits cover 420 positive-field coordinates; N=12 and large-OBC MPS calculations supply qualified extensions.

## Preparation, noise and diagnostics

B0 is a fixed six-layer Hamiltonian variational ansatz; B3 adaptively grows energy-optimized Pauli rotations from multiple references and selects using a frozen energy/resource rule. Every executed CNOT receives target-only D_p(rho)=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ), including reference preparation and folding. Explicit gates retain wire-0-MSB order and recorded connectivity. Complete C(r), all discrete structure factors and Mx are measured. Frozen D3 is a PCA/cluster resemblance diagnostic, not an independent physical truth oracle.

## The low-CNOT tradeoff

B0 to B3 reduces median CNOTs from 192 to 96. Ideal joint preparation coverage decreases from 407/420 to 385/420. At p=.01, mean pointwise maximum correlation error decreases from 0.2638 to 0.1432; B3 improves 402/420 coordinates. These are correlation errors, not phase-classification errors. Joint acceptance keeps delta e <= .001 per spin, C/SF/Mx errors <= .02 and squared ED fidelity >= .99.

## Genuine equal-CNOT-shots comparison

On 45 fixed coordinates we compare raw, quadratic zero-noise extrapolation (ZNE), and global-X symmetry verification (SV), with 32 measurement repeats. G=sum(shots x literal CNOTs) is matched per coordinate: raw/SV use 100,000 shots; ZNE uses 33,334 across folds 1/3/5, with weights 15/8,-5/4,3/8. SV estimates (O+OP)/(1+P) from all required signed joint settings. Settings and one-qubit costs remain distinct; equal G is not equal total execution cost.

## Observable result and negative control

ED-target MSE averages the unchanged 17 components (eight C, eight Fourier-related SF, Mx). At p=.01, raw/ZNE/SV give 0.01754430/0.00162271/0.01235293. At p=.05 they give 0.10511371/0.07863611/0.10231166. ZNE reduces mean MSE by 90.75% and 25.19%, improving coordinate-mean errors at all 45 points. At p=0 it worsens all 45. Bias reduction is accompanied by larger sampling MSE. Only six points have independent interior labels; these results do not establish 45-point phase accuracy.

## Why feature reconstruction remains limited

All six 17-point windows at kappa=0,.3,.45,.5,.55,.8 are executed, with identical grids and frozen matching. The .5 reference is unresolved. The other five supply finite-size RN features, not thermodynamic critical points. At p=.05 and 100k equal shots, raw matches 2.96875/5 window equivalents across repeats; ZNE 2.875/5. Endpoint domination, competing peaks, preparation error and branch sensitivity remain explicit. Mean observable improvement does not imply feature stability; audited matches are not phase certificates.

## Low-field construction and transfer

The frozen H6 union of physical/domain-wall candidates increases candidate availability from 27/48 to 45/48, and selected joint passes from 27/48 to 37/48. Median CNOTs rise from 32 to 127; objective calls rise by 7.45x. This is not an equal-cost win. N12 difficult/control transfer gives B3 23/36 versus H6 17/36. H6 is not the six-layer HVA and is not promoted as a universal replacement.

## Floating search and other extensions

A controlled kappa=.8 OBC slice supports an antiphase sample at h=.3 and a paramagnetic-side sample at h=.7. h=.4/.425 remain candidates: size/entropy/Friedel evidence conflicts, and no supported floating sample or independent transition brackets are established. Bond-dimension convergence alone cannot exclude a long-correlation-length gapped crossover. A chi=512 timeout is a resource limit, not physical exclusion. Archived dynamics quantify Trotter/noise effects; multiple detectors and N12 experiments remain in the notebook. The published evidence is frozen.

## Conclusion and reproducibility

The evidence supports lower-gate preparation and cost-controlled mitigation as tools for observable reconstruction, while preserving the gap to reliable phase-boundary inference. R0 region interiors, RN same-size diagnostics, and Rlarge size-qualified evidence are separate. Main figures and statistics rebuild from bundled numerical data and joint counts. Lightweight explicit-gate and SDK checks are supplied. V1 deterministic saved-data verification, V2 physical checks and environment-gated V3 exact random replay are reported independently.

References: Q-SITE 2026 Scientific Track, snapshot 57f9a537 (local upstream/); Tang et al., qubit-ADAPT-VQE, arXiv:1911.10205; ANNNI tensor-network study, arXiv:2402.11022; floating-phase DMRG, arXiv:cond-mat/0702676; symmetry verification, arXiv:1807.10050. Published XX/Z conventions are related to ZZ/X by local Hadamards; boundaries and sizes are not interchangeable.
