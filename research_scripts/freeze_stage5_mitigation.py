"""Select mitigation only on the predeclared 24-point validation set."""
import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_e2e import *
from annni.stage5_selection import choose,materialize
from datetime import datetime,timezone
O=OUT/'end_to_end';protocol=dict(timestamp=datetime.now(timezone.utc).isoformat(),selection='lowest mean per-observable MSE to own clean circuit at 100000 total shots, equally across validation24 and p=.01/.05; ties gate-shots',methods=['raw','zne','sv'],validation_sha=sha(OUT/'selector_benchmark/validation/index.json'),test_v2_used=False)
if not (O/'mitigation_selection_protocol.json').exists():dump(O/'mitigation_selection_protocol.json',protocol)
cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector'];rows=[]
for point in json.loads((OUT/'selector_benchmark/validation/index.json').read_text()):
 c=choose(point['candidates'],'S2',cfg)['candidate'];c=c|dict(uid=hashlib.sha256(json.dumps([c['uid'],8,point['kappa'],point['h']]).encode()).hexdigest());r=materialize(c);a=np.load(ROOT/r['archive']);row=dict(n=8,kappa=r['kappa'],h=r['h'],state=a['state'],ed_vector=vector(observations(a['ed_state'],8)),gates=compile_circuit(8,r['ref'],r['selected']['words'],r['selected']['params']),joint_pass=r['joint_pass'])
 for p in [.01,.05]:
  for method in ['raw','zne','sv']:rows.append(measured(row,p,method))
 dump(O/'validation_index.json',rows);print(len(rows),flush=True)
scores={m:float(np.mean([r['statistics']['100000']['mse_own_clean'] for r in rows if r['method']==m])) for m in ['raw','zne','sv']};winner=min(['zne','sv'],key=lambda m:scores[m]);dump(O/'mitigation_frozen.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),scores=scores,selected=winner,protocol=protocol,validation_index_sha=sha(O/'validation_index.json'),scope='Frozen for descriptive full map; no test_v2 noise used'));print(winner,scores)
