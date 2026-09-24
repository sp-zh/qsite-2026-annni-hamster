# Data included in the submission

## Main submission

The main submission is self-contained and includes:

- All 420 B3 map coordinates, with numeric ED, circuit and noisy observables, quality checks, detector outputs, literal gate tables and selected parameters. Raw and equal-shots ZNE panels are separate.
- Matched B0 observations for the 420-point grid and the frozen selected parameter archives, alongside the original B3 noise archives and comparison rows. The maximum correlation error table is checked against ED using the archived observables.
- The active followup A/B union: 2718 original record/count files, all 32 repeats and covariances, associated probabilities and literal circuit inputs. Its 102 window coordinates and 45 resource coordinates overlap. Formal metrics use only the active indices.
- Numeric curves for all six windows, repeated samples, feature matches, audit flags and branch controls, including endpoints and windows whose references fail selection.
- Confirmation and N12 rows, reference tables, floating interval and fit records, complete small dynamics observable files, scientific implementations and original lock files.
- The notebook, report and slides, reproducible statistics, verification commands, and source and payload hashes.

The formal count and window evidence includes failed and negative cases.

## Deep evidence and optional Release assets

The deep evidence includes original map, low-field, confirmation and N12 measurement counts and probabilities; all 648 valid excluded followup attempts; candidate and selected-state checkpoints; and branch records. MPS observations and convergence records are accompanied by five selected MPS checkpoints.

The repository contains the deep Stage5/Stage6 count and probability records. Seventeen large assets are published in Release v1.0.0, with paths and hashes in provenance/optional_assets.json. Main Run All uses bundled inputs.

## Original local research archive

The original workspace holds the complete Stage5/Stage6 multi-GB archives, earlier intermediates, optimization traces, dense states, additional MPS checkpoints and historical generated artifacts. These files have not been repackaged. Historical source references identify their original locations. Runtime release adapters resolve only declared bundled inputs and raise an error when an input is missing; they do not fetch files from the old workspace.
