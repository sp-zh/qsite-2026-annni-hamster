# Multi-reference calibration

Disposition: newly_executed, except explicitly historical B0/ED inputs.

18 declared points, three seeds per reference. Each run is energy optimized; ED only evaluates. See seed_selected_stability.csv for whole-selector reproducibility, not best-seed success.

```json
{
  "B3": {
    "points": 18,
    "passed": 14,
    "median_cnots": 96.0,
    "min_cnots": 31,
    "max_cnots": 128,
    "median_delta_e": 7.766609345860598e-05,
    "failures": [
      {
        "kappa": 0.8,
        "h": 0.6,
        "delta_e": 0.0016282987738605037,
        "fidelity": 0.996460791581279,
        "epsilon_c": 0.02128098629098063,
        "epsilon_sf": 0.0056786696760360855,
        "epsilon_mx": 0.0039790268573008936
      },
      {
        "kappa": 0.45,
        "h": 0.15,
        "delta_e": 0.0009592287875106464,
        "fidelity": 0.9878974427522592,
        "epsilon_c": 0.0943352146225575,
        "epsilon_sf": 0.045317192543196855,
        "epsilon_mx": 0.0070168096430758276
      },
      {
        "kappa": 0.5,
        "h": 0.15,
        "delta_e": 0.0009385590874509964,
        "fidelity": 0.9941485620012684,
        "epsilon_c": 0.03053923005768433,
        "epsilon_sf": 0.008127255733253583,
        "epsilon_mx": 0.0015814942343941318
      },
      {
        "kappa": 0.55,
        "h": 0.15,
        "delta_e": 0.0024332462670709765,
        "fidelity": 0.9424710327751767,
        "epsilon_c": 0.0634352070176362,
        "epsilon_sf": 0.022706668750881592,
        "epsilon_mx": 0.008405841413029913
      }
    ]
  },
  "B1": {
    "points": 18,
    "passed": 11,
    "median_cnots": 106.0,
    "min_cnots": 32,
    "max_cnots": 128,
    "median_delta_e": 0.00021674792501485962,
    "failures": [
      {
        "kappa": 0.8,
        "h": 0.2,
        "delta_e": 0.0003397810976473181,
        "fidelity": 0.5000308742805984,
        "epsilon_c": 0.0019384664244119776,
        "epsilon_sf": 0.0006253198765148738,
        "epsilon_mx": 0.006927457134148607
      },
      {
        "kappa": 0.8,
        "h": 0.5,
        "delta_e": 0.0013959483327573574,
        "fidelity": 0.9939270788694918,
        "epsilon_c": 0.03347691651951057,
        "epsilon_sf": 0.009573663952995415,
        "epsilon_mx": 0.014895841201673532
      },
      {
        "kappa": 0.8,
        "h": 0.6,
        "delta_e": 0.0029133226111778265,
        "fidelity": 0.9903999417698816,
        "epsilon_c": 0.04526110997061883,
        "epsilon_sf": 0.01196510543656984,
        "epsilon_mx": 0.008897137076505968
      },
      {
        "kappa": 0.8,
        "h": 0.8,
        "delta_e": 0.0016968843284415058,
        "fidelity": 0.9973702728999624,
        "epsilon_c": 0.0095928088320366,
        "epsilon_sf": 0.003744806217193447,
        "epsilon_mx": 0.004312886544864725
      },
      {
        "kappa": 0.45,
        "h": 0.15,
        "delta_e": 0.001968252222417033,
        "fidelity": 0.9321292474778652,
        "epsilon_c": 0.29439739351506805,
        "epsilon_sf": 0.1535274812457859,
        "epsilon_mx": 0.03966501177278703
      },
      {
        "kappa": 0.5,
        "h": 0.15,
        "delta_e": 0.0016471453885241738,
        "fidelity": 0.9848657434450884,
        "epsilon_c": 0.05741045162428765,
        "epsilon_sf": 0.016830762225861703,
        "epsilon_mx": 0.00198088421741216
      },
      {
        "kappa": 0.55,
        "h": 0.15,
        "delta_e": 0.006207664741953112,
        "fidelity": 0.6484819548718755,
        "epsilon_c": 0.5712867151266311,
        "epsilon_sf": 0.1566148751892858,
        "epsilon_mx": 0.12482275026902179
      }
    ]
  },
  "B2": {
    "points": 18,
    "passed": 2,
    "median_cnots": 23.0,
    "min_cnots": 6,
    "max_cnots": 23,
    "median_delta_e": 0.02393075515999532,
    "failures": [
      {
        "kappa": 0.0,
        "h": 0.9,
        "delta_e": 0.026302906257427594,
        "fidelity": 0.8914196287781212,
        "epsilon_c": 0.17480591671756318,
        "epsilon_sf": 0.12365822915857205,
        "epsilon_mx": 0.13008983104767052
      },
      {
        "kappa": 0.0,
        "h": 1.0,
        "delta_e": 0.04142938685543163,
        "fidelity": 0.8300655158512804,
        "epsilon_c": 0.26034689753696005,
        "epsilon_sf": 0.18143824261920005,
        "epsilon_mx": 0.17107263391465566
      },
      {
        "kappa": 0.0,
        "h": 1.1,
        "delta_e": 0.06003604391842088,
        "fidelity": 0.7730260653768439,
        "epsilon_c": 0.3327234692965947,
        "epsilon_sf": 0.2285290649128786,
        "epsilon_mx": 0.1978210356315816
      },
      {
        "kappa": 0.0,
        "h": 1.8,
        "delta_e": 0.017782016757617036,
        "fidelity": 0.9735346187207365,
        "epsilon_c": 0.1217706362992465,
        "epsilon_sf": 0.07185692714230238,
        "epsilon_mx": 0.027265565948902726
      },
      {
        "kappa": 0.3,
        "h": 0.4,
        "delta_e": 0.008517740423240938,
        "fidelity": 0.8887911448399965,
        "epsilon_c": 0.16893803548375397,
        "epsilon_sf": 0.1150165437017322,
        "epsilon_mx": 0.11011099239202748
      },
      {
        "kappa": 0.3,
        "h": 0.5,
        "delta_e": 0.02611909063399409,
        "fidelity": 0.6406104761639508,
        "epsilon_c": 0.5122245502719958,
        "epsilon_sf": 0.3360727083729642,
        "epsilon_mx": 0.2385978686478596
      },
      {
        "kappa": 0.3,
        "h": 1.2,
        "delta_e": 0.005640117826054336,
        "fidelity": 0.991127340186028,
        "epsilon_c": 0.04128446547800214,
        "epsilon_sf": 0.016446642885684426,
        "epsilon_mx": 0.014827889959476814
      },
      {
        "kappa": 0.8,
        "h": 0.2,
        "delta_e": 0.0004133776061459038,
        "fidelity": 0.4998631612946367,
        "epsilon_c": 0.0023254251754935007,
        "epsilon_sf": 0.0007702545549942985,
        "epsilon_mx": 0.008367385701002789
      },
      {
        "kappa": 0.8,
        "h": 0.4,
        "delta_e": 0.056490865998255035,
        "fidelity": 0.8255540500485854,
        "epsilon_c": 0.11132857569924415,
        "epsilon_sf": 0.03914312033461076,
        "epsilon_mx": 0.31925634268623937
      },
      {
        "kappa": 0.8,
        "h": 0.5,
        "delta_e": 0.018415419522443743,
        "fidelity": 0.4682746549016166,
        "epsilon_c": 0.14731612193207666,
        "epsilon_sf": 0.04687808413342065,
        "epsilon_mx": 0.15341494787214982
      },
      {
        "kappa": 0.8,
        "h": 0.6,
        "delta_e": 0.038142009208955274,
        "fidelity": 0.42631612260657054,
        "epsilon_c": 0.2980010291488149,
        "epsilon_sf": 0.09329641275074285,
        "epsilon_mx": 0.23822895362567548
      },
      {
        "kappa": 0.8,
        "h": 0.8,
        "delta_e": 0.08222997000222709,
        "fidelity": 0.7421672294535488,
        "epsilon_c": 0.4243598601440313,
        "epsilon_sf": 0.1404793667361631,
        "epsilon_mx": 0.09707803097998147
      },
      {
        "kappa": 0.8,
        "h": 1.2,
        "delta_e": 0.05986516013351517,
        "fidelity": 0.8839391878968199,
        "epsilon_c": 0.2580891365263265,
        "epsilon_sf": 0.09849299792164376,
        "epsilon_mx": 0.033462418390443505
      },
      {
        "kappa": 0.45,
        "h": 0.15,
        "delta_e": 0.011545370634792773,
        "fidelity": 0.08204431833146768,
        "epsilon_c": 1.3951957431867852,
        "epsilon_sf": 0.8296734390755685,
        "epsilon_mx": 0.3701908492453253
      },
      {
        "kappa": 0.5,
        "h": 0.15,
        "delta_e": 0.04636177650167761,
        "fidelity": 0.35852504271830876,
        "epsilon_c": 0.5350318423202942,
        "epsilon_sf": 0.16269217954120163,
        "epsilon_mx": 0.1821446767385685
      },
      {
        "kappa": 0.55,
        "h": 0.15,
        "delta_e": 0.02174241968599655,
        "fidelity": 0.06324481814481525,
        "epsilon_c": 1.4284869924931898,
        "epsilon_sf": 0.41144344887330037,
        "epsilon_mx": 0.5099892680622312
      }
    ]
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade.py --task development
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
