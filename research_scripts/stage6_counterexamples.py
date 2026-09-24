"""State-fidelity and phase-task accuracy are distinct, demonstrated numerically."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_candidates import gate_table
from annni.stage6_assess import assess
from annni.stage6_reference import record
from annni.upgrade_gates import evolve,resources,vector,observations
from annni.upgrade_detection import predict
n=8;k=.8;h=.01;g=gate_table(n,'wall','alternating',[],[]);s=evolve(g,n);metrics=assess(s,n,k,h);cfg=json.loads((ROOT/'results/stage4_upgrade_v1/detection/frozen.json').read_text());r=record(8,.5,.035);ed=np.load(ROOT/r['archive'])['state'];v=vector(observations(ed,8));out=dict(timestamp=datetime.now(timezone.utc).isoformat(),low_fidelity_observables=dict(n=n,kappa=k,h=h,gates=g,**resources(g,n),**metrics,explanation='A real paid two-configuration global-flip cat: translationally averaged C/SF are close to the full four-translation low-field antiphase cat; state overlap about1/2. No symmetry projection or ED loading.'),unit_fidelity_not_phase_truth=dict(n=8,kappa=.5,h=.035,fidelity=1.,old_detector=predict(v,cfg),reference=r['archive'],independent_label=None,explanation='Exact ED data at competing multiphase vicinity remain RN continuous diagnostics; an output resemblance label is not independently established thermodynamic phase truth. This is an ideal-information example, not free quantum StatePrep.'))
dump(OUT/'failure_mechanisms/state_vs_task_counterexamples.json',out);print(metrics)
