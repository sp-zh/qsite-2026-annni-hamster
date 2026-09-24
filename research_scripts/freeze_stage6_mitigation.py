"""One estimator per preparation, chosen only on new validation; no p-dependent refits."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=OUT/'end_to_end/mitigation_frozen.json'
if p.exists():
 saved=json.loads(p.read_text());assert saved['confirmation_used'] is False
 print('Existing frozen estimator retained');raise SystemExit(0)
rows=json.loads((OUT/'end_to_end/validation_analysis.json').read_text());assert len(rows)==24;new=json.loads((OUT/'confirmation/method_frozen.json').read_text())['physical_method'];ranking={};selected={}
def region(r):return 'low_field' if .4<=r['kappa']<=.6 and r['h']<=.35 else 'transition_band' if r['kappa']>.6 and .2<=r['h']<=.7 else 'interior'
for method in ['B3',new]:
 options=[]
 for estimator in ['raw','zne','zne_quadratic','sv']:
  groups={};nonfinite=0
  for r in rows:
   for e in r['entries']:
    if e['method']!=method or e['estimator']!=estimator or e['p']==0:continue
    groups.setdefault(region(r),[]).extend(s['error_ED']['mse'] for s in e['samples'] if s['budget']==100000);nonfinite+=e['quality']['100000']['nonfinite']
  values={g:float(np.mean(x)) for g,x in groups.items()};options.append(dict(estimator=estimator,macro_ED_MSE=float(np.mean(list(values.values()))),region_MSE=values,nonfinite=nonfinite))
 best=min(options,key=lambda x:(x['nonfinite']>0,x['macro_ED_MSE'],['raw','zne','zne_quadratic','sv'].index(x['estimator'])));selected[method]=best['estimator'];ranking[method]=options
dump(p,dict(timestamp=datetime.now(timezone.utc).isoformat(),selected=selected,all_options=ranking,validation_sha=sha(OUT/'end_to_end/validation_analysis.json'),code_sha=sha(__file__),selection='At100k totalshots, equal macro-weight to low-field/band/interior, average p=.01/.05 and all32 repetitions, ED MSE primary. One estimator per preparation at every p. All estimators retained in core/windows; full maps always retain raw.',confirmation_used=False));print(selected)
