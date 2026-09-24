# Artifact exports

Scientific regeneration is `bash scripts/reproduce_stage5.sh --report-only` in the locked scientific environment. It creates the figures, technical report and executed notebook from actual saved experiments.

PDF export is separate from scientific execution. The delivered run uses the bundled artifact runtime with versions in `export_environment.json`. To recreate that small tool environment without changing `.venv`:

```sh
uv venv --python 3.12 .venv-report
uv pip install --python .venv-report/bin/python -r results/stage5_v1/submission/report_requirements.lock.txt
.venv-report/bin/python scripts/render_stage5_pdf.py
```

The editable presentation is generated with OfficeCLI1.0.143 and Pillow:

```sh
officecli --version
.venv-report/bin/python scripts/build_stage5_slides.py
```

The deck builder refuses to overwrite an existing presentation. Preserve or move an existing export explicitly before rebuilding. Titles, subtitles and notes are native editable elements; scientific figures are embedded images with the plotting source and all numerical data supplied separately. OfficeCLI installation is an optional external tooling step, not a scientific dependency or a paid/cloud service used by this study.

Per-page PDF inspection and actual slide-render limitations are recorded in the export QA files. Rendering is not implied by successful XML validation.

For a clean presentation-tool setup, obtain OfficeCLI1.0.143 from the official releases page (https://github.com/iOfficeAI/OfficeCLI/releases); verify the version before building. The scientific verify/report-only entry points do not require OfficeCLI.
