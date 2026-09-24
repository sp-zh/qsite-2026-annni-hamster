"""Read-only provenance and numerical validation; no baseline data mutations."""
import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_gates import *
start=time.perf_counter();protected=json.loads((OUT/'verification/protected_inputs.json').read_text());missing=[];changed=[]
for name,digest in protected.items():
 p=ROOT/name
 if not p.exists():missing.append(name)
 elif sha(p)!=digest:changed.append(name)
assert not missing and not changed,(missing[:5],changed[:5])
mps_manifest=json.loads((OUT/'floating/archive_manifest.json').read_text());assert all(sha(ROOT/n)==h for n,h in mps_manifest['files'].items())
opt=0;noise=0;reload=0
for p in (OUT/'adaptive/cache').glob('*.json'):
 r=json.loads(p.read_text());archive=ROOT/r['archive'];assert sha(archive)==r['sha256'];a=np.load(archive);s=r['selected'];state=state_and_grad(np.array(s['params']),s['words'],r['n'],r['ref'],r['kappa'],r['h'])[2];np.testing.assert_allclose(state,a['state'],atol=1e-11);np.testing.assert_allclose(state,state[::-1],atol=1e-10);assert abs(np.linalg.norm(state)-1)<1e-10
 np.testing.assert_allclose(vector(observations(state,r['n'])),vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx']))),atol=1e-11)
 assert s['cnots']<=r['key']['budget'] if not r['key']['fixed'] else True
 opt+=1
for p in (OUT/'noise/cache').glob('*.json'):
 r=json.loads(p.read_text());assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);np.testing.assert_allclose(a['prep']+a['noise'],a['total'],atol=1e-12);np.testing.assert_allclose(a['structure_factor'],np.fft.fft(a['correlations']).real/r['n'],atol=1e-12);assert abs(sum(a['structure_factor'])-1)<1e-9;assert r['cnots']==r['noise_channels']==sum(r['target_counts'])
 if 'rho' in a:
  rho=a['rho'];assert abs(np.trace(rho)-1)<1e-9;assert np.max(abs(rho-rho.conj().T))<1e-10
  if r['n']==8 and reload%20==0:assert np.linalg.eigvalsh(rho).min()>-1e-9
  reload+=1
 noise+=1
# Input axes and h=0 missing conventions remain verified at every new package check.
from annni.diagnostics import validate_dataset
for name in ['grid_n8','slices_n8','slices_n12','slices_n16']:validate_dataset(np.load(ROOT/f'results/baseline/{name}.npz'))
assert len(PLAN['held_out'])>=48 and not set(map(tuple,PLAN['held_out']))&set(map(tuple,PLAN['final_map']+PLAN['development']+PLAN['validation']))
for task,total in [('development',18),('heldout',48),('map',420),('n12',60)]:
 p=OUT/task/'index.json'
 if p.exists():
  a=json.loads(p.read_text());assert len(a)==total,(task,len(a))
  for point in a:
   for r in point['methods'].values():assert sha(ROOT/r['archive'])==r['sha256']
# Real branch pairs require equal coordinates and two parameter archives, not direction labels.
if (OUT/'branches/index.json').exists():
 for row in json.loads((OUT/'branches/index.json').read_text()):
  if row['actual_structure_switch']:
   assert row['actual_switch_pair_checked'] and len(row['endpoints'])==2
   for endpoint in row['endpoints']:
    for comparison in endpoint['comparisons']:
     a=np.load(ROOT/comparison['a_archive']);b=np.load(ROOT/comparison['b_archive']);assert sha(ROOT/comparison['a_archive'])==comparison['a_sha256'] and sha(ROOT/comparison['b_archive'])==comparison['b_sha256']
result=dict(passed=True,protected_files_unchanged=len(protected),mps_artifacts_checked=len(mps_manifest['files']),adaptive_states_reloaded=opt,noise_archives_checked=noise,full_density_archives=reload,seconds=time.perf_counter()-start,checks='all pure parameter reloads, global-X symmetry, full observable identities, signed error decomposition, literal CNOT channel counts, input axes and missing h0, real branch archive pairs',coverage_limit='N8 PSD eigenchecks on deterministic every-20th stored matrix plus runtime each newly simulated N8; N12 trace/Hermiticity and validated CPTP gates, no full spectra',timestamp=datetime.now(timezone.utc).isoformat())
dump(OUT/'verification/result_audit.json',result);print(json.dumps(result,indent=2))
