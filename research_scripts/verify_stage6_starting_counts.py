"""Fresh recount of historical raw run indices; only representative physical recomputation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.upgrade_gates import compile_circuit,evolve,h_action
b0path=ROOT/'results/stage3_v1/grid/selection_frozen.json';path=ROOT/'results/stage5_v1/selector_benchmark/map/index.json';b0=json.loads(b0path.read_text())['rows'];rows=json.loads(path.read_text());counts={'B0_joint':sum(r['joint_pass'] for r in b0),'B0_total':len(b0)}
for name in ['B3','B5']:
 counts[name+'_joint']=sum(r[name]['joint_pass'] for r in rows);counts[name+'_median_cnot']=float(np.median([r[name]['selected']['cnots'] for r in rows]))
counts['has_qualified_old_candidate']=sum(any(c['joint_pass'] for c in r['candidates']) for r in rows);checks=[]
for index in [0,201,419]:
 for name in ['B3','B5']:
  r=rows[index][name];a=np.load(ROOT/r['archive']);assert sha(ROOT/r['archive'])==r['sha256'];s=evolve(compile_circuit(r['n'],r['ref'],r['selected']['words'],r['selected']['params']),r['n']);np.testing.assert_allclose(s,a['state'],atol=1e-11);energy=float(np.vdot(s,h_action(s,r['n'],r['kappa'],r['h'])).real);assert abs(energy-r['energy'])<1e-9;checks.append(dict(index=index,method=name,archive=r['archive'],state_max_error=float(np.max(abs(s-a['state']))),energy_error=energy-r['energy']))
dump(OUT/'verification/stage5_starting_recount.json',dict(time=datetime.now(timezone.utc).isoformat(),counts=counts,checks=checks,source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [b0path,path]},scope='Recounted raw indices and6literal circuit/state/energy recomputations. Not a repeated full420point optimization or audit.'));print(counts)
