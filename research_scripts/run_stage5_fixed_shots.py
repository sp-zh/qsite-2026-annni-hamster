"""Targeted finite-shot check of the observed k=.3 fixed-structure peak shift."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_e2e import *
O=OUT/'end_to_end';protocol=dict(timestamp=datetime.now(timezone.utc).isoformat(),kappa=.3,selection='Exploratory follow-up chosen after deterministic coarse/fine fixed-branch peaks showed an apparent positive shift; not a preregistered case selection',method='raw',p=[0,.01,.05],budgets=PLAN['mitigation_shots'],repetitions=32,all_fine_window_coordinates=True)
if not (O/'fixed_shots_protocol.json').exists():dump(O/'fixed_shots_protocol.json',protocol)
rows=[]
for point in json.loads((O/'branches_refined/fixed_index.json').read_text()):
 if point['kappa']!=.3:continue
 r=point['state'];a=np.load(ROOT/r['archive']);row=dict(n=8,kappa=r['kappa'],h=r['h'],state=a['state'],ed_vector=vector(observations(a['ed_state'],8)),gates=compile_circuit(8,r['ref'],r['selected']['words'],r['selected']['params']),joint_pass=r['joint_pass']);rows.append(dict(kappa=r['kappa'],h=r['h'],entries=[measured(row,p,'raw') for p in [0,.01,.05]]));dump(O/'fixed_shots_index.json',rows);print(len(rows),flush=True)
hs=np.array([r['h'] for r in rows]);mid=(hs[:-1]+hs[1:])/2;out=[]
for budget in ['10000','100000']:
 for metric in ['full_observable_change','mx_derivative']:
  loc={}
  for p in [0,.01,.05]:
   arr=np.array([np.load(ROOT/next(e for e in r['entries'] if e['p']==p)['archive'])['samples_'+budget] for r in rows]);d=np.diff(arr,axis=0)/.0125;y=np.linalg.norm(d,axis=2) if metric=='full_observable_change' else abs(d[:,:,-1]);loc[str(p)]=mid[np.argmax(y,axis=0)].tolist()
  out.append(dict(shots=int(budget),metric=metric,locations=loc,shift_p05_minus_p0=np.subtract(loc['0.05'],loc['0']).tolist(),shift_quantiles=np.quantile(np.subtract(loc['0.05'],loc['0']),[.025,.5,.975]).tolist(),scope='Independent measurement repetitions at each p, paired by repeat index for empirical difference; includes peak-search noise, not parameter-population confidence'))
dump(O/'fixed_shots_analysis.json',out);print(out)
