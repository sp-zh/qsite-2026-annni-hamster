# Scientific evidence retention

This repository expands the standalone release and its scientifically relevant supplement, plus original baseline slices, earlier preparation/diagnostic results, and additional selection, transfer, reference and failure summaries. The local source archive is unchanged.

All six B3 response windows and the 45-coordinate equal-CNOT-shots evidence are ordinary repository data. Raw joint counts, active indices, RNG keys and gate/parameter identifiers are retained. The 648 excluded followup attempts are retained but excluded from final statistics.

`provenance/optional_assets.json` lists exact deep-evidence files at or above 100 MiB, their original paths and SHA256. They are supplied separately as GitHub Release assets when uploaded. Restore an asset to its listed path only for optional deep reproduction. The main notebook, V1 and V2 do not depend on these files. Key MPS pickle checkpoints should only be loaded from trusted provenance in the matching scientific environment.

Excluded local material: virtual environments, interpreter/font/editor caches, old packaging ZIPs, repeated pre-fix source snapshots, redundant expanded full-state intermediates and unselected large MPS tensor/optimizer-iteration objects. Final numerical observables, convergence/timeout records, important candidate checkpoints, and failure analyses remain. The repository does not claim every optimizer iteration or all tensor states are included.

Existing indexed scientific layouts remain intact, including some wide directories: rebucketing would invalidate original paths embedded in checkpoint/measurement records. `GITHUB_SIZE_AUDIT.csv` documents file decisions; original hashes and sanitized public hashes are distinguished in provenance. Sanitization changes only personal paths/administrative identifiers in derived public logs, never numeric arrays, circuit parameters, counts, thresholds or labels.

Download optional `.gz` assets from the repository Release into a directory, then run `python scripts/restore_optional_assets.py --download-dir PATH`. This validates compressed and decompressed SHA256, restores original relative paths, and never loads a pickle or runs a scientific experiment.
