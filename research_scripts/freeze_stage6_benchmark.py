import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=OUT/'failure_mechanisms/benchmark.json'
if p.exists():raise SystemExit('Benchmark exists; retained')
a=json.loads((ROOT/'results/stage5_v1/selector_benchmark/audit/index.json').read_text());old=[x for x in a if x['n']==8 and x['group']=='map'];fails=[x for x in old if not x['selectors']['S0']['candidate']['joint_pass']]
required=[(.45,.15),(.5,.15),(.55,.15),(.8,.6),(.8,.8),(.425,.02),(.45,.035),(.475,.05),(.5,.01),(.5,.075),(.525,.035),(.55,.05),(.575,.075)]
coords=required.copy()
for r in fails:
 t=(r['kappa'],r['h'])
 if t not in coords and len(coords)<24:coords.append(t)
controls=[]
for k,h in [(0,.2),(0,1.8),(.1,.2),(.2,1.5),(.3,.1),(.3,1.2),(.4,1.8),(.6,.1),(.7,1.5),(.8,.1),(.9,1.8),(1,.1)]:
 r=min([x for x in old if x['selectors']['S0']['candidate']['joint_pass'] and (x['kappa'],x['h']) not in controls and (x['kappa'],x['h']) not in coords],key=lambda x:abs(x['kappa']-k)+abs(x['h']-h));controls.append((r['kappa'],r['h']))
historical={(round(x['kappa'],10),round(x['h'],10)) for x in a}
for path in (ROOT/'results/stage5_v1/selector_benchmark').glob('*/index.json'):
 for x in json.loads(path.read_text()):
  if 'kappa' in x and 'h' in x:historical.add((round(x['kappa'],10),round(x['h'],10)))
val={tuple(x) for x in PLAN['validation']};conf={(x['kappa'],x['h']) for x in PLAN['confirmation']};assert len(val)==24 and len(conf)==96 and not val&conf and not val&historical and not conf&historical
rows=[dict(kappa=k,h=h,region='difficult',historical=(k,h) in historical) for k,h in coords]+[dict(kappa=k,h=h,region='interior_control',historical=True) for k,h in controls]
dump(p,dict(points=rows,source='Stage5 fixed candidate audit plus13 declared new/old low-field targets; no new method result used',timestamp=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),historical_coordinate_count=len(historical),validation_confirmation_disjoint=True,coordinate_hash=uid(rows)));dump(OUT/'verification/historical_coordinates.json',sorted(historical));print('Fixed36 benchmark,24validation,96confirmation')
