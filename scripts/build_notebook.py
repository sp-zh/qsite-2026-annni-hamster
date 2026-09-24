from pathlib import Path
import nbformat as nb
R=Path(__file__).resolve().parents[1];cells=[]
def md(s):cells.append(nb.v4.new_markdown_cell(s.replace(chr(92)*2,chr(92))))
def code(s):cells.append(nb.v4.new_code_cell(s))
md(r'''# Noise-Aware ANNNI Phase Diagnostics
## Low-CNOT preparation, error mitigation, and their limits
Team hamster: Shupei Zhang, Yangxin Zhou, Michael Li, Kathy Chen. Q-SITE 2026, Scientific Track.

This self-contained submission compares observable errors, resource costs and finite-size phase features. Low-CNOT preparation and cost-controlled mitigation improve observable reconstruction, while phase-feature reconstruction remains limited.

The notebook distinguishes three kinds of work. `archived_results` contains the frozen scientific experiments. `recomputed_from_saved_data` rebuilds their figures and statistics, and `fresh_light_validation` reruns one explicit circuit and saved-count reconstruction. Run All excludes grid optimization and DMRG.

Each cohort has its own denominator: the main maps contain 420 points, the confirmation cohort has 96 coordinates, its low-field subset has 48, the resource comparison has 45, and the windows contain 102. The 45 and 102 sets overlap, giving a union of 110 coordinates instead of 147.''')
code('''from pathlib import Path
import sys, json, numpy as np
ROOT = Path.cwd().resolve()
assert (ROOT / "scripts/release.py").is_file(), "Run with the submission root as working directory"
sys.path.insert(0, str(ROOT / "scripts"))
import release
from IPython.display import display, Image, Markdown
OUT = ROOT / "build/notebook"
OUT.mkdir(parents=True, exist_ok=True)
print(release.env())
print("Inputs: repository-relative files")
''')
md(r'''## Model, observables and noise
$$H=-\sum_iZ_iZ_{i+1}+\kappa\sum_iZ_iZ_{i+2}-h\sum_iX_i.$$
Small circuits use N=8 or 12 with PBC and wire 0 as the most-significant bit. Large MPS calculations use OBC, so their results are kept separate from N8 labels.
$$C(r)=N^{-1}\sum_i\langle Z_iZ_{i+r}\rangle,\quad M_x=N^{-1}\sum_i\langle X_i\rangle,\quad m_q^2=N^{-2}\sum_{ij}e^{iq(i-j)}\langle Z_iZ_j\rangle.$$
The observables include every discrete q and distance. Self correlations give the 1/N background; an ideal period-four antiphase has $m_{\pi/2}^2=1/2$. h=0 classical mixtures are separate from the positive-h pure-state protocol. Missing h=0 fidelities remain unfilled.

After each literal CNOT, only its target receives $D_p(\rho)=(1-p)\rho+\frac p3(X\rho X+Y\rho Y+Z\rho Z)$, p=0,.01,.05. Gate counts include reference preparation, decoding and folding. The circuits assume direct NN/NNN gates; literal tables record extra support and routing. The other track's 20-qubit hardware graph does not apply.

Source implementations: `annni/model.py`, `circuits.py`, `upgrade_gates.py`, `upgrade_adapt.py`, `stage6_candidates.py`, `upgrade_mitigation.py`. PennyLane 0.44.1 supplies the original HVA and an independent density crosscheck. The explicit NumPy backend executes the same archived gates for repeated simulations.''')
md(r'''## Preparation and independent reference
B0 is a six-layer Hamiltonian variational circuit (192 CNOT). Each layer applies NN ZZ rotations, NNN ZZ rotations, then RX: angle 2 theta means exp(-i theta P). B3 grows Pauli rotations from multiple references, optimizing energy, then selecting by the frozen energy/resource rule. Circuit preparation does not use ED StatePrep. The literal gate table and selected parameters for every B3 map point are bundled in `data/core/b3_map_circuits.json`.

A state passes only when delta e <= .001 per spin, max C/SF/Mx errors <= .02, and squared ED fidelity >= .99. Optimizer success, observable pass and state pass are separate.

R0 denotes supported region interiors. RN denotes same-size ED features, which can disagree with other diagnostics. Rlarge denotes larger-system evidence qualified by boundaries and size. Frozen D3 uses PCA and clustered reference resemblance, including a degraded-state control. We use it throughout as the established baseline; it was not selected using confirmation results. Applying D3 to ED produces an ideal diagnostic output whose labels still require independent physical validation.''')
code('''stats = release.statistics(OUT)  # recomputed_from_saved_data
print(json.dumps(stats["b0_b3"], indent=2))
from release_figures import draw
figure_receipt = draw(OUT, stats)  # all charts rebuilt from numeric files
print(figure_receipt)
display(Image(filename=str(OUT / "resource_tradeoff.png")))''')
md('''## Three noise maps
Exact-expectation raw B3 maps use the same grid and frozen D3. Crosses mark failed ideal preparations while preserving the detector output. Colors encode the frozen D3 pattern-resemblance classes. Unassigned and degraded outputs have separate classes. Branch sensitivity is audited for the six windows; these audits do not establish branch safety for the main grid.

The panels compare the ED reference with ideal and noisy circuits. The independent reference coverage has its own panel.''')
code('''display(Image(filename=str(OUT / "phase_comparison.png")))
display(Image(filename=str(OUT / "reference_scope.png")))''')
md('''### Finite-measurement and mitigation maps
These maps use one archived repeat with 100,000 total shots per point and p. Quadratic ZNE divides that total among folds 1/3/5 and X/Z settings. They match shot counts, while the 45-coordinate comparison below matches CNOT-shots. That smaller cohort is not extrapolated to the full 420-point grid.''')
code('''display(Image(filename=str(OUT / "phase_single_raw.png")))
display(Image(filename=str(OUT / "phase_single_zne_quadratic.png")))''')
md(r'''## Equal-resource mitigation
Quadratic ZNE combines scales 1/3/5 with weights (15/8,-5/4,3/8); linear ZNE is an archived baseline evaluated separately. Symmetry verification estimates $(\langle O\rangle+\langle OP\rangle)/(1+\langle P\rangle)$, $P=\prod_iX_i$, preserving the YY sign and covariance from shared bitstrings. SV verifies global-X symmetry without projecting momentum.

The main budget is G=100,000 times the point's original CNOT count. Raw and SV use 100,000 shots; quadratic ZNE uses 33,334, split 11,112/11,111/11,111. Integer G matches exactly. The higher budget uses actual G=299,998 times CNOT, including the two-CNOT-shot shortfall. Measurement settings and single-qubit gates are recorded separately and fall outside G.

The error metric averages 17 squared component errors: eight C, eight Fourier-related SF, and Mx. It retains the original equal component weights, including the C/SF redundancy, without adjustments based on the results. A mean across 32 repeats differs from a single 100k experiment. Errors against ED and against each circuit's own p0 target are reported separately.''')
code('''print(json.dumps([r for r in stats["equal_resource"] if r["mode"]=="equal_gate" and r["budget"]==100000], indent=2))
display(Image(filename=str(OUT / "equal_resource.png")))
display(Image(filename=str(OUT / "bias_sampling.png")))''')
md('''ZNE improves coordinate-mean MSE for all 45 coordinates at p=.01 and .05, but worsens all 45 at p=0. Individual random repeats do not all improve. These MSE results measure observable reconstruction; only six resource-cohort coordinates have independent interior labels. ZNE reduces bias while increasing sampling error.''')
md('''## Local response features and their limits
All six 17-point windows (kappa=0,.3,.45,.5,.55,.8) are retained. Five references are resolvable under the frozen rule; kappa=.5 fails the frozen peak-selection criterion. Matching uses the same feature across methods and includes endpoint and multi-peak failures, alongside preparation and branch audits. Window-equivalent counts average matches over 32 repetitions; they do not count established phase transitions.

The kappa=.8 example was specified before the followup and records a feature-reconstruction failure. Exact expectations isolate preparation/noise effects. The data include full sampled curves and empirical quantiles. These quantiles describe the samples without providing thermodynamic confidence intervals.''')
code('''display(Image(filename=str(OUT / "window_coverage.png")))
display(Image(filename=str(OUT / "six_windows.png")))
display(Image(filename=str(OUT / "window_example.png")))''')
md('''## Extensions and results
1. N>=12: difficult-region transfer was executed, with H6 performing below B3 on this cohort.
2. Multiple detectors: the package preserves frozen D1/D3 and newer D4/D5. Performance depends on the cohort; the results establish no universal improvement. D2 requires full-state access beyond the local-shot budget.
3. Mitigation: raw/linear/quadratic ZNE/SV implementations and equal-resource raw/quadratic/SV tests are available. At p=.05, raw B3 D3 assigns 384/420 main-grid points to the degraded class.
4. Dynamics: archived product-state quench/Trotter comparisons measure discretization and noise effects separately. The release adds no new quench runs.
5. Floating search: the controlled kappa=.8 OBC slice establishes antiphase/PM-side controls. h=.4/.425 belong to the screened subset. The final evidence contains zero supported floating samples and zero established transition brackets. The chi=512 run at .35 ended at its resource limit and provides no basis for excluding a phase.

H6 combines physical and domain-wall candidates within a frozen region; it is distinct from the six-layer HVA. N8 low-field candidate availability improves at greater gate/search cost; N12 selected passes are 23/36 for B3 and 17/36 for H6.''')
code('''print(json.dumps(stats["extensions"], indent=2))
display(Image(filename=str(OUT / "extensions.png")))
display(Image(filename=str(OUT / "dynamics.png")))
display(Image(filename=str(OUT / "floating_evidence.png")))
display(Image(filename=str(OUT / "floating_fit_sensitivity.png")))''')
md('''## Fresh lightweight validation
This cell compiles saved B3 parameters into gates and checks the saved state. It evolves p=0 and p=.01 with a target-only channel, then checks energy/SF identities and measurement probabilities. The prepared circuit input contains no ED state. `--sdk` separately runs PennyLane in the scientific environment.''')
code('''fresh = release.physics(OUT, sdk=False)
print(json.dumps(fresh, indent=2))
# One shared coordinate and equal-G budget for all estimators, all 32 repeats.
example_point = next(r["point_id"] for _, r in release.records() if r["method"]=="raw" and r["p"]==.01 and r["mode"]=="equal_gate" and r["budget"]==100000)
for method in ["raw", "zne_quadratic", "sv"]:
    record = next(r for _, r in release.records() if r["method"]==method and r["p"]==.01 and r["mode"]=="equal_gate" and r["budget"]==100000 and r["point_id"]==example_point)
    with np.load(release.path(record["archive"])) as arrays:
        rebuilt = release.samples_from_counts(record, arrays)
        np.testing.assert_allclose(rebuilt, arrays["samples"], atol=2e-12, rtol=2e-12)
    print(method, "reconstructed saved estimates:", rebuilt.shape, "G=", record["CNOT_shots_per_repeat"])''')
md('''### Portable deterministic data checks (V1)
The separate deep V1 command verifies the manifest, all active joint-count estimates, integer resource equality, coordinates, gate tables and denominators. Default Run All runs the representative checks above. The full count audit is separate, and historical RNG streams are not resampled. Optional V3 requires a matching environment; skipped replay is recorded separately from a pass.''')
code('''print("Representative count and physical checks completed above.")
print("Deep V1: python scripts/release.py verify-data")''')
md('''## Reproduction and conclusion
From this directory: `python scripts/release.py redraw --out build/redraw`, `python scripts/release.py verify-data`, `python scripts/release.py verify-physics --quick --sdk`, and optional `python scripts/release.py verify-exact-replay`.

To start a separate research run outside this notebook: `python scripts/recompute.py --compute --kappa 0.3 --h 0.5 --out build/research`. It invokes the original bounded B3 implementation and writes new data separately. The full historical orchestration in `research_scripts/` retains its original provenance and expired run guards. Use the commands above for the default reproduction workflow.

The experiments show how preparation quality, resource use and observable errors interact, including mitigation at equal CNOT-shots. Improved observable MSE alone does not establish phase boundaries. The results include failed low-field preparations, branch changes, detector rejections and finite-size effects.

References: [Q-SITE task](https://github.com/benmcdonough20/QSITE-2026-QuantumCoalition), [qubit ADAPT](https://arxiv.org/abs/1911.10205), [ANNNI tensor-network study](https://arxiv.org/abs/2402.11022), [floating-phase DMRG](https://arxiv.org/abs/cond-mat/0702676), [symmetry verification](https://arxiv.org/abs/1807.10050). Published XX/Z conventions map to this ZZ/X convention by local Hadamards; OBC/PBC and finite-size evidence remain distinct. See `docs/KNOWN_LIMITATIONS.md`, `provenance/SOURCE_MAP.csv` and the immutable manifests.''')
n=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}});nb.validate(n);nb.write(n,R/'submission.ipynb')
