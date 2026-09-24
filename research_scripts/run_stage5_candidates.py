import sys,json,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_selection import load_candidates,choose,materialize,retry
from annni.stage5_baseline_selectors import choose
def save_candidate(c):
 c=c|dict(uid=hashlib.sha256(json.dumps([c['uid'],c['n'],c['kappa'],c['h']]).encode()).hexdigest());return materialize(c)
p=argparse.ArgumentParser();p.add_argument('--task',choices=['audit','validation','test','n12test','n12_192','windows','map'],required=True);args=p.parse_args();task=args.task
O=OUT/'selector_benchmark'/task;O.mkdir(parents=True,exist_ok=True);rows=[];started=time.perf_counter();old=ROOT/'results/stage4_upgrade_v1'
if task in ['audit','map']:
 tasks=['map','heldout','n12'] if task=='audit' else ['map'];work=[]
 for group in tasks:
  for x in json.loads((old/group/'index.json').read_text()):work.append((group,x))
else:
 coords=PLAN['validation_v2'] if task=='validation' else PLAN['test_v2'] if task=='test' else PLAN['n12_test_v2'] if task=='n12test' else PLAN['slices']+PLAN['n12_test_v2'] if task=='n12_192' else [(k,h) for k,hs in PLAN['windows'] for h in hs];work=[(task,dict(kappa=k,h=h,n=12 if task.startswith('n12') else 8)) for k,h in coords]
if task not in ['audit','validation']:
 freeze=json.loads((OUT/'selector_frozen.json').read_text());cfg=freeze['selector']
 if (O/'unsealed.json').exists():assert json.loads((O/'unsealed.json').read_text())['freeze_sha']==sha(OUT/'selector_frozen.json')
 else:dump(O/'unsealed.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),freeze_sha=sha(OUT/'selector_frozen.json'),task=task))
for ii,(group,point) in enumerate(work):
 guard();n=point['n'];k=point['kappa'];h=point['h'];path=O/f'n{n}_k{k:.6f}_h{h:.6f}.json'
 if path.exists():r=json.loads(path.read_text());assert r['selector_code']==sha(ROOT/'annni/stage5_selection.py');rows.append(r);continue
 if 'candidates' in point:runs=point['candidates']
 else:runs=[adaptive(n,k,h,ref,11,budget=192 if task=='n12_192' else 128,group=task) for ref in PLAN['refs']]
 candidates=load_candidates(runs);r=dict(n=n,kappa=k,h=h,group=group,candidates=candidates,selector_code=sha(ROOT/'annni/stage5_selection.py'),same_candidate_set=True)
 r['selectors']={rule:choose(candidates,rule) for rule in ['S0','S1']}
 if task in ['audit','validation']:r['S2_grid']=[dict(config=c,selection=choose(candidates,'S2',c)) for c in PLAN['selector_candidates']]
 else:
  r['selectors']['S2']=choose(candidates,'S2',cfg);expanded,details=retry(candidates,cfg);assert not details.get('triggered') or (details['candidate']['n']==n and abs(details['candidate']['kappa']-k)<1e-12 and abs(details['candidate']['h']-h)<1e-12),'Retry cache Hamiltonian mismatch';r['reoptimization']=details;r['B5_selection']=choose(expanded,'S2',cfg);r['B5']=save_candidate(r['B5_selection']['candidate']);r['B3']=save_candidate(r['selectors']['S0']['candidate'])
 good=[c for c in candidates if c['joint_pass']];r['oracle']=min(good,key=lambda c:(c['cnots'],c['energy'])) if good else None
 old_selected=point.get('methods',{}).get('B3');r['historical_selected']=old_selected
 r['failure_category']=('candidate_available_selection_failed' if good and not r['selectors']['S0']['candidate']['joint_pass'] else 'candidate_available' if good else 'no_qualified_candidate_budget_reached' if any(c['cnots']>=c['source_budget']-1 for c in candidates) else 'early_stop_no_qualified_candidate')
 dump(path,r);rows.append(r)
 dump(O/'index.json',rows)
 if ii%5==0:print(task,ii+1,len(work),round(time.perf_counter()-started,2),flush=True)
dump(O/'index.json',rows)
