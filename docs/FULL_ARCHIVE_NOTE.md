# Scientific evidence retention

This repository contains the standalone release and its scientific supplement, along with original baseline slices, earlier preparation and diagnostic results, and summaries of selection, transfer, references and failures. The local source archive is unchanged.

All six B3 response windows and the 45-coordinate equal-CNOT-shots evidence are bundled in the repository. Raw joint counts, active indices, RNG keys and gate/parameter identifiers are retained. The 648 excluded followup attempts are retained but excluded from final statistics.

`provenance/optional_assets.json` lists exact deep-evidence files at or above 100 MiB, their original paths and SHA256. They are published as 17 assets in GitHub Release v1.0.0. Restore an asset to its listed path only for optional deep reproduction. The main notebook, V1 and V2 do not depend on these files. Key MPS pickle checkpoints should only be loaded from trusted provenance in the matching scientific environment.

The package excludes virtual environments, interpreter/font/editor caches, old packaging ZIPs, repeated pre-fix source snapshots, redundant expanded full-state intermediates and unselected large MPS tensor/optimizer-iteration objects. It retains final numerical observables, convergence and timeout records, selected candidate checkpoints and failure analyses.

Scientific directories keep their indexed layout, including directories with many files, because checkpoint and measurement records embed the original paths. `GITHUB_SIZE_AUDIT.csv` documents file decisions; original hashes and sanitized public hashes are distinguished in provenance. Sanitization replaces personal paths and administrative identifiers in derived public logs. Numeric arrays, circuit parameters, counts, thresholds and labels remain unchanged.

Download optional `.gz` assets from the repository Release into a directory, then run `python scripts/restore_optional_assets.py --download-dir PATH`. This validates compressed and decompressed SHA256, restores original relative paths, and never loads a pickle or runs a scientific experiment.

The public repository also retains all original end-to-end measurement/count and probability records from Stage 5 and Stage 6: 43,862 files beyond the original standalone closure, all byte-identical to their source archives. Their historical cohorts remain separate from the 2,718 active followup records. Data were transferred in bounded Git pushes; no new physical experiments were performed.
