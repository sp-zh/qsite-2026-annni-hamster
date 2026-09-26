# Speaker notes

Team hamster: Shupei Zhang, Yangxin Zhou, Michael Li, Kathy Chen

Speaking plan: 370 seconds (6 min 10 sec).

## Slide 1: Noise-Aware ANNNI Phase Diagnostics (40 seconds)

We study how quantum state preparation and noise affect reconstruction of the ANNNI phase diagram. Fewer entangling gates improve noisy correlations, and error mitigation helps when we match the gate-weighted measurement budget. Establishing a phase boundary requires separate evidence. The submission includes failed preparations, detector rejections and the floating-scan results. The notebook contains the full numerical evidence and a lightweight circuit check.

## Slide 2: Model and evidence layers (45 seconds)

The Hamiltonian combines ferromagnetic nearest-neighbor coupling, competing next-nearest-neighbor coupling and a transverse field. Our small circuits use periodic boundaries. At each of the three noise strengths, the specified channel acts on the target after every literal CNOT, including reference preparation and folding. We distinguish supported interiors, same-size exact-diagonalization features and larger-system evidence so that detector output can be assessed against an independent reference. The observables include every distance and momentum, with the self-correlation background retained.

## Slide 3: Fewer gates, different tradeoffs (45 seconds)

B0 is the original fixed six-layer Hamiltonian variational ansatz. B3 starts from several physical references, grows energy-optimized Pauli rotations and selects a circuit using a frozen energy and resource rule. The median CNOT count falls from 192 to 96, while ideal joint preparation coverage drops from 407 to 385 out of 420. At one percent noise, mean maximum correlation error falls from 0.2638 to 0.1432, with improvement at 402 coordinates. These measurements do not establish phase-label accuracy.

## Slide 4: Three noise levels, one diagnostic (45 seconds)

The three required noise maps appear alongside ED data classified by the same detector. We keep the method, grid and legend fixed across noise levels. Colors show resemblance to physical patterns; independent labels are available only at the coordinates shown in the notebook's reference panel. Crosses mark failed ideal preparations while leaving detector labels visible. The notebook also separates single-repeat finite-shot maps from equal-shots mitigation maps. The smaller equal-resource cohort is evaluated separately, without extrapolating it to a full map.

## Slide 5: Mitigation at equal CNOT-shots (55 seconds)

At equal shot counts, extrapolation receives more noisy gates. To control this cost, we match the sum of shots times literal CNOTs at each coordinate. Raw and symmetry verification use one hundred thousand shots; quadratic ZNE uses thirty-three thousand three hundred and thirty-four across the three folds. Their integer gate-weighted costs match exactly. At p=.01 and .05, mean ED-target MSE falls by 90.75 and 25.19 percent. All 45 coordinate means improve at these noise levels, but all 45 worsen at zero noise. ZNE reduces bias while increasing sampling error. Only six coordinates have independent phase-interior labels.

## Slide 6: Better observables, unstable features (50 seconds)

The prespecified kappa point eight window shows why observable reconstruction and response-feature matching need separate evaluation. These curves use exact expectations, so shot fluctuations cannot explain every failure. All six windows were executed. Five reference features are resolvable; the kappa point five reference fails the frozen peak-selection criterion. At strong noise, equal-shots raw estimates match roughly three of the five windows on average across measurement repeats. Extrapolation does not improve that aggregate. The records include endpoint and multiple-peak warnings, preparation failures and same-coordinate branch comparisons. Even a match without a listed warning requires more evidence to establish a thermodynamic transition.

## Slide 7: Extensions expose the limits (45 seconds)

Combining physical and domain-wall candidates increases selected joint passes in the independent low-field confirmation subset from 27 to 37 out of 48. That improvement costs more: median CNOTs rise from 32 to 127, and objective calls increase by about seven and a half times. On the N12 difficult/control set, H6 performs below B3. The package includes results for all five extension topics: larger circuits, multiple detectors, mitigation, dynamics and the floating-phase search.

## Slide 8: What the evidence supports (45 seconds)

The controlled large-system slice supports an antiphase control at field point three and a paramagnetic-side control at point seven. At fields point four and point four two five, the size, entropy and Friedel diagnostics disagree. The final evidence contains zero supported floating samples and zero established transition brackets. The high-bond-dimension continuation reached its time limit, which gives no basis for excluding a phase. Lower-gate preparation and resource-controlled mitigation improve observable reconstruction in these experiments; reliable boundary inference needs stronger evidence. The submission includes saved joint counts, gate tables, reproducible figures and separate deterministic, physical and random-replay checks.