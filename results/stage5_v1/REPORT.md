# ANNNI Stage 5: selection, execution and independent checks

The unchanged joint preparation test passes at 60/72 new coordinates under S0 and 62/72 under frozen S2/B5. S1 energy minimization also passes 62/72. On the old descriptive grid, acceptance rises only from 385/420 to 388/420. The selected CNOT median rises from 96 to 128. This is a small clean-state coverage gain with an observable noise penalty, not a universal improvement.

## Model and nonoracle selection
The circuit model is the periodic Pauli ANNNI Hamiltonian, H=-sum ZZ_NN+kappa sum ZZ_NNN-h sum X, h>0, N=8 or 12. Wire 0 is the most significant bit. All distances and discrete wavevectors are retained, including the 1/N self-correlation term. The ideal period-four cat has m(pi/2)^2=1/2. OBC tensor-network evidence is treated separately.

Every actual CNOT is followed by target-only D_p(rho)=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ). Reference preparation and folding are charged; NN/NNN ring connections are direct. Measurement basis rotations are local (H for X, RX(+pi/2) for Y); SV needs no added entangling measurement gates. The measured setting audit records their one-qubit gate-shots separately, without imposing unrequested single-qubit noise. Parameters remain fixed across p=0,.01,.05.

For finite h>0, the connected computational-basis spin-flip graph and Perron-Frobenius positivity imply a unique positive ground vector, hence P=+1 and T=+1. Our own finite-system derivation and explicit algebra/counterexamples accompany the data. Nonzero momentum can have |<T>|=1, and a same-sector excited eigenstate can have zero variance. Neither parity, momentum-zero weight nor variance certifies fidelity.

A later audit also caught fractional-field filename aliasing in the auxiliary HVA baseline cache. The original Stage3 full grid was unaffected. All70 off-grid HVA coordinates were reoptimized with a full coordinate/configuration hash, three actual seeds each; affected B0 execution and shot statistics were recomputed. Old outputs and their additional compute cost are retained, with no detector or selection retuning.

A post-test compatibility audit caught and corrected the S0 same-CNOT tie ordering (energy, not variance). All 948 stored historical comparisons now reproduce the original parameters; affected raw B3 comparisons were rerun, prior records retained, and S1/S2 thresholds and choices were not retuned. S1 variance-tie removal changes none of the observed choices. S0 reproduces the old two-stage per-spin 1e-4 energy/resource window. S1 takes minimum energy with an absolute 1e-10 numerical tie. S2 requires w0>=.99 and w+>=.999999, then uses a per-spin 1e-6 energy/resource window. These values were selected on the new 24-point validation set and frozen before unsealing 72 new test coordinates. S2 is ideal-state-access-assisted classical design, not an implemented low-cost hardware measurement of translation. No output projection is applied. One bounded energy-only retry of at most 2000 iterations is triggered by the frozen energy-gap/qualification rule; no oracle enters selection.

## What changed, and what did not
Auditing all old checkpoints finds qualified candidates at 388/420 grid points, 43/48 old held-out points and 41/60 N12 points. Selection alone repairs only three, one and one old failures, respectively. Most remaining failures lack a qualifying saved candidate. At (.975,.15), the actual 31-CNOT GHZ candidate has F=.500010 and w0=.500032, yet its max correlation error is only .000255 and all observable tolerances pass. The 32-CNOT antiphase candidate has F=.999988 and max correlation error .0000404. Their energy difference is about .000450 total (.0000562 per spin), inside the old window. The actual frozen S1 and S2 choose an even lower-energy98-CNOT antiphase candidate (F=.99999978); they do not deploy the minimal known passing32-CNOT candidate. The pair31/32 is an explanatory counterexample, not the resource increment of the deployed selector. Thus the old failure concerns the pure-state criterion and cannot itself establish an incorrect physical label. All other checkpoints, translation weights and a separate low spectrum are also checked; a fixed lowest-eight subspace overlap remains auxiliary, never a replacement acceptance rule.

The 72-coordinate test is new; the original 420 and 48 are descriptive development data. Three reference starts share seed 11 and are not three independent seed replications. An unoptimized reference checkpoint has a legacy success flag, but derived optimizer-success counts now exclude it and report reference selections separately; the raw checkpoint flag remains preserved. The primary N8 cap remains 128 CNOT. Stricter S2 can discard a lower-energy imperfectly translation-symmetric state and retain a much worse symmetric candidate. Its rare large errors and unsuccessful retries remain visible. S1 matches the N8 pass-count gain, so the gain cannot be attributed uniquely to symmetry.

Full-grid mean maximum correlation error at p=.01 is B0 .2638, B3 .1432 and B5 .1821; at p=.05 it is .4454, .3666 and .4117. B5 therefore improves on the older deep HVA but degrades relative to B3. Longer and differently selected circuits both change the noise response; gate count alone is not an isolated causal variable. This precludes recommending an unconditional replacement on clean acceptance alone.

## End-to-end evaluation at a fixed denominator
Five arms are executed at the same 94 core coordinates: B0 raw, B3 raw, B5 raw, B5 ZNE and B5 SV. Three common local windows start at step .025 and are uniformly refined to .0125 for every arm and p. Fixed-structure continuation and actual same-coordinate structure-switch pairs distinguish preparation changes from diagnostic response. On the fixed kappa=.3 branch, the refined exact-density full-observable peak support changes from [.45,.4625] at p=0 to [.4875,.5] at p=.05, a positive grid-difference range [.025,.05]. Mx and D2 support the direction, with passing local preparation stencils and compatible coarse-grid supports. This is a circuit-protocol feature shift, not a Hamiltonian phase-boundary change. A targeted, explicitly exploratory 100k-shot follow-up has empirical shift ranges [-.11125,.09031] for the full-observable rate and [-.075,.13063] for Mx, both spanning zero: the shift is not resolved at that finite measurement budget. D2 uses full simulator densities and is outside the local-measurement shot budget.

Detector choice materially changes the strong-noise comparison. On the same12 anchors at100k shots and p=.05, D3 with B3 raw gives192/384 correct,0 wrong and192 rejected; D3 with B5 raw, ZNE or SV gives64/384 correct and0 wrong. Thus the D1-specific improvement of B5 ZNE over B5 raw is not an advantage over the strongest evaluated old-baseline/detector combination. All D1/D3 results are retained.

D1 and D3 retain frozen observable-only rules; no coordinates, p, reference or CNOT count are classifier inputs. Independently justified low-field ordered and high-field anchors are qualified and frozen before noise evaluation. Other coordinates have no asserted exact phase labels. Agreement with ED passed through the same detector is called diagnostic agreement, not physical classification accuracy.

At 100,000 total shots per coordinate/p and 32 independent measurement repetitions:

| p | arm | correct / all anchor trials | wrong accepted / all | rejected / all | MSE to own clean |
|---|---|---|---|---|---|
| 0.01 | B0_raw | 38/384 | 0/384 | 346/384 | 0.05877 |
| 0.01 | B3_raw | 384/384 | 0/384 | 0/384 | 0.01617 |
| 0.01 | B5_raw | 384/384 | 0/384 | 0/384 | 0.02225 |
| 0.01 | B5_zne | 384/384 | 0/384 | 0/384 | 0.01333 |
| 0.01 | B5_sv | 384/384 | 0/384 | 0/384 | 0.01603 |
| 0.05 | B0_raw | 0/384 | 0/384 | 384/384 | 0.15192 |
| 0.05 | B3_raw | 0/384 | 0/384 | 384/384 | 0.10211 |
| 0.05 | B5_raw | 0/384 | 0/384 | 384/384 | 0.12244 |
| 0.05 | B5_zne | 64/384 | 0/384 | 320/384 | 0.11927 |
| 0.05 | B5_sv | 29/384 | 0/384 | 355/384 | 0.12118 |

Raw uses two settings, ZNE six across folds 1/3/5, and parity SV 30 settings at N8 or 68 at N12. All share total budgets of 10,000 and 100,000 shots; whole-bitstring counts, covariance and gate-shots are saved. Distinct physical estimation keys use independent streams; identical circuit/coordinate/p/method keys intentionally reuse the same counts across arm labels. The shared-stream index corrects an overly broad early metadata phrase about independence across all arms; no independent cross-arm standard errors are assumed. A fixed linear ZNE intercept never includes ED or p=0 in the noisy fit. SV uses signed (O+OP)/(1+P); it cannot correct nonzero momentum. Estimates are not clipped. Validation-only mean MSE selected ZNE for the full-grid extension. Full-map extent is explicitly recorded in its index. A matching finite-shot raw comparator was also executed from the same saved scale1 distributions, without changing frozen rules. On the complete420-coordinate descriptive grid, the fixed anchor criteria qualify37 coordinates (1184 measurement trials). At p=.01 both B5 raw and ZNE identify all1184 under D1/D3. At p=.05 D1 correct counts rise from0 to96 with ZNE, with0 wrong accepts and1088 remaining rejections; D3 changes from96 to97 correct. This small gain does not restore a strong-noise phase map. Fewer rejections alone is not evidence of better identification.

## Twelve spins and independent large-system physics
The N12 comparison retains all 60 old and 24 new coordinates, with 128 and 192 CNOT caps. The 192 branch is a cold deterministic rerun with the same seeds and shares optimization prefixes; it is not an independent restart experiment. Fixed candidate selection, extra quantum gates and extra classical search are reported separately. S2 at each cap is tabulated before retries, and B5_192 after bounded same-gate retries. The larger cap also lengthens the adaptive search: matching per-optimization limits does not equalize total classical work, so its gain is a combined resource contrast, not a pure causal effect of gate count alone. At192 CNOT, the eight remaining old-point failures and seven new-point failures have no jointly passing saved candidate; every reference search stopped at the cap. Some selected circuits are much shorter because strict symmetry filtering rejects lower-energy candidates. At N12(.8,.7), S1 selects a192-CNOT candidate with w0=.98585, energy error/site .00513 and F=.97462; frozen S2 rejects it and selects a10-CNOT antiphase reference with w0~1, energy error/site .21978 and F=.06722. Neither passes, but the symmetry filter makes preparation much worse. This actual failure argues for a future, newly validated energy-quality safeguard, not retuning this test in place. This separates candidate-pool failure from selection-only repair but does not prove that more gates, rather than better optimization, would solve it. Twelve fixed coordinates receive paired three-p exact-density checks, including failed preparations; six coordinates receive equal-budget raw/SV measurements with a separate N12 PCA trained only on old clean development data. An exact classical reuse of the all-X density representation reduces repeated basis rotations for the68 joint distributions. A real N12 noisy-density cross-check found max probability difference1.3e-18 and pilot times210.64s versus26.02s; another density job was active, so the8.09x ratio is a pilot measurement. Physical measurement rotations and costs are unchanged. The new backend hash and RNG namespace were fixed before any N12 sampled result, with the old source retained. SV was declared for this extension before viewing N12 mitigated results to avoid additional folding evolutions; it does not assert that the N8 validation preference for ZNE transfers to N12.

N12 completed counts and acceptance:
- old_descriptive60 S0: 40/60; median 127 CNOT.
- old_descriptive60 S1: 40/60; median 128 CNOT.
- old_descriptive60 S2: 41/60; median 128 CNOT.
- old_descriptive60 S2_192: 52/60; median 192 CNOT.
- old_descriptive60 B5_192: 52/60; median 192 CNOT.
- new_test24 S0: 10/24; median 128 CNOT.
- new_test24 S1: 9/24; median 128 CNOT.
- new_test24 S2: 11/24; median 128 CNOT.
- new_test24 S2_192: 17/24; median 192 CNOT.
- new_test24 B5_192: 17/24; median 192 CNOT.

On all12 tested coordinates, raising the S2 cap128 to192 improves the noiseless max-correlation error, but makes it worse at both p=.01 and .05. Mean noisy increases are .05616 and .04565, with zero improved pairs at either level. This is the measured limit of the added preparation/search resource in the prescribed noise model; it does not establish that every untested coordinate behaves this way.

N12 actual paired noise results (negative change means improvement):
- p=0.01, S0_128 -> S2_128: paired mean change in max correlation error +0.03550; improved fraction 0.000 over 12 coordinates.
- p=0.01, S2_128 -> S2_192: paired mean change in max correlation error +0.05616; improved fraction 0.000 over 12 coordinates.
- p=0.01, S2_192 -> B5_192: paired mean change in max correlation error +0.00000; improved fraction 0.000 over 12 coordinates.
- p=0.05, S0_128 -> S2_128: paired mean change in max correlation error +0.04414; improved fraction 0.000 over 12 coordinates.
- p=0.05, S2_128 -> S2_192: paired mean change in max correlation error +0.04565; improved fraction 0.000 over 12 coordinates.
- p=0.05, S2_192 -> B5_192: paired mean change in max correlation error +0.00000; improved fraction 0.000 over 12 coordinates.

N12 same-budget raw/SV results at100,000 total shots and32 repetitions:

| p | estimator | MSE to own clean | MSE to ED | D1 correct / anchor trials | D3 correct / anchor trials |
|---|---|---|---|---|---|
| 0 | raw | 0.000001 | 0.001878 | 64/64 | 64/64 |
| 0 | sv | 0.000015 | 0.001897 | 64/64 | 64/64 |
| 0.01 | raw | 0.025658 | 0.022542 | 64/64 | 64/64 |
| 0.01 | sv | 0.021231 | 0.018518 | 64/64 | 64/64 |
| 0.05 | raw | 0.113048 | 0.104421 | 0/64 | 0/64 |
| 0.05 | sv | 0.113392 | 0.104711 | 0/64 | 0/64 |

The denominator includes only independently qualified anchors; zero anchor trials would mean no anchor accuracy estimate. The complete analysis separately retains accepted, wrong and rejected counts and all six coordinates, including preparations that fail. A smaller noise-only MSE does not establish restoration of the ED state or of an entire phase map.

TeNPy 1.1.1 uses OBC, Pauli operators and no U(1) constraint. Three old centers receive new N128 chi128/256 calculations from two initial states, with h +/- .025 neighbors at N96/128 and Ising/gapped controls. Signed oscillatory power and exponential fits have equal parameter counts. For distance r, correlations average origin sites i from N/4 up to min(3N/4,N-r), excluding that upper endpoint; at long distances the partner can approach an edge. Fits use r=2..floor(N/3) and r=4..N/2-2, with the last25 percent as the contiguous held-out block. These are finite-boundary-sensitive windows, not an assumed infinite-chain correlator. Final-distance-block extrapolation, two windows, raw/connected correlations, entropy and bond/size stability are separate checks; correlated distances do not yield naive statistical significance. The OBC entropy coefficient is c/6, with c fitted freely. An added oscillatory/finite-size regression is explicitly exploratory sensitivity and does not tune the main grade.

New center grades:
- (0.6, 0.2): supported_in_tested_window -> support_strengthened; c windows [1.0128013211240288, 1.0494876389252745]; chi-converged=True.
- (0.8, 0.5): supported_in_tested_window -> support_strengthened; c windows [0.9798721293393502, 0.9752169961592869]; chi-converged=True.
- (1, 0.7): supported_in_tested_window -> support_strengthened; c windows [1.0835854083632497, 1.0685409359399176]; chi-converged=True.

The configured solver stopping tolerances are unmet in 4/39 completed main MPS runs. This is recorded separately from changes under chi128 to256; a bond-stable result is not silently called fully converged. Actual sweep energy/entropy changes and discarded weights are preserved. At (1,.7), the two plain entropy-fit windows across sizes are: [(64, [1.144611611994371, 1.0931934650890949]), (96, [1.1327405582624859, 1.13941448007713]), (128, [1.0835854083632497, 1.0685409359399176]), (160, [1.083402634244325, 1.0546809625891371])]. The predeclared optional N160 check at this point completed at chi128/256, with one initial path; its two c windows are 1.08340 and 1.05468 and the chi512 trigger was not reached. It does not replace the main two-initial-state checks. This shows that the old elevated coefficient weakens but does not vanish uniformly with N; it is not a thermodynamic extrapolation.

Actual neighboring-point diagnostics (two fixed windows, all four raw/connected held-out comparisons retained):

| N | kappa | h | chi-stable | power wins | c windows | q windows |
|---|---|---|---|---|---|---|
| 96 | 0.6 | 0.175 | True | 4/4 | 0.979, 1.082 | 1.2977, 1.2984 |
| 128 | 0.6 | 0.175 | True | 4/4 | 0.989, 0.968 | 1.2929, 1.2935 |
| 96 | 0.6 | 0.225 | True | 4/4 | 1.074, 1.030 | 1.2356, 1.2360 |
| 128 | 0.6 | 0.225 | True | 4/4 | 1.046, 1.058 | 1.2432, 1.2436 |
| 96 | 0.8 | 0.475 | True | 4/4 | 1.080, 1.049 | 1.3655, 1.3663 |
| 128 | 0.8 | 0.475 | True | 4/4 | 1.077, 1.087 | 1.3670, 1.3675 |
| 96 | 0.8 | 0.525 | True | 4/4 | 0.856, 0.822 | 1.3459, 1.3467 |
| 128 | 0.8 | 0.525 | True | 4/4 | 0.867, 0.857 | 1.3459, 1.3463 |
| 96 | 1 | 0.675 | True | 4/4 | 1.148, 1.165 | 1.4307, 1.4311 |
| 128 | 1 | 0.675 | True | 4/4 | 1.107, 1.121 | 1.4362, 1.4370 |
| 96 | 1 | 0.725 | True | 4/4 | 1.021, 1.011 | 1.4160, 1.4166 |
| 128 | 1 | 0.725 | True | 4/4 | 1.020, 0.998 | 1.4156, 1.4162 |

Same-pipeline controls give the following freely fitted c windows: [(0, 1, [0.5152245148009229, 0.5123787539880094]), (0, 0.2, [-4.2779043674509883e-17, 8.194200199004826e-16]), (0, 1.8, [7.476467754553532e-08, 9.138679449190202e-11])]. The h=.525 neighbors at kappa=.8 retain coefficients around .82-.87, rather than exactly1; these windows remain finite-size evidence and are not forced to the expected value. Historical wider-side controls are plotted separately from these new neighbors.

The numeric settings and individual tolerances were frozen before calculation, but the composite requirement that all four held-out comparisons favor power and initialization differences stay below .01 was only made explicit after calculations started. This aggregation is conservative evidence review, not a fully preregistered phase test; the disclosure and all constituent checks are saved. Only tested discrete points are claimed. Bond convergence does not establish a thermodynamic size limit, and no OBC phase labels are transferred onto N8/N12 noisy states. Prior small-size OBC/PBC bridge and side controls remain explicitly historical evidence.

## Dynamics, decision and reproducibility
Seventy-two new quench configurations use six frozen coordinates, two original product states, two time steps and three p values. Two old noiseless sequences were actually recomputed. Halving dt reduces ideal discretization error but doubles CNOTs from 640 to 1280 and increases noisy total error. These finite-time features are not certified equilibrium labels or dynamical critical boundaries.

Decision: the implementation and controlled comparisons can be used; unconditional B5 replacement and a recovered p=.05 full phase map are not supported. Region-specific observable/anchor comparisons retain preparation_failed, selection_unresolved and branch_sensitive masks. All failures and limited resource effects remain part of the submission, not exclusions.

Run `bash scripts/reproduce_stage5.sh --verify`, `--report-only`, or `--resume` from the project root. Resume verifies fingerprints and the original Stage5 deadline without resetting it. The notebook reads stored experiments and performs a fresh explicit-circuit consistency check. Sources, raw candidate histories, joint counts, MPS checkpoints and package hashes accompany the report.

## Primary sources and scope
Boyd, Stanford EE363 Lecture17 (2008-09), Perron-Frobenius theorem, pp5-7, https://web.stanford.edu/class/ee363/archive/lectures/pf.pdf (newly accessed). Tang et al., PRX Quantum2,020310 (2021); Cea et al., arXiv:2402.11022; Beccaria et al., cond-mat/0702676; Bonet-Monroig et al., PRA98,062339 (2018); official TeNPy1.1.1, PennyLane0.44.1 and Mitiq ZNE sources were accessed in Stage4 and retained as historical references. New derivations and numerical conclusions are labeled as ours, not attributed to those sources.
