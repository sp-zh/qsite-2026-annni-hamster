# Twelve-qubit circuits

Disposition: newly_executed, except explicitly historical B0/ED inputs.

60 new N12 preparations and12 representative exact-density simulations at each of three p. No real hardware. Full matrix spectrum is not computed for every N12 density; validated CPTP gate evolution, trace and Hermiticity are checked.

```json
{
  "preparation": {
    "B3": {
      "points": 60,
      "passed": 40,
      "median_cnots": 127.0,
      "min_cnots": 63,
      "max_cnots": 128,
      "median_delta_e": 0.0001435207606096019,
      "failures": [
        {
          "kappa": 0.0,
          "h": 1.0,
          "delta_e": 0.0012094279124612584,
          "fidelity": 0.9967913907004714,
          "epsilon_c": 0.0208413736806754,
          "epsilon_sf": 0.010689772365054195,
          "epsilon_mx": 0.002862129724978124
        },
        {
          "kappa": 0.0,
          "h": 1.1,
          "delta_e": 0.0015389354393485395,
          "fidelity": 0.9946931541350206,
          "epsilon_c": 0.05580377480964205,
          "epsilon_sf": 0.030117945188706585,
          "epsilon_mx": 0.008858754479414643
        },
        {
          "kappa": 0.0,
          "h": 1.2,
          "delta_e": 0.0006900371026968463,
          "fidelity": 0.9976882213659555,
          "epsilon_c": 0.0349307094229338,
          "epsilon_sf": 0.019072368680612295,
          "epsilon_mx": 0.004174653044315746
        },
        {
          "kappa": 0.0,
          "h": 1.3,
          "delta_e": 0.0006815492399153319,
          "fidelity": 0.9981904575850219,
          "epsilon_c": 0.02651682903089879,
          "epsilon_sf": 0.015492984713370184,
          "epsilon_mx": 0.004009613024271164
        },
        {
          "kappa": 0.3,
          "h": 0.4,
          "delta_e": 0.0007433987449750509,
          "fidelity": 0.9872112971002077,
          "epsilon_c": 0.051784486147610886,
          "epsilon_sf": 0.03380247194986252,
          "epsilon_mx": 0.01692318395958725
        },
        {
          "kappa": 0.3,
          "h": 0.5,
          "delta_e": 0.0005611646610865032,
          "fidelity": 0.9888291669006632,
          "epsilon_c": 0.10706074370153063,
          "epsilon_sf": 0.0671579889658886,
          "epsilon_mx": 0.01866256662682353
        },
        {
          "kappa": 0.3,
          "h": 0.7,
          "delta_e": 0.0001813018462003176,
          "fidelity": 0.9989200714254906,
          "epsilon_c": 0.02417804113697826,
          "epsilon_sf": 0.007218528569352289,
          "epsilon_mx": 0.002088413076498874
        },
        {
          "kappa": 0.3,
          "h": 0.8,
          "delta_e": 0.0001532700881208271,
          "fidelity": 0.9987564279952554,
          "epsilon_c": 0.022691816556437497,
          "epsilon_sf": 0.014459532212740878,
          "epsilon_mx": 0.0010560092846273461
        },
        {
          "kappa": 0.8,
          "h": 0.4,
          "delta_e": 0.0011652476600853372,
          "fidelity": 0.9865345978968658,
          "epsilon_c": 0.026553835775967816,
          "epsilon_sf": 0.008795533715081794,
          "epsilon_mx": 0.019905567306240157
        },
        {
          "kappa": 0.8,
          "h": 0.5,
          "delta_e": 0.005942770768545991,
          "fidelity": 0.8265630358884606,
          "epsilon_c": 0.2916702349638206,
          "epsilon_sf": 0.09067105648082835,
          "epsilon_mx": 0.10822558996806464
        },
        {
          "kappa": 0.8,
          "h": 0.6,
          "delta_e": 0.01028499012950664,
          "fidelity": 0.8666162895948059,
          "epsilon_c": 0.027918122019864378,
          "epsilon_sf": 0.006915482455437827,
          "epsilon_mx": 0.014047023650851198
        },
        {
          "kappa": 0.8,
          "h": 0.7,
          "delta_e": 0.008014794119067137,
          "fidelity": 0.9430476737698608,
          "epsilon_c": 0.07920599007219227,
          "epsilon_sf": 0.025144514201270868,
          "epsilon_mx": 0.014689783981514548
        },
        {
          "kappa": 0.8,
          "h": 0.8,
          "delta_e": 0.005819176460235702,
          "fidelity": 0.9779149752353791,
          "epsilon_c": 0.049425784543207556,
          "epsilon_sf": 0.017269355929638214,
          "epsilon_mx": 0.016633261203948257
        },
        {
          "kappa": 0.8,
          "h": 0.9,
          "delta_e": 0.004482459605287037,
          "fidelity": 0.9875610995716955,
          "epsilon_c": 0.027017351071271345,
          "epsilon_sf": 0.009764525177690886,
          "epsilon_mx": 0.013438053825036378
        },
        {
          "kappa": 0.8,
          "h": 1.0,
          "delta_e": 0.003173869150812377,
          "fidelity": 0.9915804973949552,
          "epsilon_c": 0.03474988343459453,
          "epsilon_sf": 0.012046834498620845,
          "epsilon_mx": 0.009587175053474839
        },
        {
          "kappa": 0.8,
          "h": 1.1,
          "delta_e": 0.003407946919548562,
          "fidelity": 0.9920732187299334,
          "epsilon_c": 0.022817344917214093,
          "epsilon_sf": 0.007482153275151754,
          "epsilon_mx": 0.008736321304339545
        },
        {
          "kappa": 0.8,
          "h": 1.2,
          "delta_e": 0.0023524107407505803,
          "fidelity": 0.9944815272849727,
          "epsilon_c": 0.029071913983073218,
          "epsilon_sf": 0.009276995942110039,
          "epsilon_mx": 0.006171883034987502
        },
        {
          "kappa": 0.8,
          "h": 1.3,
          "delta_e": 0.0015327446560432871,
          "fidelity": 0.9973379133698544,
          "epsilon_c": 0.013219534652520903,
          "epsilon_sf": 0.004797591936935047,
          "epsilon_mx": 0.004008007542966707
        },
        {
          "kappa": 0.8,
          "h": 1.4,
          "delta_e": 0.0013933291134475094,
          "fidelity": 0.9974096335400613,
          "epsilon_c": 0.014061351328983285,
          "epsilon_sf": 0.004783885592250542,
          "epsilon_mx": 0.0033167778695591954
        },
        {
          "kappa": 0.8,
          "h": 1.5,
          "delta_e": 0.0012312411050213374,
          "fidelity": 0.9977393607062011,
          "epsilon_c": 0.013488460758716257,
          "epsilon_sf": 0.004438368043638979,
          "epsilon_mx": 0.0027767137068529513
        }
      ]
    }
  },
  "noise": {
    "points": 12,
    "configs": 36,
    "prep_pass": 8,
    "backend": "exact density"
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_n12_noise.py
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
