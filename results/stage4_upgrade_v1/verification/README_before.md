# ANNNI Scientific Track — submission candidate

**Preparation-Protocol Dependence of Noisy ANNNI Phase Diagnostics**

The project has executed ED baselines, VQE calibration, matched depth/noise experiments, a 420-point positive-field grid, a corrected actual-branch audit, bounded repair and local nested-grid experiments. It is not an ED-only starter.

Start with [the executed submission notebook](submission/submission.ipynb), [the three-page English report](submission/report.pdf), and [the seven-slide presentation](submission/presentation.html). Author/team placeholders require completion; scientific claims and remaining deliverable gaps are explicit in the [requirements checklist](submission/requirements_checklist.csv).

Current results are generated from [statistics.json](submission/statistics.json) and linked to raw evidence in [evidence_table.csv](submission/evidence_table.csv): fixed L6 grid preparation coverage 411/420; 33 actual switching intervals audited; 78 repair attempts; 230 local preparations and 690 local noise configurations. These are selected deterministic simulations, not independent-start success rates or statistical confidence estimates.

No universal nonzero boundary displacement, floating phase or quantum advantage is claimed. Continuous diagnostics and quality masks retain preparation failures, unresolved features and protocol dependence.

## Reproduce

```sh
bash scripts/reproduce_submission.sh
```

The default validates archives, rebuilds the submission and executes lightweight ideal/noisy checks. Explicit `--compute` is required to resume the Stage4 experiment; its independent 90-minute session is not silently reset. See [environment and export instructions](submission/REPRODUCE.md). Numerical requirements remain in [requirements.lock.txt](requirements.lock.txt); PDF export uses a separate optional environment.

## Model and protocols

N=8 periodic ANNNI, H=-ΣZZ_NN+κΣZZ_NNN-hΣX. The main HVA uses L=6, 192 literal CNOTs; after each CNOT only its target receives the prescribed depolarizing channel with p=0,.01,.05. Full 256×256 density matrices, shots=None, no symmetry projection or gate cancellation. All p share frozen parameters at a point. h=0 is absent from the circuit grid.

All eight discrete structure factors are stored, including the self term. The control-resemblance classifier itself uses only three features: [m0²,2m(π/2)²,Mx]. Its labels are not proof of thermodynamic phases.

## Traceability and historical results

- [Stage4 execution report and limitations](results/stage4_v1/REPORT.md)
- [Stage4 decision fields](results/stage4_v1/decision.json)
- [Stage3 historical report](results/stage3_v1/REPORT.md)
- [VQE calibration](results/calibration_v1/REPORT.md)
- [ED baseline](results/baseline/REPORT.md)
- [Unmodified competition snapshot](upstream/Scientific%20Track/README.md) and [provenance](upstream/PROVENANCE.json)

Stage3 data, original configuration and logs remain unchanged. Corrected branch/support logic is versioned in new Stage4 modules. The previous README and source fingerprints are retained in results/stage4_v1/verification/source_before. Final manifests distinguish unchanged history, newly created files and modified entry/source artifacts. No remote publication is performed by the reproduction command.
