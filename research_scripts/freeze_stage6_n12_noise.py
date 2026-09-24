import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
# Complete the registered MPS convergence controls in the same second lane,
# before starting any N12 work; no third heavy process is introduced.
import subprocess
if not (OUT/'verification/progress_mps_controls_done.json').exists():
 with (OUT/'verification/mps_controls.log').open('a') as log:
  result=subprocess.run([str(ROOT/'.venv-tn/bin/python'),'scripts/run_stage6_mps_controls.py'],stdout=log,stderr=subprocess.STDOUT)
  assert result.returncode==0
# Finish the bounded development-only optimization attribution in this free lane.
# These auxiliary results cannot alter already-frozen confirmation generation.
for name,script,artifact in [('energy_continuation','run_stage6_energy_continuation.py','failure_mechanisms/energy_continuation_index.json'),('growth_audit','audit_stage6_intermediates.py','failure_mechanisms/growth_audit.json')]:
 marker=OUT/f'verification/{name}_completed.json'
 if not marker.exists():
  with (OUT/f'verification/{name}.log').open('a') as log:
   result=subprocess.run([sys.executable,'scripts/'+script],stdout=log,stderr=subprocess.STDOUT)
   assert result.returncode==0
  dump(marker,dict(time=datetime.now(timezone.utc).isoformat(),script_sha=sha(ROOT/'scripts'/script),artifact=artifact,artifact_sha=sha(OUT/artifact),scope='development only; no change to frozen methods'))
p=OUT/'n12_transfer/noise_coordinates.json'
if p.exists():
 saved=json.loads(p.read_text());assert len(saved)==12 and len({(r['kappa'],r['h']) for r in saved})==12
 print('Frozen N12 noise coordinates retained');raise SystemExit(0)
base=json.loads((OUT/'n12_transfer/coordinates.json').read_text());window=json.loads((OUT/'n12_transfer/window_coordinates.json').read_text());points=[dict(base[i],source_task='n12') for i in [0,6,12,18,24,30]]+[window[i] for i in np.linspace(0,len(window)-1,6,dtype=int)];assert len({(r['kappa'],r['h']) for r in points})==12;dump(p,points);dump(OUT/'n12_transfer/resource_protocol.json',dict(n=12,seed=631,first_budget=128,full_coordinates=36,window_coordinates=len(window),paired_192_coordinates=base[::3],paired_192_rule='Every third frozen coordinate:4low,4band,4interior; bounded12point resource diagnostic. Expand only after completing all core packages.',noise_coordinates=points,noise_policy='All12predeclaredpoints at p0/.01/.05, including any failed preparations. Exact density first, serial within worker; no post-hoc pass filtering',structure_scaling='Same frozen H6 dispatch and local wall/physical pools, parameter cap160 and per-optimization400iterations. Reference/decode cost grows with N and is included.',coordinate_sha=uid(points)))
