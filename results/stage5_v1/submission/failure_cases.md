# Executed failure cases

All joint acceptance thresholds are unchanged. The following tables retain every failed new N8 test point and every failed192-cap N12 point; no new phase labels are assigned.

The near-degenerate31/32-CNOT explanation is in [the original candidate audit](../selection_audit/counterexample.json). Frozen S1/S2 actually select98 CNOTs there. The severe N12(.8,.7) symmetry-filter failure is discussed in technical_report.md.

## New N8 test:10 retained failures

| kappa | h | selected CNOT | energy error/site | max C error | max SF error | Mx error | F | attribution |
|---|---|---|---|---|---|---|---|---|
| 0.475423 | 0.125996 | 31 | 0.026545 | 1.51291 | 0.892247 | 0.376116 | 0.012919 | no_qualified_candidate_budget_reached |
| 0.602809 | 0.193923 | 128 | 0.000474789 | 0.0409106 | 0.0122346 | 0.0215234 | 0.985638 | no_qualified_candidate_budget_reached |
| 0.631177 | 0.35091 | 96 | 0.0102369 | 0.467749 | 0.131615 | 0.112171 | 0.821993 | no_qualified_candidate_budget_reached |
| 0.604778 | 0.409939 | 128 | 0.00180038 | 0.0592063 | 0.017965 | 0.0125103 | 0.992564 | no_qualified_candidate_budget_reached |
| 0.611818 | 0.255952 | 128 | 0.00282992 | 0.242435 | 0.0711517 | 0.0859737 | 0.922061 | no_qualified_candidate_budget_reached |
| 0.638666 | 0.487596 | 128 | 0.00174251 | 0.0168128 | 0.00604011 | 0.00939888 | 0.995911 | no_qualified_candidate_budget_reached |
| 0.578691 | 0.427605 | 128 | 0.00106936 | 0.0200957 | 0.00726509 | 0.00472375 | 0.996363 | no_qualified_candidate_budget_reached |
| 0.694815 | 0.42688 | 128 | 0.00188096 | 0.054597 | 0.0155548 | 0.0139909 | 0.988833 | no_qualified_candidate_budget_reached |
| 0.56013 | 0.216366 | 127 | 0.00220513 | 0.0413509 | 0.0143721 | 0.00856853 | 0.97532 | no_qualified_candidate_budget_reached |
| 0.578708 | 0.324332 | 128 | 0.0016506 | 0.0502014 | 0.0159236 | 0.00697764 | 0.989775 | no_qualified_candidate_budget_reached |

## N12 at192 cap:15 retained failures

| kappa | h | selected CNOT | energy error/site | max C error | max SF error | Mx error | F | attribution |
|---|---|---|---|---|---|---|---|---|
| 0.3 | 0.5 | 191 | 3.88437e-05 | 0.0224994 | 0.0121866 | 0.00247375 | 0.99951 | no_qualified_candidate_budget_reached |
| 0.8 | 0.5 | 192 | 0.00472669 | 0.273383 | 0.0840501 | 0.0942851 | 0.852533 | no_qualified_candidate_budget_reached |
| 0.8 | 0.6 | 160 | 0.0174658 | 0.535799 | 0.153802 | 0.0945406 | 0.698303 | no_qualified_candidate_budget_reached |
| 0.8 | 0.7 | 10 | 0.219775 | 1.06305 | 0.351932 | 0.732786 | 0.0672229 | no_qualified_candidate_budget_reached |
| 0.8 | 0.8 | 192 | 0.00269898 | 0.0211849 | 0.00779725 | 0.0109297 | 0.992126 | no_qualified_candidate_budget_reached |
| 0.8 | 0.9 | 192 | 0.00166287 | 0.0222698 | 0.00704651 | 0.00635159 | 0.995661 | no_qualified_candidate_budget_reached |
| 0.8 | 1.0 | 192 | 0.00132541 | 0.0178552 | 0.0056612 | 0.00489845 | 0.996975 | no_qualified_candidate_budget_reached |
| 0.8 | 1.1 | 192 | 0.00102899 | 0.0205496 | 0.00583868 | 0.00349552 | 0.997805 | no_qualified_candidate_budget_reached |
| 0.482429 | 0.584498 | 192 | 0.00103755 | 0.0424896 | 0.0122944 | 0.00515891 | 0.995254 | no_qualified_candidate_budget_reached |
| 0.530192 | 0.304778 | 10 | 0.138031 | 1.43052 | 0.443256 | 0.607131 | 0.000793956 | no_qualified_candidate_budget_reached |
| 0.482685 | 0.188679 | 64 | 0.0128762 | 0.526836 | 0.184464 | 0.0401861 | 0.524725 | no_qualified_candidate_budget_reached |
| 0.610248 | 0.212278 | 192 | 0.0107851 | 1.44434 | 0.423558 | 0.347549 | 0.0252394 | no_qualified_candidate_budget_reached |
| 0.373046 | 0.338199 | 192 | 0.000157905 | 0.0837613 | 0.0435411 | 0.0064785 | 0.994599 | no_qualified_candidate_budget_reached |
| 0.517734 | 0.201329 | 32 | 0.0693251 | 1.46048 | 0.434869 | 0.37522 | 0.000637442 | no_qualified_candidate_budget_reached |
| 0.633588 | 0.699861 | 192 | 0.00154423 | 0.0439937 | 0.0117502 | 0.00695202 | 0.99397 | no_qualified_candidate_budget_reached |

Budget exhaustion does not prove an expressivity limit or exclude better optimization at the same cap. Full precision and all descriptive/transition failures: [failures.csv](failures.csv). N12 source stops and candidate availability: [failure_details.json](../n12_scaling/failure_details.json).