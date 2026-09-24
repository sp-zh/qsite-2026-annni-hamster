import sys,json,time,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
rows=json.loads((OUT/'n12/index.json').read_text());wanted=PLAN['n12_noise_points'];out=[];t=time.perf_counter()
for point in rows:
 if not any(abs(point['kappa']-k)<1e-12 and abs(point['h']-h)<1e-12 for k,h in wanted):continue
 row=point['methods']['B3'];records=[]
 for p in [0,.01,.05]:
  r=noise_record(row,p);records.append(r);print(point['kappa'],point['h'],p,r['seconds'],resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
 out.append(dict(n=12,kappa=point['kappa'],h=point['h'],row=row,noise=records));dump(OUT/'n12/noise_index.json',out)
dump(OUT/'n12/noise_cost.json',dict(seconds=time.perf_counter()-t,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,backend='exact full density, sequential representatives; no eigenvalue spectrum at N12'))
