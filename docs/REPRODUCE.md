# Reproduce from this directory

The original science lock is preserved in environments/requirements.lock.txt (Python3.14). Portable environment details and tested coverage are separately recorded in provenance/verification/. Do not treat portable checks as a full VQE/DMRG certification.

Install with an isolated matching Python: `python -m venv .venv` then `.venv/bin/python -m pip install -r environments/requirements.lock.txt`. Notebook HTML export additionally uses nbconvert7.16.6; use the tested portable lock when available. Do not install over a research environment.

Read: open submission.html / report.pdf. Run notebook from the submission directory.

```
python scripts/release.py verify-data
python scripts/release.py verify-physics --quick
python scripts/release.py verify-physics --quick --sdk
python scripts/release.py redraw --out build/redraw
python scripts/release.py verify-exact-replay
python scripts/execute_notebook.py
```

V1: deterministic saved counts, all32 repeats per active record, exact integer resource checks, coordinates/gates, manifest. V2: one actual saved-parameter B3 circuit at p0/.01; optional SDK default.mixed comparison. V3: strict environment-gated replay; mismatch is a skip, a matched-environment assertion failure exits nonzero. No catch-and-pass path exists.

Default commands read only bundled files and write build/. No outside historical archive is needed. Missing inputs fail explicitly. Runtime path resolution rejects escapes. package_manifest excludes generated build/ and itself. Verification receipts and ZIP hashes are external sidecars to avoid self-reference.

Opt-in original main algorithm:
```
python scripts/recompute.py --compute --kappa 0.3 --h 0.5 --seed 11 --budget 128 --minutes 20 --out build/research
```
This invokes original B3 energy-only adaptive growth with a new bounded run clock, preserving source algorithms and frozen thresholds. It is not executed in this release. Single-point runtime is variable; no new timing claim is made. Full original orchestration scripts are in research_scripts/ and scientific modules in annni/. Historical plans retain expired deadlines and should not be launched as a quick start. MPS needs the separate TeNPy lock and optional supplement; pickle checkpoints must only be loaded from trusted provenance.

Report/deck rebuild uses scripts/build_documents.py (ReportLab4.4.9,python-pptx1.0.2,Pillow12.3.0) and a PDF-capable office renderer; its output is not required for numerical Run All. Figures are losslessly redrawn from the same numerical files.

The main archive is self-contained. Deeper scientific evidence is expanded into results/. Optional large Release assets are indexed by provenance/optional_assets.json and are not dependencies of the main notebook. Original multi-GB stage archives remain local and are not repackaged.
