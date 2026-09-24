"""Versioned actual examples separating state quality from task reconstruction."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'failure_mechanisms';original=O/'state_vs_task_counterexamples.json';data=json.loads(original.read_text());s=O/'windows_paired_summary.json';rows=json.loads(s.read_text())['rows'];selected=[r for r in rows if r['method']=='B3' and r['kappa']==0];b=OUT/'end_to_end/pure_window_reconstruction.json';boundary=next(r for r in json.loads(b.read_text())['rows'] if r['method']=='B3' and r['kappa']==0)
assert len(selected)==17 and all(r['joint_pass'] for r in selected)
assert boundary['reference_resolvable'] and not boundary['algorithm_estimatable']
data.update(version=2,timestamp=datetime.now(timezone.utc).isoformat(),original_source=str(original.relative_to(ROOT)),original_sha=sha(original),high_fidelity_but_RN_window_ambiguous=dict(method='B3',n=8,kappa=0,coordinates=17,state_pass=17,observable_pass=17,joint_pass=17,minimum_squared_ED_fidelity=min(r['fidelity'] for r in selected),maximum_correlation_error=max(r['epsilon_c'] for r in selected),primary=boundary['result']['primary'],competing_peaks=boundary['result']['competing'],reference_primary=boundary['reference']['primary'],scope='All17 real energy-optimized circuits pass the original state/observable tests, but the frozen unsmoothed response-peak rule detects a competing maximum. High pointwise fidelity alone does not guarantee unique finite-size feature reconstruction. This is not a claim that the exact thermodynamic critical point moved.',source_summaries=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [s,b]],circuits=[r['source'] for r in selected]))
dump(O/'state_vs_task_counterexamples_v2.json',data);print('Both low-F accurate-observable and high-F ambiguous-task circuit examples documented')
