import sys,json,platform,hashlib,importlib.metadata,subprocess
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage4_upgrade_v1';S=O/'submission';plan=json.loads((O/'experiment_plan.json').read_text());stats=json.loads((S/'statistics.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2))
files=[p for base in ['annni','scripts','configs','tests'] for p in (R/base).glob('*') if p.is_file() and ('upgrade' in p.name or p.name in ['model.py','circuits.py','vqe.py','noise.py','diagnostics.py','stage3.py'])]
meta=dict(run_id=plan['run_id'],started=plan['started_utc'],deadline=plan['deadline'],finalized=datetime.now(timezone.utc).isoformat(),elapsed_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(plan['started_utc'])).total_seconds(),python=sys.version,platform=platform.platform(),versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','pennylane','matplotlib','nbformat','nbclient']},tensor_network_environment=dict(path='.venv-tn',lock='requirements-tn.lock.txt',python='3.12.14',tenpy='1.1.1',main_environment_unchanged=True),source_hashes={str(p.relative_to(R)):sha(p) for p in files},input_manifest='verification/protected_inputs.json',plan_sha256=sha(O/'experiment_plan.json'),freeze_sha256=sha(O/'freeze.json'),conventions=plan['conventions'],resource_budget=plan['resources'],resource_amendment=json.loads((O/'resource_amendment_v1.json').read_text()),orchestration_amendment=json.loads((O/'orchestration_amendment_v1.json').read_text()),workpackage_budgets=plan['budgets_fraction'],actual_cost=stats['cost'],noise_model=plan['conventions']['noise'],optimizer=dict(method='L-BFGS-B',maxiter_per_append=plan['maxiter'],ftol=plan['ftol'],gtol=plan['gtol'],selection=plan['selection'],seed_protocol=plan['seed_protocol']),cache='Every canonical physical key includes code fingerprint, complete explicit gate list, parameters, N/PBC, kappa/h, p and compile/fold flags. Noise kept-density and compact records have distinct keys. Artifact disposition marks first execution; cross-package aliases reuse these same hashed files without claiming another execution.',historical_reused=['baseline ED matching coordinates','Stage3 B0 selected parameters and prescribed-noise archives'],not_executed=json.loads((O/'decision.json').read_text())['not_executed'],amendments=['New independent output directory because prior stage4_v1 exists','Network proxy failed; direct primary-source retrieval succeeded for papers; some ReadTheDocs pages403, official source fallback','New isolated TeNPy environment; first uv cache path blocked, task-local cache succeeded','Small-N spatial fit empty-window error fixed before large-N runs','Uhlmann sandwich cutoff failed self-fidelity; stable trace-norm implementation before data diagnostics','Noise metadata Python/JSON tuple and NumPy-bool normalization fixed; prior failed logs retained; raw old-code records not silently relabeled'],test_report='verification/final_tests.log',numerical_audit='verification/result_audit.json',bonus_decision='decision.json',pdf_sha256=sha(S/'report.pdf') if (S/'report.pdf').exists() else None,notebook_sha256=sha(S/'submission.ipynb'),presentation_sha256=sha(S/'presentation.pptx') if (S/'presentation.pptx').exists() else None)
dump(O/'metadata.json',meta)
root='''# ANNNI Scientific Track — adaptive circuit research package

The latest campaign adds explicit multi-reference qubit-ADAPT preparation, a frozen held-out comparison, N=12 circuits and exact noise simulations, three diagnostic mechanisms, finite-shot ZNE/symmetry verification, OBC MPS evidence and second-order quench dynamics. Older Stage3 and diagnostic Stage4 outputs remain unchanged.

'''+f"Latest preparation coverage: **{stats['map']['B3']['passed']}/420** descriptive-grid points and **{stats['heldout']['B3']['passed']}/48** frozen held-out points; selected grid CNOT median **{stats['map']['B3']['median_cnots']:g}**, historical HVA192. These are preparation pass counts, not classification accuracy. N12: **{stats['n12']['B3']['passed']}/60** preparations, with36 representative noise configurations.\n\n"+'''- [Executed notebook](results/stage4_upgrade_v1/submission/submission.ipynb)
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
'''
(R/'README.md').write_text(root)
(S/'REPRODUCE.md').write_text('''# Reproduce this campaign

Run commands from the extracted project root. The science environment lock is requirements.lock.txt (Python3.14.5). TeNPy is independently locked in requirements-tn.lock.txt (Python3.12.14). Create separate environments, never install tensor-network packages over the old science environment.

```
uv venv --python 3.14 .venv
uv pip sync --python .venv/bin/python requirements.lock.txt
uv venv --python 3.12 .venv-tn
uv pip sync --python .venv-tn/bin/python requirements-tn.lock.txt
bash scripts/reproduce_upgrade.sh --verify
bash scripts/reproduce_upgrade.sh --report-only
bash scripts/reproduce_upgrade.sh --resume
```

`--verify` runs tests and loads saved parameters/observables. `--report-only` regenerates plots, numerical summaries and the executed notebook without redoing optimization. `--resume` checks experiment/cache fingerprints and continues incomplete packages within the original deadline; it does not silently start a new budget. Source changes require a new versioned campaign instead of relabeling historical results.

PDF export is independent: use a Python environment with reportlab4.4.9 and pypdf6.10.0 to run scripts/render_upgrade_pdf.py. Editable slides use officecli1.0.143 and Pillow, via scripts/build_upgrade_slides.py; existing slides are protected against implicit overwrite. Speaker notes and the narrative Markdown remain editable. Author/team information and a timed rehearsal are submission tasks for the human team; no personal identity is invented.

The ZIP contains actual numerical data, MPS checkpoints, source, locks and metadata, not virtual environments. SHA256 values are checked after fresh extraction. Downloaded full papers are excluded from redistribution; citation/access records and method notes remain. Historical cache artifacts are labeled as reused, with new experiment results kept in stage4_upgrade_v1.
''')
print('Metadata and root README finalized')
