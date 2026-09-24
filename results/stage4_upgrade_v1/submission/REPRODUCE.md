# Reproduce this campaign

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
