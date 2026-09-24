# Speaker notes

Team hamster — Shupei Zhang, Yangxin Zhou, Michael Li, Kathy Chen

Estimated timing, not an actual rehearsal: 370 seconds (6 min 10 sec).

## Slide 1: Noise-Aware ANNNI Phase Diagnostics (40 seconds)

We study how quantum state preparation and noise affect reconstruction of the ANNNI phase diagram. The central result is a tradeoff: fewer entangling gates improve noisy correlations, and mitigation helps under a genuinely matched gate-weighted measurement budget. But neither improvement alone certifies a phase boundary. We keep the failed preparations, detector rejections and unresolved floating-phase evidence in the submission. The notebook contains the full numerical evidence and a lightweight circuit check.

## Slide 2: Model and evidence layers (45 seconds)

The Hamiltonian has ferromagnetic nearest-neighbor coupling, competing next-nearest-neighbor coupling and a transverse field. We use periodic boundaries for the small circuits. Noise follows every literal CNOT, on its target only, with the same specified channel at all three noise strengths. Reference preparation and folding count as gates. Three evidence layers prevent a detector from grading itself: supported interiors, same-size exact-diagonalization features, and larger-system evidence. Our observables retain every distance and momentum, including the self-correlation background.

## Slide 3: Fewer gates, different tradeoffs (45 seconds)

B0 is the original fixed six-layer Hamiltonian variational ansatz. B3 starts from several physical references and grows energy-optimized Pauli rotations, then uses a frozen energy and resource rule. The median CNOT count is halved, from 192 to 96. Ideal joint preparation coverage drops from 407 to 385 out of 420, so the method does not win on every metric. At noise probability one percent, mean maximum correlation error falls from 0.2638 to 0.1432, with improvement at 402 coordinates. This is an observable result, not phase-label accuracy.

## Slide 4: Three noise levels, one diagnostic (45 seconds)

These are the required three noise maps, alongside the same detector applied to ED data. The method, grid and legend remain fixed across noise levels. The colors show resemblance to physical patterns, not independently validated truth at every coordinate. Crosses indicate failed ideal preparation without hiding the label. Our notebook separately displays single-repeat finite-shot maps and equal-shots mitigation maps. It also shows where independent region labels exist. We never extend the smaller equal-resource cohort into a full equal-resource map.

## Slide 5: Mitigation at equal CNOT-shots (55 seconds)

Equal shot counts alone favor extrapolation with more noisy gates. We therefore match the sum of shots times literal CNOTs at each coordinate. Raw and symmetry verification use one hundred thousand shots, whereas quadratic ZNE uses thirty-three thousand three hundred and thirty-four shots shared across the three folds. The integer gate-weighted costs match exactly. At p=.01 and .05 the mean ED-target MSE falls by 90.75 and 25.19 percent. Each of the 45 coordinate means improves. ZNE worsens all 45 at zero noise. It reduces bias while increasing sampling error, and only six coordinates have independent phase-interior labels.

## Slide 6: Better observables, unstable features (50 seconds)

The prespecified kappa point eight window illustrates why a smaller component error need not stabilize a response feature. These curves use exact expectations so shot fluctuations cannot explain every failure. All six windows were actually executed. Five reference features are resolvable; the kappa point five reference is not. At strong noise, the equal-shots raw result matches roughly three of those five windows when averaged over measurement repeats, and extrapolation does not improve that aggregate. We retain endpoint and multiple-peak warnings, preparation failures and real same-coordinate branch comparisons. A match with no listed warning is still not proof of a thermodynamic transition.

## Slide 7: Extensions expose the limits (45 seconds)

The newer physical and domain-wall construction improves selected joint passes in the independent low-field confirmation subset, from 27 to 37 out of 48. However, median CNOTs increase from 32 to 127 and objective calls increase by about seven and a half times. H6 therefore is not an equal-cost universal winner. Its transfer to the N12 difficult/control set is weaker than B3. The five extension topics remain in the package: larger circuits, multiple detectors, mitigation, dynamics, and the floating-phase search. The negative transfer result is preserved rather than removed from the final story.

## Slide 8: What the evidence supports (45 seconds)

The controlled large-system slice supports an antiphase control at field point three and a paramagnetic-side control at point seven. Fields point four and point four two five remain candidates, but the size, entropy and Friedel evidence do not establish a supported floating interval or two independent transition brackets. A timed-out high-bond-dimension continuation is not evidence against a phase. Our conclusion is therefore specific: lower-gate preparation and resource-controlled mitigation improve observable reconstruction, while reliable boundary inference needs stronger evidence. The submission ships saved joint counts, gate tables, reproducible figures, and separate deterministic, physical and random-replay checks.