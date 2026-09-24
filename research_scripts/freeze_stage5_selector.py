import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
a=json.loads((OUT/'selector_benchmark/validation/index.json').read_text());assert len(a)==24
rows=[]
for i,cfg in enumerate(PLAN['selector_candidates']):
 r=[x['S2_grid'][i]['selection'] for x in a];rows.append(dict(selector=cfg,passed=sum(x['candidate']['joint_pass'] for x in r),unresolved=sum(x['selection_unresolved'] for x in r),mean_cnots=float(np.mean([x['candidate']['cnots'] for x in r]))))
best=min(rows,key=lambda x:(-x['passed'],x['unresolved'],x['mean_cnots'],x['selector']['energy_tolerance_per_site']));result=dict(selector=best['selector'],validation_results=rows,rule='maximize validation joint passes, then unresolved count, then CNOT cost, then smaller energy tolerance; fixed before test_v2 unsealing',timestamp=datetime.now(timezone.utc).isoformat(),validation_sha=sha(OUT/'selector_benchmark/validation/index.json'),code_sha=sha(ROOT/'annni/stage5_selection.py'),access='state-access-assisted design; no free hardware translation measurement; no projection')
p=OUT/'selector_frozen.json'
if p.exists():assert json.loads(p.read_text())['selector']==result['selector'];print('Existing selector matches')
else:dump(p,result);print(json.dumps(result,indent=2))
