"""Readable audit report, plots and bounded decision; reads completed runs."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import csv,json,sys
sys.path.insert(0,str(ROOT))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
OUT=ROOT/'results/calibration_v1'
def read():
    rows=[json.loads(p.read_text()) for p in sorted((OUT/'runs').glob('*.json'))]
    summary=json.loads((OUT/'summary.json').read_text())
    selected=json.loads((OUT/'selected.json').read_text())
    cfg=json.loads((ROOT/'configs/calibration_v1.json').read_text())
    return rows,summary,selected,cfg
def representative(rows,summary,selected,i):
    if str(i) in selected: return selected[str(i)]
    return next(s for s in summary if s['point']==i and s['layers']==8)
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=175,bbox_inches='tight')
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)
def make_figures():
    rows,summary,selected,cfg=read()
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    colors={0:'#2864aa',.3:'#bb7920',.8:'#8860a4'}
    fig,axs=plt.subplots(2,3,figsize=(13,7.5),layout='constrained')
    for ax,key,limit,label in zip(axs.flat,['delta_e','epsilon_c','epsilon_sf','epsilon_mx','infidelity'],
                                  [.001,.02,.02,.02,.01],
                                  ['Energy error per spin','Max C(r) error','Max m²(q) error','Mx error','1 - pure-state fidelity']):
        for r in rows:
            y=1-r['fidelity'] if key=='infidelity' else r[key]
            jitter={11:-.08,23:0,37:.08}[r['seed']]
            ax.scatter(r['layers']+jitter,max(y,1e-12),s=13,alpha=.6,
                       marker='o' if r['layers']<8 else '^',color=colors[r['kappa']])
        ax.axhline(limit,color='black',ls='--',lw=1)
        ax.set(yscale='log',xticks=[1,2,4,6,8],xlabel='Layers L',ylabel=label)
        ax.grid(axis='y',alpha=.2)
    ax=axs[1,2]
    for k,color in colors.items():ax.scatter([],[],color=color,label=f'κ={k}')
    layers=[1,2,4,6,8]
    fractions=[sum(r['joint_pass'] for r in rows if r['layers']==L)/sum(r['layers']==L for r in rows) for L in layers]
    ax.bar([str(L) for L in layers],fractions,color='#7293b3')
    for j,L in enumerate(layers):
        count=sum(r['layers']==L for r in rows)
        ax.text(j,fractions[j]+.02,f"n={count}",ha='center',fontsize=9)
    ax.set(ylabel='Joint pass fraction',xlabel='Layers L',ylim=(0,1.1))
    ax.legend(loc='upper left',fontsize=8)
    fig.suptitle('195 completed energy-only runs | fixed acceptance thresholds (dashed)')
    fig.supxlabel('L=1–6: same 15 points × 3 seeds. L=8: only five failed-stability points, warm continuation; not a matched cohort.',fontsize=9)
    save(fig,'accuracy_vs_depth')
    matrix=np.full((15,5),np.nan);seed_matrix=np.zeros((15,3))
    labels=[]
    for i,point in enumerate(cfg['points']):
        for j,L in enumerate(layers):
            g=[r for r in rows if r['point']==i and r['layers']==L]
            if g:matrix[i,j]=sum(r['joint_pass'] for r in g)
        chosen=representative(rows,summary,selected,i)
        labels.append(f"κ={point[0]}, h={point[1]}  (L={chosen['layers']})")
        for j,seed in enumerate(cfg['seeds']):
            seed_matrix[i,j]=next(r['joint_pass'] for r in rows if r['point']==i and r['layers']==chosen['layers'] and r['seed']==seed)
    fig,axs=plt.subplots(1,2,figsize=(12,8),layout='constrained')
    cmap=plt.get_cmap('Blues').copy();cmap.set_bad('#e6e6e6')
    axs[0].imshow(matrix,vmin=0,vmax=3,cmap=cmap,aspect='auto')
    for i in range(15):
        for j in range(5):
            axs[0].text(j,i,'—' if np.isnan(matrix[i,j]) else f'{int(matrix[i,j])}/3',ha='center',va='center',
                        color='white' if matrix[i,j]>=2 else 'black')
    axs[0].set(xticks=range(5),xticklabels=layers,yticks=range(15),
               yticklabels=[f"κ={k}, h={h}" for k,h in cfg['points']],xlabel='Layers L',title='Joint passes / three runs; grey = not run')
    axs[1].imshow(seed_matrix,vmin=0,vmax=1,cmap=ListedColormap(['#f4ddba','#3979af']),aspect='auto')
    for i in range(15):
        for j in range(3):
            axs[1].text(j,i,'PASS' if seed_matrix[i,j] else 'FAIL',ha='center',va='center',
                        color='white' if seed_matrix[i,j] else 'black',fontsize=8)
    axs[1].set(xticks=range(3),xticklabels=cfg['seeds'],yticks=range(15),yticklabels=labels,
               xlabel='Seed',title='Smallest stable candidate; unstable point uses L=8')
    save(fig,'seed_stability')
    fig,axs=plt.subplots(3,5,figsize=(15,8),layout='constrained')
    for i,ax in enumerate(axs.flat):
        chosen=representative(rows,summary,selected,i)
        d=np.load(OUT/'runs'/f"{chosen['best_run']}.npz")
        ax.plot(np.arange(8)/4,d['ed_structure_factor'],'k--',label='ED',lw=1.2)
        ax.plot(np.arange(8)/4,d['structure_factor'],'o-',color='#2864aa',label='Energy-best VQE',ms=3)
        ax.set(title=f"κ={chosen['kappa']}, h={chosen['h']}, L={chosen['layers']}\n{chosen['joint_pass_count']}/3 pass",
               ylim=(-.02,1.02),xlabel='q / π',ylabel='m²(q)')
        if str(i) not in selected:ax.set_title(ax.get_title()+' (unstable)',color='#9c5b00')
    axs[0,0].legend(fontsize=7)
    fig.suptitle('Full structure factor | all 15 points | common scale and retained 1/N self terms')
    save(fig,'structure_factor_comparison')
    fig,ax=plt.subplots(figsize=(8,6),layout='constrained')
    for i,(k,h) in enumerate(cfg['points']):
        chosen=representative(rows,summary,selected,i);stable=str(i) in selected
        ax.scatter(k,h,s=100,marker='o' if stable else 'X',color='#2864aa' if stable else '#bd7920')
        ax.annotate(f"L{chosen['layers']} · {chosen['joint_pass_count']}/3",(k,h),xytext=(10,0),textcoords='offset points',fontsize=9,va='center')
    ax.set(xlim=(-.08,1.1),ylim=(0,2),xlabel='κ',ylabel='h',
           title='Representative-point acceptance | blue: stable, orange X: unstable')
    ax.grid(alpha=.2);save(fig,'accepted_points')

def make_report():
    rows,summary,selected,cfg=read()
    meta=json.loads((OUT/'metadata.json').read_text())
    noise=list(csv.DictReader((ROOT/'results/noise_smoke_v1/observations.csv').open()))
    noise_meta=json.loads((ROOT/'results/noise_smoke_v1/metadata.json').read_text())
    diag_meta=json.loads((ROOT/'results/diagnostics_v1/metadata.json').read_text())
    inv=[json.loads(line) for line in (OUT/'invocations.jsonl').read_text().splitlines()]
    table='| κ | h | L1 | L2 | L4 | L6 | L8 rescue | candidate L | best δe | best F | optimizer success / 3 |\n|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for i,(k,h) in enumerate(cfg['points']):
        counts=[]
        for L in [1,2,4,6,8]:
            g=[s for s in summary if s['point']==i and s['layers']==L]
            counts.append(f"{g[0]['joint_pass_count']}/3" if g else '—')
        c=representative(rows,summary,selected,i)
        label=str(c['layers']) if str(i) in selected else f"{c['layers']} unstable"
        table+=f"|{k}|{h}|"+'|'.join(counts)+f"|{label}|{c['energy_best_delta_e']:.3g}|{c['energy_best_fidelity']:.8f}|{c['optimization_success_count']}/3|\n"
    failedtable='| run | δe | εC | εSF | εMx | F | optimizer status |\n|---|---:|---:|---:|---:|---:|---|\n'
    for r in rows:
        if r['point']==6 and r['layers'] in [6,8]:
            failedtable+=f"|{r['run_id']}|{r['delta_e']:.4g}|{r['epsilon_c']:.4g}|{r['epsilon_sf']:.4g}|{r['epsilon_mx']:.4g}|{r['fidelity']:.6f}|{r['message']}|\n"
    ntable='| κ | h | L | CNOT | F_ED(p=0) | F_ED(.01) | F_ED(.05) | purity(.05) |\n|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for i in [0,4,9,11,14]:
        g=[r for r in noise if int(r['point'])==i]
        ntable+=f"|{g[0]['kappa']}|{g[0]['h']}|{g[0]['layers']}|{g[0]['cnots']}|"+'|'.join(f"{float(r['ed_fidelity']):.6f}" for r in g)+f"|{float(g[-1]['purity']):.6f}|\n"
    report=f"""# Stage 2 — executed calibration, diagnostics and gate-noise tests

**Decision: NO-GO for an unrestricted 21×21 noisy scan with the current protocol.**
Useful calibrated states are retained: 14/15 points have a depth with at least two of three trajectories passing all engineering thresholds. Bounded, individually gated follow-up slices can proceed. No complete noisy grid was run.

## What actually ran

- Existing tests rerun before implementation: 13 passed. Full suite after additions: {(OUT/'all_tests.txt').read_text().strip().splitlines()[-1]}.
- Main calibration: 15 points × 4 depths × 3 seeds = 180 runs.
- Prespecified fallback: five failed-stability points × 3 seeds at L=8 = 15 additional runs. Total 195; none discarded.
- All-wavevector diagnostics consumed existing ED files only; no complete ED scan was rerun.
- Five calibrated points × p=0, .01, .05: all 15 density-matrix simulations ran.
- All upstream and baseline files were hash-verified unchanged. Python 3.14.5 / PennyLane 0.44.1, all installed lockfile versions matched; no dependency changes.
- Final artifact verification independently checked 195 saved runs, all selected states against PennyLane, and all 15 density archives.

## Circuit and optimization

Initial state is H on all eight wires. Each layer executes, in order:
NN edges (i,(i+1) mod 8), then NNN edges (i,(i+2) mod 8), then every wire's RX.
Each edge list is traversed i=0..7.
IsingZZ(2γ)=exp(-iγ ZiZj), IsingZZ(2η)=exp(-iη ZiZj), RX(2β)=exp(-iβ Xi).
Each layer is U_X(β) U_NNN(η) U_NN(γ) acting on the previous state; later gates multiply on the left.
There are 3L independent parameters, not shared between layers.

The simulator fuses each commuting family only to accelerate exact pure-state evolution. Its analytic adjoint gradient was checked against PennyLane backprop and central differences.
No ED StatePrep, ED fidelity objective, or output projection is used for main optimization.
ED values are loaded only after energy optimization to score the result.
Wire 0 is the most significant bit; basis and asymmetric-state checks establish the mapping.

L-BFGS-B minimizes total energy with maxiter=400, maxfun=20000, ftol=1e-12, gtol=1e-8, maxls=30.
Independent nonzero initialization uses uniform[-.5,.5], SeedSequence([seed,point_index,L]), seeds 11/23/37.
Every run saves initial/final parameters, full state/C(r)/m²(q), Mx, energy/gradient trace, iteration/evaluation counts, status, time, and resource counts.
Selection within each point/depth uses lowest energy, never post-hoc fidelity.
Fallback was triggered at the recorded UTC time in fallback_decision.json, using each seed's own L6 trajectory plus two independently sampled small layers.
This is warm continuation, not three fresh independent L8 restarts, and not three copies of the best L6 seed. No thresholds or budgets were changed.

## Acceptance and all 15 points

observable_pass requires δe≤.001, εC≤.02, εSF≤.02, εMx≤.02. state_pass requires F≥.99.
joint_pass is their conjunction; optimizer success is recorded separately and is not a substitute for either.
A candidate needs at least 2/3 joint passes, with its minimum-energy run passing too.
Three seeds provide an operational repeatability check, not a confidence bound on success probability.

{table}

The table reports joint passes, not optimizer convergence. Best δe/F are from the **same minimum-energy run** at the candidate depth.
Every depth's min/median/max metrics and counts are in summary.csv; every individual run is in all_runs.csv and runs/*.npz.
Across all 195 runs: {sum(r['observable_pass'] for r in rows)} observable passes, {sum(r['state_pass'] for r in rows)} state passes,
{sum(r['joint_pass'] for r in rows)} joint passes and {sum(r['optimization_success'] for r in rows)} optimizer-success exits.
{sum(not r['optimization_success'] for r in rows)} runs stopped at the bounded iteration budget.
Negative δe was not clipped; values below −1e-9 would raise a consistency failure. Observed minimum δe={min(r['delta_e'] for r in rows):.3e}.

### Unresolved point and failure interpretation

(κ,h)=(.3,.4) is still 1/3 joint pass at both L6 and L8:

{failedtable}

At L8 seed 11, energy and F pass but C(r) and m²(q) fail. Seed 37 remains in a substantially worse state.
Seed 23 achieves excellent observables and F but reaches the iteration limit.
This supports sensitivity to initialization/local minima and limited optimization budget; it does not prove ansatz expressibility is impossible.
No enlarged low-energy subspace or relaxed fidelity threshold was used.
All other failed shallow-depth groups remain in the table; the passing seed in a failed group does not make that group stable.

### Candidate and resources

No single tested uniform depth is established across all 15 points.
The smallest stable candidates are L2 (one point), L4 (four), L6 (five), and L8 continuation (four).
L8 was only tested on the prespecified five failures, so its performance cannot be extrapolated to all points.

Compilation is literal CNOT(control,target)–RZ(2a,target)–CNOT(control,target) for every ZZ.
Connectivity allows the specified NN/NNN logical edges directly; no unrelated 20-qubit routing graph or SWAP is introduced.
Resource counts retain zero/small rotations and do not cancel gates: CNOT=32L, parameter count=3L, compiled unitary gates=8+56L.
Scheduling respects per-wire source order; depths at L2/4/6/8 are 75/149/223/297.
Each qubit is a target 4L times. The full ordered directions and channel-inclusive depths are saved in resources_L*.json and noise schedules.json.
Different adaptive depths imply different noise exposure, a confound that must remain explicit in any future phase comparison.

## Frozen operational diagnostics v1

The main outputs are continuous features and finite-size response peaks, not four-phase labels.
All q=2πk/N are retained, with the 1/N self term and ideal antiphase peak .5.
Equivalent q and 2π−q amplitudes are averaged, not summed.
All near maxima within max(.005, .10×maximum) are retained.

Negative ordered-structure-factor derivatives and Mx derivatives use unsmoothed second-order finite differences on h>0.
Every local maximum and one-sided endpoint maximum is saved, together with supporting grid intervals.
Existing chiF uses squared overlaps at h_mid, and h=0 intervals remain NaN.
These intervals describe grid support, not statistical confidence or sub-grid precision.

The control comparison uses [m0²,2mπ/2²,Mx] and fixed analytic ferro, antiphase, plus, mixed prototypes.
Euclidean distance must be ≤.45, with a runner-up margin ≥.10, otherwise uncertain.
Completely mixed controls are degraded, not mislabeled high-field paramagnetic.
The thresholds are engineering choices frozen before noise, not fit to literature boundaries or noisy outputs.
Twelve controls across N8/12/16 passed.

At κ=.8 the first sampled non-π/2 mode exceeding π/2 is h=.65 for N12 and .50 for N16; not observed up to h=2 for N8.
N8's structure-factor/Mx/chiF peak positions are .600/.500/.525, preserving diagnostic disagreement.
All 28 local peaks, including a weak N16 h=1.55 feature, are retained.
These are finite-size mode competition and response features, not sufficient evidence for floating phase; N16 is not used to label N8.

## Actual per-gate noise

Same ideal parameters and gate schedule at every p; no retraining, no shots, no terminal-noise substitution.
Each actual CNOT is immediately followed only on its target by PennyLane D_p(ρ)=(1−p)ρ+(p/3)(XρX+YρY+ZρZ).
Both CNOTs of every ZZ decomposition get a channel, including p=0 for a matched structure.
All p=0 pure/decomposed/density checks, channel count/target checks, and density trace/Hermiticity/PSD checks passed.

{ntable}

For mixed states F_ED means <ψ_ED|ρ|ψ_ED>, not a pure-state inner product.
Each noise archive saves signed εprep=O_circuit(0)−O_ED and δnoise=O_circuit(p)−O_circuit(0) separately.
At p=.05 all five frozen prototype outputs are degraded. L6 and L8 purities are close to 1/256≈.00390625.
The shorter antiphase circuit retaining more signal than the deeper ferro circuit does **not** establish intrinsic antiphase robustness.
At p=.01 the L8 representative already has ED overlap ≈.110, so depth is a substantive limitation.
There is no quantitative phase-boundary-shift claim from these five points.

## Decision and concrete next configuration

NO-GO for a blind full noisy grid under this candidate/compilation protocol.
The blockers are (i) unresolved 2/3 stability at (.3,.4), (ii) no verified common depth, (iii) strong cumulative noise,
and (iv) diagnostics are a frozen operational v1, not a validated discrete phase classifier.

A next bounded task should use saved parameters, preserve v1, and create v2:
1. Resolve (.3,.4) with a predeclared small initialization/continuation comparison and fixed budget; do not silently extend v1.
2. Compare resource-efficient compilation or a single shorter circuit candidate at existing representatives before scaling noise.
3. For any exploratory slice, first validate p=0 at every point using the same thresholds; save failures as missing/uncertain.
4. Choose and freeze the compilation/depth policy, then use the same parameters and structure across p.
5. Freeze diagnostics v1 for the first comparison; any revised thresholds become a separately reported v2.

A ready-to-review proposed configuration is configs/next_stage_proposal.json; it is **not executed** in this round.

## Measured runtime and reproducibility

Total optimizer time across the 195 saved runs: {meta['total_optimizer_seconds']:.3f} seconds.
Calibration invocation wall times (pilot/main/fallback, including artifact work): {', '.join(f"{i['seconds']:.3f}" for i in inv)} seconds.
These are local fused-simulator timings, not quantum-hardware execution costs.
Actual 15-density-check sum: {noise_meta['density_simulation_seconds']:.3f} seconds; full smoke script {noise_meta['elapsed_seconds']:.3f} seconds.
A 441-point × 3-p noise run at these observed per-circuit costs would be roughly 11–44 minutes **as a linear estimate only**,
excluding retries, plotting, optimization, and changing cost/depth. It is not approved by the scientific readiness decision.

From project root:

    MPLCONFIGDIR=.mplconfig OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_calibration.py --pilot
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_calibration.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_calibration.py --fallback
    .venv/bin/python scripts/run_diagnostics.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_noise_smoke.py
    OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/verify_stage2.py
    .venv/bin/python scripts/report_calibration.py
    .venv/bin/python scripts/build_calibration_notebook.py

Calibration commands resume only with exact code/config/input fingerprints and matching per-run NPZ hashes.
Pilot runs were reused, not counted twice. For a fresh replicate use a separate project copy or a new versioned experiment; do not delete v1.
Notebook clearly separates stored historical experiment results from its fresh small check. Eight code cells executed without cell errors; five saved output figures were inspected. The restricted macOS environment emitted a psutil permission warning during kernel shutdown, after all cells completed; the raw log is retained in notebook_execution.log. No dependency changes were made to suppress it.
No complete noisy scan, larger-N VQE, hardware, paid service, QCNN, ZNE, or dynamics was run.

## Figures

![Accuracy and fixed thresholds](accuracy_vs_depth.png)

![Seed stability and unrun cells](seed_stability.png)

![All structure factors](structure_factor_comparison.png)

![Accepted representative points](accepted_points.png)
"""
    (OUT/'REPORT.md').write_text(report)
    decision=dict(decision="NO-GO for full noisy grid",stable_points=14,total_points=15,
        blockers=["(.3,.4) only 1/3 joint pass through L8","no common depth validated",
                  "p=.05 deep circuits almost mixed","operational diagnostics not strict phase classification"],
        usable="14 calibrated representatives, frozen diagnostics, literal noise pipeline",
        full_noisy_scan_executed=False)
    (OUT/'decision.json').write_text(json.dumps(decision,indent=2))
if __name__=='__main__':
    make_figures();make_report();print('Calibration report and four plot sets generated')
