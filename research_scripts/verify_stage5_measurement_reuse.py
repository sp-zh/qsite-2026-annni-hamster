"""Benchmark and verify N12 probabilities against the original literal rotations."""
import sys,json,time,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.upgrade_mitigation import groups as original,estimated_vector
from annni.stage5_measurement_groups import groups as reused
rows=json.loads((OUT/'n12_scaling/noise_index.json').read_text())
point=next(r for r in rows if r['kappa']==0 and r['h']==.5)
r=next(e['record'] for e in point['entries'] if e['arm']=='B5_192' and e['record']['p']==.01)
assert r['key']['keep_density'] and sha(ROOT/r['archive'])==r['sha256']
rho=np.load(ROOT/r['archive'])['rho'];t=time.perf_counter();old=original(rho);old_seconds=time.perf_counter()-t;t=time.perf_counter();new=reused(rho);new_seconds=time.perf_counter()-t
assert list(old)==list(new) and len(new)==68
for b in old:np.testing.assert_allclose(new[b],old[b],atol=2e-14,rtol=2e-12)
for sv in [False,True]:np.testing.assert_allclose(estimated_vector(new,12,sv)[0],estimated_vector(old,12,sv)[0],atol=2e-12)
dump(OUT/'verification/measurement_reuse.json',dict(passed=True,timestamp=datetime.now(timezone.utc).isoformat(),n=12,source=r['archive'],source_sha=r['sha256'],old_implementation_sha=sha(ROOT/'annni/upgrade_mitigation.py'),new_implementation_sha=sha(ROOT/'annni/stage5_measurement_groups.py'),settings=68,max_absolute_probability_difference=max(float(np.max(abs(old[b]-new[b]))) for b in old),literal_rotation_seconds=old_seconds,reused_representation_seconds=new_seconds,speedup=old_seconds/new_seconds,process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Classical simulator probability calculation only; exactly the same physical basis rotations, joint outcomes, CNOT/noise/shot budgets and sampling order. Pilot extra cost retained.'))
print(old_seconds,new_seconds,flush=True)
