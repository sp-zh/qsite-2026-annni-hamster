# Experimental results and scope

The finite periodic N8 experiments compare preparation quality, resource use and observable errors. B3 reduces median CNOTs from 192 to 96 and reduces noisy correlation error, while ideal joint preparation passes decrease from 407/420 to 385/420. H6 increases N8 low-field selected passes from 27/48 to 37/48, with higher gate counts and search costs. On the N12 difficult/control cohort, B3 passes 23/36 and H6 passes 17/36.

At equal CNOT-shots, quadratic ZNE reduces mean ED-target MSE by 90.75% at p=.01 and 25.19% at p=.05 across 45 coordinates. Six coordinates have independent interior labels. The 17-component metric includes Fourier-related C and SF components. It measures observable reconstruction; phase-feature matching is evaluated separately. At p=.05, B3 raw D3 assigns 384/420 main-grid points to the degraded class.

All six B3 response windows are executed. Five ED references pass the frozen peak-selection criterion; the kappa=.5 reference fails that criterion and contributes no reference position. The records include endpoint effects, competing peaks, preparation results and branch comparisons. N8 circuits use PBC; large MPS chains use OBC.

The kappa=.8 OBC scan establishes an antiphase control at h=.3 and a PM-side control at h=.7. The screened floating subset contains the h=.4/.425 samples. The final evidence contains zero supported floating samples and zero established transition brackets, so it does not establish a continuous floating interval. Historical (.8,.5) and (1,.7) interpretations are superseded by this result; (.6,.2) belongs to the historical cohort. The h=.35 chi512 run ended at its resource limit.

# Reproduction contract

V1 reconstructs estimates from saved integer counts. V2 recompiles literal gates and checks states, probabilities and identities at absolute tolerance 2e-10, with a separate PennyLane crosscheck. V3 exactly replays one frozen record at repeats 0, 1 and 31 across all 30 SV settings. It requires the matching Python 3.14.5 / NumPy 2.5.3 / SciPy 1.18.1 environment.

V3 compares the Python build, NumPy, SciPy, platform, machine and PCG64 identity before replay. An incompatible environment returns SKIPPED_ENV_MISMATCH. This contract covers the stated record and environment. The archive preserves input, code and configuration hashes alongside the original RNG keys, counts and seeds. Replay uses the archived probabilities unchanged.

# Submission status

Team hamster: Shupei Zhang, Yangxin Zhou, Michael Li and Kathy Chen. The final deliverables contain all four names. Team-confirmed competition status: submitted: true; dashboard_status: draft. The authenticated dashboard governs finalization, file-size limits and presentation delivery.
