# Release changes

The release adds adapter scripts to export inputs, rebuild statistics and figures, generate the notebook, report and slides, and run V1/V2/V3 verification separately. This work introduces no scientific coordinates, candidate selections, detector fits, relaxed thresholds or large simulations. Historical source modules and lock files are copied verbatim. The explicit recompute command redirects future opt-in outputs to build/ and gives those runs a new deadline.

Formal followup statistics use the union of A_index and B_index: 2718 records across 110 distinct active coordinates. A contains 102 coordinates and B contains 45, with overlap. The archive preserves and accounts for the cost of 648 valid earlier attempts, which are excluded from formal pooling. Existing cache-key, tie-rule, gate-fingerprint and monotonic-index corrections are retained. Main-map and window circuits remain separate even at the same coordinate.

Figures use the frozen D3 baseline and the archived scientific definitions. The report, notebook and slides read release_statistics derived from numerical data. V1 reconstructs all saved repeated estimates. V2 recompiles and simulates a saved circuit, with a PennyLane crosscheck in the locked scientific environment. V3 replays one fixed record using its archived random identity. Verification receipts identify the environment used.

Historical reports record their original experiments and tests. Packaging these records does not create new experimental evidence. The repository is published on GitHub. The team confirms submitted: true and dashboard_status: draft; the dashboard entry is saved as Draft. See release_status.json.
