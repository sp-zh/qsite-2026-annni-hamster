# Reproduce the final submission

The scientific environment uses Python 3.14.5 and environments/requirements.lock.txt. Run the following commands from the repository root:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r environments/requirements.lock.txt
.venv/bin/python -m pip install nbconvert==7.16.6
.venv/bin/python scripts/execute_notebook.py
.venv/bin/python scripts/release.py verify-data
.venv/bin/python scripts/release.py verify-physics --quick --sdk
.venv/bin/python scripts/release.py verify-exact-replay
.venv/bin/python scripts/release.py redraw --out build/redraw
```

The Python 3.12 portable environment uses environments/portable-python312.lock.txt. It executes saved-data reconstruction, NumPy circuit checks, plots and Notebook/HTML export. Use its interpreter path for each command; omit the SDK flag. V3 returns SKIPPED_ENV_MISMATCH in this environment.

V1 verifies saved counts across all 32 repeats per active record, integer resource equality, coordinates, gate tables and the manifest. V2 replays one actual saved-parameter B3 circuit at p=0/.01; --sdk compares PennyLane default.mixed. V3 performs strict bitwise replay after matching the environment contract. Assertion failures exit nonzero.

Default commands read bundled files and write build/. Missing inputs and paths outside the package raise errors. package_manifest.json and SHA256SUMS.txt describe the same payload; build/, .git and the two checksum lists are excluded. Historical verification receipts retain their recorded execution scope and commit.

The bounded optimization entry executes a new B3 energy-only run:

```bash
.venv/bin/python scripts/recompute.py --compute --kappa 0.3 --h 0.5 --seed 11 --budget 128 --minutes 20 --out build/research
```

This opt-in command preserves source algorithms and frozen thresholds, uses a new run clock and writes separate output. Notebook Run All uses archived experiments, saved-data reconstruction and representative physical checks. Historical orchestration scripts in research_scripts/ retain their original run deadlines. MPS reproduction uses the separate TeNPy lock and trusted optional checkpoints.

Report generation uses scripts/build_documents.py with ReportLab4.4.9 and Pillow12.3.0. The existing deck layout is updated through OfficeCLI; the legacy full-deck builder uses python-pptx1.0.2. A PDF-capable office renderer exports presentation.pdf. Numerical Run All executes independently of document generation.

The main archive is self-contained. Seventeen optional large assets are published in Release v1.0.0 and indexed by provenance/optional_assets.json. The original local multi-GB archives remain separate from the public package.
