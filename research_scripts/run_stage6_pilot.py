import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_candidates import *
rows=[]
for k,h in [(.5,.035),(.55,.15),(.8,.6)]:
 for basis,ref in [('physical','antiphase'),('wall','alternating')]:
  for search in ['greedy','top4']:
   r=adaptive(8,k,h,basis,ref,search,101,128);rows.append(r);dump(OUT/'domain_wall_candidates/pilot_index.json',rows);print(k,h,basis,search,round(r['seconds'],2),r['selected']['energy'],r['selected']['cnots'],flush=True)
