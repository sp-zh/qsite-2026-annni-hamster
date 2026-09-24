import sys,json,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
def main(task):
 records=json.loads((OUT/task/'index.json').read_text());rows=[];t=time.perf_counter()
 for i,point in enumerate(records):
  out=dict(n=point['n'],kappa=point['kappa'],h=point['h'],methods={})
  for method,row in point['methods'].items():
   out['methods'][method]=[noise_record(row,p,keep=task in ['development','heldout']) for p in [0,.01,.05]]
  # Frozen B4 rule uses noisy energy only, paid p=.01 pilot on both equivalent compiles.
  # No ED filtering: preparation pass is reported solely as evaluation mask.
  b3=point['methods']['B3'];normal=out['methods']['B3'][1];rev=noise_record(b3,.01,reverse=True,keep=task in ['development','heldout'])
  reverse=bool(rev['energy']<normal['energy']);out['B4_selection']=dict(criterion='smaller p=.01 energy among exact p0-equivalent compiled directions',reverse=reverse,extra_pilot_cnots=rev['cnots'],extra_pilot_configs=1,energies=[normal['energy'],rev['energy']])
  out['methods']['B4']=[noise_record(b3,p,reverse=reverse,keep=task in ['development','heldout']) for p in [0,.01,.05]];rows.append(out)
  if i%5==0 or i==len(records)-1:
   dump(OUT/task/'noise_index.json',rows);print(task,i+1,round(time.perf_counter()-t,2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--task',required=True);a=p.parse_args();main(a.task)
