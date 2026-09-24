"""Matched full-grid raw shot comparator using already executed ZNE scale-1 distributions."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_e2e import *
O=OUT/'end_to_end';rows=[];start=time.perf_counter()
note=O/'full_raw_extension.json'
if not note.exists():dump(note,dict(timestamp=datetime.now(timezone.utc).isoformat(),scope='Full420 raw with the same10k/100k total budgets and32 repeats as frozen ZNE, for matched map comparison. No classifier/selector/estimator changes. Existing exact scale1 distributions reused by physical fingerprint.',reason='Keep displayed full-grid raw and mitigated labels on the same finite-shot definition; deterministic raw map is retained separately.',additional_quantum_distributions_expected=0,allocation_unchanged=True))
for i,(k,h) in enumerate(PLAN['final_map']):
 guard();selected=json.loads((OUT/'selector_benchmark/map'/f'n8_k{k:.6f}_h{h:.6f}.json').read_text())['B5'];a=np.load(ROOT/selected['archive']);c=selected['selected'];row=dict(n=8,kappa=k,h=h,state=a['state'],ed_vector=vector(observations(a['ed_state'],8)),gates=compile_circuit(8,selected['ref'],c['words'],c['params']),joint_pass=selected['joint_pass'])
 entries=[dict(arm='B5_raw',record=measured(row,p,'raw')) for p in [0,.01,.05]];rows.append(dict(n=8,kappa=k,h=h,entries=entries));dump(O/'full_raw_index.json',rows)
 if i%20==0:print('full raw',i+1,420,round(time.perf_counter()-start,2),flush=True)
print('full raw complete',len(rows),round(time.perf_counter()-start,2),flush=True)
