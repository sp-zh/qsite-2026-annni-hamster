import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_noise import noise_record
O=OUT/'n8_maps';a=json.loads((OUT/'selector_benchmark/map/index.json').read_text());out=[];t=time.perf_counter()
for i,r in enumerate(a):
 out.append(dict(kappa=r['kappa'],h=r['h'],selection_unresolved=r['B5_selection']['selection_unresolved'],B5=[noise_record(r['B5'],p) for p in [0,.01,.05]]));dump(O/'noise_index.json',out)
 if i%10==0:print(i+1,len(a),round(time.perf_counter()-t,1),flush=True)
