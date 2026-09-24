"""Record and repair only S0 baseline compatibility, never retune frozen S2."""
import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_s0 import choose
from annni.stage5_baseline_selectors import choose as choose_baseline
from annni.stage5_selection import materialize
backup=OUT/'verification/s0_before_fix';changes=[];matches=[]
for index in (OUT/'selector_benchmark').glob('*/index.json'):
 rows=json.loads(index.read_text());updated=False
 for r in rows:
  correct=choose(r['candidates'],'S0');old=r['selectors']['S0'];same=correct['candidate']['uid']==old['candidate']['uid']
  if not same:
   original=OUT/'selector_benchmark'/index.parent.name/f"n{r['n']}_k{r['kappa']:.6f}_h{r['h']:.6f}.json";dest=backup/index.parent.name/original.name;dest.parent.mkdir(parents=True,exist_ok=True)
   if not dest.exists():shutil.copy2(original,dest)
   changes.append(dict(task=index.parent.name,n=r['n'],kappa=r['kappa'],h=r['h'],old_uid=old['candidate']['uid'],new_uid=correct['candidate']['uid'],old_pass=old['candidate']['joint_pass'],new_pass=correct['candidate']['joint_pass'],frozen_S2_unchanged=True))
   r['selectors']['S0']=correct;r['S0_compatibility_code']=sha(ROOT/'annni/stage5_s0.py')
   if 'B3' in r:
    c=correct['candidate'];c=c|dict(uid=hashlib.sha256(json.dumps([c['uid'],c['n'],c['kappa'],c['h']]).encode()).hexdigest());r['B3']=materialize(c)
   good=r['oracle'] is not None;r['failure_category']=('candidate_available_selection_failed' if good and not correct['candidate']['joint_pass'] else 'candidate_available' if good else r['failure_category']);dump(original,r);updated=True
  correct_s1=choose_baseline(r['candidates'],'S1')
  if correct_s1['candidate']['uid']!=r['selectors']['S1']['candidate']['uid']:
   original=OUT/'selector_benchmark'/index.parent.name/f"n{r['n']}_k{r['kappa']:.6f}_h{r['h']:.6f}.json";dest=backup/index.parent.name/original.name;dest.parent.mkdir(parents=True,exist_ok=True)
   if not dest.exists():shutil.copy2(original,dest)
   changes.append(dict(rule='S1',task=index.parent.name,n=r['n'],kappa=r['kappa'],h=r['h'],old_uid=r['selectors']['S1']['candidate']['uid'],new_uid=correct_s1['candidate']['uid'],frozen_S2_unchanged=True));r['selectors']['S1']=correct_s1;r['baseline_compatibility_code']=sha(ROOT/'annni/stage5_baseline_selectors.py');dump(original,r);updated=True
  if r.get('historical_selected'):
   h=r['historical_selected'];c=correct['candidate'];matches.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],same_ref=c['ref']==h['ref'],same_words=c['words']==h['selected']['words'],same_params=c['params']==h['selected']['params']))
 if updated:
  dest=backup/index.parent.name/'index.json'
  if not dest.exists():shutil.copy2(index,dest)
  dump(index,rows)
log=OUT/'verification/s0_compatibility_corrections.json';prior=json.loads(log.read_text()) if log.exists() else []
prior.append(dict(timestamp=datetime.now(timezone.utc).isoformat(),changes=changes,historical_parameter_matches=sum(all(r[k] for k in ['same_ref','same_words','same_params']) for r in matches),historical_count=len(matches),comparison=matches,reason='Implementation correction to requested historical S0, not tuning after test; original outputs retained; S1/S2 candidate choice and freeze unchanged'));dump(log,prior)
for name in ['core_index.json','refined_index.json']:
 p=OUT/'end_to_end'/name;dest=backup/'end_to_end'/name
 if p.exists() and not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
print('Corrected',len(changes),'point records; historical matches',prior[-1]['historical_parameter_matches'],'/',len(matches))
