# Matched N8 full map

Disposition: newly_executed, except explicitly historical B0/ED inputs.

420 positive-field descriptive coordinates, B3/B4 at three prescribed p. Historical B0 reused unchanged. Global and common-pass statistics differ; neither is classification accuracy.

```json
{
  "B3_p0_all": {
    "points": 420,
    "c_error_mean_new": 0.004703970688472746,
    "c_error_mean_old": 0.0019264822058457755,
    "c_improved": 17,
    "sf_error_mean_new": 0.0016441663057383674,
    "sf_error_mean_old": 0.0006118017404639629,
    "mx_error_mean_new": 0.0012782928621506956,
    "mx_error_mean_old": 0.000531299553305962
  },
  "B3_p0_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.002457526424468546,
    "c_error_mean_old": 0.0005670437271270868,
    "c_improved": 9,
    "sf_error_mean_new": 0.0009659783661804645,
    "sf_error_mean_old": 0.00019085343069657682,
    "mx_error_mean_new": 0.0006977745342256387,
    "mx_error_mean_old": 0.00016893946593693666
  },
  "B3_p0.01_all": {
    "points": 420,
    "c_error_mean_new": 0.1431838708115352,
    "c_error_mean_old": 0.2637546695248888,
    "c_improved": 402,
    "sf_error_mean_new": 0.06921408716704261,
    "sf_error_mean_old": 0.1376200085389517,
    "mx_error_mean_new": 0.17623072654483124,
    "mx_error_mean_old": 0.3293091909185632
  },
  "B3_p0.01_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.1357403199615195,
    "c_error_mean_old": 0.25538748725425464,
    "c_improved": 365,
    "sf_error_mean_new": 0.06825103275250269,
    "sf_error_mean_old": 0.13867303168595105,
    "mx_error_mean_new": 0.17581973352281072,
    "mx_error_mean_old": 0.33229618041056047
  },
  "B3_p0.05_all": {
    "points": 420,
    "c_error_mean_new": 0.36661281532549406,
    "c_error_mean_old": 0.44536145816306466,
    "c_improved": 418,
    "sf_error_mean_new": 0.17849738802078136,
    "sf_error_mean_old": 0.2216423242828738,
    "mx_error_mean_new": 0.5213655005913184,
    "mx_error_mean_old": 0.6762565630623341
  },
  "B3_p0.05_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.3531750770754975,
    "c_error_mean_old": 0.4326896576960182,
    "c_improved": 381,
    "sf_error_mean_new": 0.17803970081057882,
    "sf_error_mean_old": 0.222844459772217,
    "mx_error_mean_new": 0.5267279130404325,
    "mx_error_mean_old": 0.6894916078264863
  },
  "B4_p0_all": {
    "points": 420,
    "c_error_mean_new": 0.004703970688472751,
    "c_error_mean_old": 0.0019264822058457755,
    "c_improved": 17,
    "sf_error_mean_new": 0.0016441663057383726,
    "sf_error_mean_old": 0.0006118017404639629,
    "mx_error_mean_new": 0.0012782928621506901,
    "mx_error_mean_old": 0.000531299553305962
  },
  "B4_p0_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.0024575264244685556,
    "c_error_mean_old": 0.0005670437271270868,
    "c_improved": 9,
    "sf_error_mean_new": 0.0009659783661804718,
    "sf_error_mean_old": 0.00019085343069657682,
    "mx_error_mean_new": 0.0006977745342256342,
    "mx_error_mean_old": 0.00016893946593693666
  },
  "B4_p0.01_all": {
    "points": 420,
    "c_error_mean_new": 0.14142516680602388,
    "c_error_mean_old": 0.2637546695248888,
    "c_improved": 405,
    "sf_error_mean_new": 0.0685607971252497,
    "sf_error_mean_old": 0.1376200085389517,
    "mx_error_mean_new": 0.1741277301465313,
    "mx_error_mean_old": 0.3293091909185632
  },
  "B4_p0.01_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.134193890361843,
    "c_error_mean_old": 0.25538748725425464,
    "c_improved": 368,
    "sf_error_mean_new": 0.06766050463943424,
    "sf_error_mean_old": 0.13867303168595105,
    "mx_error_mean_new": 0.17373086744153596,
    "mx_error_mean_old": 0.33229618041056047
  },
  "B4_p0.05_all": {
    "points": 420,
    "c_error_mean_new": 0.3643525765665762,
    "c_error_mean_old": 0.44536145816306466,
    "c_improved": 418,
    "sf_error_mean_new": 0.17769631975946265,
    "sf_error_mean_old": 0.2216423242828738,
    "mx_error_mean_new": 0.5186320902545183,
    "mx_error_mean_old": 0.6762565630623341
  },
  "B4_p0.05_common_pass": {
    "points": 383,
    "c_error_mean_new": 0.3509782450094442,
    "c_error_mean_old": 0.4326896576960182,
    "c_improved": 381,
    "sf_error_mean_new": 0.17724421876370663,
    "sf_error_mean_old": 0.222844459772217,
    "mx_error_mean_new": 0.5238093328485807,
    "mx_error_mean_old": 0.6894916078264863
  }
}
```

Reproduce from project root, retaining frozen hashes/deadline:

```sh
.venv/bin/python scripts/run_upgrade_noise.py --task map
```

Full provenance and code/input hashes: ../metadata.json and ../verification/.
