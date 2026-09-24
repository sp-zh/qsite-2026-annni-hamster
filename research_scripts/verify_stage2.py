"""Independent saved-artifact checks; does not optimize or rerun ED scans."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
import json,hashlib
import numpy as np
from annni.circuits import observe,HVAEngine,qnode
from annni.vqe import metrics
from annni.noise import density_checks
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'results/calibration_v1'
audit=json.loads((out/'input_audit.json').read_text())
for p,sha in audit['protected_sha256'].items():assert digest(ROOT/p)==sha,p
manifest=json.loads((out/'run_manifest.json').read_text())
for p,sha in manifest['hashes'].items():assert digest(ROOT/p)==sha,p
cfg=manifest['configuration']
rows=[json.loads(p.read_text()) for p in sorted((out/'runs').glob('*.json'))]
max_norm=max_parity=max_translation=max_metric=0.
for r in rows:
    path=out/'runs'/f"{r['run_id']}.npz";assert digest(path)==r['archive_sha256']
    d=np.load(path);s=d['state'];ids=np.arange(256);shift=((ids<<1)&255)|(ids>>7)
    max_norm=max(max_norm,float(abs(np.vdot(s,s)-1)))
    max_parity=max(max_parity,float(np.max(abs(s-s[::-1]))))
    max_translation=max(max_translation,float(np.max(abs(s-s[shift]))))
    met,obs,ref=metrics(s,d['ed_state'],r['ed_energy'],r['kappa'],r['h'],cfg['thresholds'])
    for k in ['energy','delta_e','epsilon_c','epsilon_sf','epsilon_mx','fidelity']:
        max_metric=max(max_metric,abs(met[k]-r[k]))
    assert all(met[k]==r[k] for k in ['observable_pass','state_pass','joint_pass'])
    np.testing.assert_allclose(obs['structure_factor'],d['structure_factor'],atol=1e-12)
    np.testing.assert_allclose(obs['correlations'],d['correlations'],atol=1e-12)
    np.testing.assert_allclose(obs['structure_factor'].sum(),1,atol=1e-11)
assert max(max_norm,max_parity,max_translation,max_metric)<1e-10
selected=json.loads((out/'selected.json').read_text())
qnode_error=0.
for s in selected.values():
    d=np.load(out/'runs'/f"{s['best_run']}.npz")
    qnode_error=max(qnode_error,float(np.max(abs(qnode()(d['final_params'])-d['state']))))
assert qnode_error<1e-10
noise=ROOT/'results/noise_smoke_v1'
meta=json.loads((noise/'metadata.json').read_text())
for p,sha in meta['input_hashes'].items():assert digest(ROOT/p)==sha,p
noise_files=list(noise.glob('p*_noise*.npz'))
for p in noise_files:
    d=np.load(p);density_checks(d['rho'])
    obs=observe(d['rho'])
    np.testing.assert_allclose(obs['structure_factor'],d['structure_factor'],atol=1e-12)
    assert np.linalg.norm(d['params'])>0
result=dict(optimization_runs_checked=len(rows),protected_files_unchanged=len(audit['protected_sha256']),
    max_state_norm_error=max_norm,max_parity_error=max_parity,max_translation_error=max_translation,
    max_saved_metric_error=max_metric,all_selected_pennylane_max_amplitude_error=qnode_error,
    density_archives_checked=len(noise_files),baseline_and_upstream_unchanged=True,
    main_runs=sum(r['layers']<=6 for r in rows),fallback_runs=sum(r['layers']==8 for r in rows))
(out/'verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
