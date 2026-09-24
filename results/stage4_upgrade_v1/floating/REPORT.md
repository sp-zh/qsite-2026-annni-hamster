# Large-OBC floating evidence

Disposition: newly_executed, except explicitly historical B0/ED inputs.

98 unique MPS solves including small-model validation;39 coarse-index and66 refine-index references overlap. N32/64/96;chi64/128/256;two center initializations. Three centers satisfy transparent post-computation evidence criteria, not exact continuous phase boundaries. See evidence_grading.json, convergence_comparison.json and small_periodic_bridge.json.

```json
{
  "status": "validated_evidence",
  "scope": "N32 coarse; N64/96, chi64/128/256, two initializations at centers",
  "evidence": [
    {
      "kappa": 0.6,
      "h": 0.1,
      "evidence_grade": "not_resolved",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": false,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": false,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 6.661338147750939e-16,
          "delta_correlation": 8.260059303211165e-14,
          "delta_entropy": 1.928313411725391e-12
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 1.1842378929335002e-15,
          "delta_correlation": 6.139533326177116e-14,
          "delta_entropy": 8.783518075199115e-13
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        0.0005613167544683362,
        0.0017035049681719291,
        -0.00044340271145717553,
        0.001179228789018675
      ],
      "q": [
        1.5685320683538035,
        1.569878510791022
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 0.6,
      "h": 0.2,
      "evidence_grade": "supported_in_tested_window",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": true,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": true
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 6.445288747158884e-12,
          "delta_correlation": 1.4822297167427223e-07,
          "delta_entropy": 1.084422842634325e-07
        },
        {
          "n": 96,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 8.245611600917376e-11,
          "delta_correlation": 8.737273024528314e-07,
          "delta_entropy": 2.3593617666239908e-06
        }
      ],
      "initialization_checks": [
        {
          "n": 64,
          "delta_energy_per_site": 1.4654943925052066e-14,
          "delta_correlation": 1.0856028923034167e-09,
          "delta_entropy": 7.841238991446176e-09
        },
        {
          "n": 96,
          "delta_energy_per_site": 7.179442225909346e-15,
          "delta_correlation": 4.675867815162604e-08,
          "delta_entropy": 6.501051452723061e-08
        }
      ],
      "entropy_c": [
        1.0485685812845493,
        0.9691000703553523,
        1.0234271747882588,
        1.0676462973718444
      ],
      "q": [
        1.2602984240033706,
        1.265228211045028
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 0.6,
      "h": 0.3,
      "evidence_grade": "candidate",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 2.3622832578951147e-09,
          "delta_correlation": 9.081774924146746e-06,
          "delta_entropy": 1.713568778116681e-05
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 1.288099153266368e-08,
          "delta_correlation": 3.900344600177297e-05,
          "delta_entropy": 0.0001614537986107667
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        0.7716998786249567,
        0.6987669756889591,
        0.7465001464444807,
        0.7025769273142314
      ],
      "q": [
        1.1972473873585778,
        1.1964259002937887
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 0.8,
      "h": 0.4,
      "evidence_grade": "candidate",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 2.7411809488953054e-09,
          "delta_correlation": 4.274797789749485e-06,
          "delta_entropy": 1.768487616526926e-05
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 2.383731271630533e-08,
          "delta_correlation": 3.9758649487686704e-05,
          "delta_entropy": 0.00023248792184427103
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        1.047930245770794,
        0.8308555095514865,
        1.4051861545829407,
        1.51243844299628
      ],
      "q": [
        1.4080193932503047,
        1.4210597955852995
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 0.8,
      "h": 0.5,
      "evidence_grade": "supported_in_tested_window",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": true,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": true
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 1.1692202761537374e-11,
          "delta_correlation": 1.791496128666914e-07,
          "delta_entropy": 8.360697245635151e-08
        },
        {
          "n": 96,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 1.5817865535912764e-10,
          "delta_correlation": 1.4897400077429346e-06,
          "delta_entropy": 1.8416002349752603e-06
        }
      ],
      "initialization_checks": [
        {
          "n": 64,
          "delta_energy_per_site": 4.440892098500626e-16,
          "delta_correlation": 1.754261735875673e-10,
          "delta_entropy": 1.28807053911828e-09
        },
        {
          "n": 96,
          "delta_energy_per_site": 9.177843670234628e-15,
          "delta_correlation": 1.2852498509907662e-09,
          "delta_entropy": 4.506861550623853e-10
        }
      ],
      "entropy_c": [
        1.0544424112994253,
        1.1137908935769356,
        1.019960958496629,
        0.9899847949780392
      ],
      "q": [
        1.3557113172080155,
        1.3583182924238817
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 0.8,
      "h": 0.6,
      "evidence_grade": "candidate",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": false,
        "connected_power_preferred": false,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 9.570753078946836e-10,
          "delta_correlation": 3.581637460420284e-06,
          "delta_entropy": 4.132943528523114e-06
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 4.197145446009169e-09,
          "delta_correlation": 1.4558597380753824e-05,
          "delta_entropy": 3.039943724048033e-05
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        0.5079166816315216,
        0.4853316888273852,
        0.38821600295465686,
        0.34258269578417205
      ],
      "q": [
        1.3221262221178174,
        1.323567555565415
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 1.0,
      "h": 0.6,
      "evidence_grade": "candidate",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 2.4974942114397436e-09,
          "delta_correlation": 1.5103310792019542e-06,
          "delta_entropy": 1.1918351181083864e-05
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 1.9749347194656746e-08,
          "delta_correlation": 3.715674860604867e-05,
          "delta_entropy": 0.00016129255199626158
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        0.9287673953694087,
        1.2641721855719097,
        1.1050791130197686,
        0.8298072411976607
      ],
      "q": [
        1.4593172157350194,
        1.4633616226091983
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 1.0,
      "h": 0.7,
      "evidence_grade": "supported_in_tested_window",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": true,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": true,
        "connected_power_preferred": true,
        "independent_initializations_available_and_agree": true
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 1.322342235710039e-11,
          "delta_correlation": 1.4913047513553934e-07,
          "delta_entropy": 6.774540484144609e-08
        },
        {
          "n": 96,
          "chi_low": 128,
          "chi_high": 256,
          "delta_energy_per_site": 1.9593926481320523e-10,
          "delta_correlation": 1.183318005026912e-06,
          "delta_entropy": 1.6535906626202745e-06
        }
      ],
      "initialization_checks": [
        {
          "n": 64,
          "delta_energy_per_site": 5.10702591327572e-15,
          "delta_correlation": 9.978455561832078e-11,
          "delta_entropy": 5.558908888758651e-11
        },
        {
          "n": 96,
          "delta_energy_per_site": 1.5395092608135503e-14,
          "delta_correlation": 1.40297123918387e-09,
          "delta_entropy": 3.5452178970274417e-09
        }
      ],
      "entropy_c": [
        1.144611611994371,
        1.0931934650890949,
        1.1327405582624859,
        1.13941448007713
      ],
      "q": [
        1.4187778585075361,
        1.425344775332354
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    },
    {
      "kappa": 1.0,
      "h": 0.8,
      "evidence_grade": "candidate",
      "criteria": {
        "bond_converged": true,
        "entropy_windows_near_c1": false,
        "incommensurate_size_stable": true,
        "power_aic_preferred_both_windows": false,
        "connected_power_preferred": false,
        "independent_initializations_available_and_agree": false
      },
      "checks": [
        {
          "n": 64,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 1.9769383907686233e-09,
          "delta_correlation": 3.488950451102646e-06,
          "delta_entropy": 6.235944622678957e-06
        },
        {
          "n": 96,
          "chi_low": 64,
          "chi_high": 128,
          "delta_energy_per_site": 1.0444017058593621e-08,
          "delta_correlation": 1.8547113658479164e-05,
          "delta_entropy": 5.562805706604834e-05
        }
      ],
      "initialization_checks": [],
      "entropy_c": [
        0.7120137726659252,
        0.655299882745414,
        0.6064614197125022,
        0.5703478373500779
      ],
      "q": [
        1.395678047768858,
        1.3956378957680713
      ],
      "claim": "Finite OBC numerical evidence; not a phase boundary or a small-N noisy label"
    }
  ],
  "missing": "No universal thermodynamic boundary or transfer of labels to noisy small N"
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv-tn/bin/python scripts/run_upgrade_floating.py --task refine
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
