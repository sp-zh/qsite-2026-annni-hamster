# ANNNI Scientific Track — adaptive circuit research package

The latest campaign adds explicit multi-reference qubit-ADAPT preparation, a frozen held-out comparison, N=12 circuits and exact noise simulations, three diagnostic mechanisms, finite-shot ZNE/symmetry verification, OBC MPS evidence and second-order quench dynamics. Older Stage3 and diagnostic Stage4 outputs remain unchanged.

Latest preparation coverage: **385/420** descriptive-grid points and **42/48** frozen held-out points; selected grid CNOT median **96**, historical HVA192. These are preparation pass counts, not classification accuracy. N12: **40/60** preparations, with36 representative noise configurations.

- [Executed notebook](results/stage4_upgrade_v1/submission/submission.ipynb)
- [Three-page report](results/stage4_upgrade_v1/submission/report.pdf)
- [Editable presentation](results/stage4_upgrade_v1/submission/presentation.pptx)
- [Technical report and limitations](results/stage4_upgrade_v1/REPORT.md)
- [Five bonus statuses](results/stage4_upgrade_v1/BONUS_STATUS.md)
- [Frozen plan](results/stage4_upgrade_v1/experiment_plan.json) and [decision](results/stage4_upgrade_v1/decision.json)

```sh
bash scripts/reproduce_upgrade.sh --verify
bash scripts/reproduce_upgrade.sh --report-only
bash scripts/reproduce_upgrade.sh --resume
```

Use the existing scientific `.venv`; new TeNPy uses isolated `.venv-tn` and `requirements-tn.lock.txt`. Resume validates frozen keys and retains the original12-hour deadline. No cloud, hardware, push or environment-wide upgrade is used. Archive verification and explicit limitations are part of the package. The baseline Hamiltonian is periodic H=-NNZZ+kappa*NNNZZ-hX. Per-CNOT target depolarization includes every reference-preparation and folding gate. Full q structure factors retain self terms. h=0 is a separate ED mixed-state convention and absent from circuit maps.

Previous [Stage3 baseline](results/stage3_v1/REPORT.md), [Stage4 diagnostic repair](results/stage4_v1/REPORT.md), [calibration](results/calibration_v1/REPORT.md), and [upstream snapshot](upstream/Scientific%20Track/README.md) retain their provenance. The prior root README is saved in the latest verification directory. No universal thermodynamic phase-boundary shift or quantum advantage is claimed.
