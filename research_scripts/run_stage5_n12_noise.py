"""Paired frozen-coordinate budgets/selectors; includes failed preparations."""
import sys,json,time,argparse,hashlib,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_selection import choose,materialize
from annni.stage5_baseline_selectors import choose
from annni.stage5_noise import noise_record
parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args();O=OUT/'n12_scaling';cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector'];audit=json.loads((OUT/'selector_benchmark/audit/index.json').read_text());rows=[];start=time.perf_counter()
for k,h in PLAN['n12_noise_points']:
 point=next(r for r in audit if r['n']==12 and abs(r['kappa']-k)<1e-10 and abs(r['h']-h)<1e-10);arms={}
 for rule in ['S0','S1','S2']:
  c=choose(point['candidates'],rule,cfg)['candidate'];c=c|dict(uid=hashlib.sha256(json.dumps([c['uid'],12,k,h]).encode()).hexdigest());arms[rule+'_128']=materialize(c)
 extra=OUT/'selector_benchmark/n12_192'/f'n12_k{k:.6f}_h{h:.6f}.json'
 if not extra.exists():raise RuntimeError('Wait for completed N12 clean budget comparison: '+str(extra))
 large=json.loads(extra.read_text());c=large['selectors']['S2']['candidate'];c=c|dict(uid=hashlib.sha256(json.dumps([c['uid'],12,k,h]).encode()).hexdigest());arms['S2_192']=materialize(c);arms['B5_192']=large['B5'];entries=[]
 for name,arm in arms.items():
  for p in [0,.01,.05]:
   t=time.perf_counter();keep=(name in ['S2_192','B5_192'] and any(abs(k-a)<1e-10 and abs(h-b)<1e-10 for a,b in PLAN['n12_mitigation_points']));r=noise_record(arm,p,keep=keep);entries.append(dict(arm=name,record=r,actual_call_seconds=time.perf_counter()-t,process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss));print(k,h,name,p,entries[-1]['actual_call_seconds'],flush=True)
   if args.pilot and name=='S2_192' and p==0:dump(O/'density_pilot.json',entries[-1]);sys.exit(0)
 rows.append(dict(kappa=k,h=h,entries=entries));dump(O/'noise_index.json',rows)
print('complete',len(rows),time.perf_counter()-start)
