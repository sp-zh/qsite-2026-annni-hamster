"""Bounded dev-only oracle audit of every saved growth state; never changes selection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_candidates import evaluate
from annni.stage6_assess import assess
rows=[]
for point in json.loads((OUT/'domain_wall_candidates/development_101_0_index.json').read_text())[:24]:
 for method in ['C0','C1','C2','C3']:
  for path in point['methods'][method]['runs']:
   r=json.loads((ROOT/path).read_text());history=[];words=[]
   for step in r['steps']:
    for probe in step['probes']:
     s=evaluate(probe['final'],words+[probe['word']],r['n'],r['basis'],r['ref'],r['kappa'],r['h'])[2];history.append(dict(growth_step=len(words)+1,kind='bounded_search_probe',word=probe['word'],**assess(s,r['n'],r['kappa'],r['h'])))
    words.append(step['word']);s=evaluate(step['optimization']['final'],words,r['n'],r['basis'],r['ref'],r['kappa'],r['h'])[2];history.append(dict(growth_step=len(words),kind='accepted_growth',**assess(s,r['n'],r['kappa'],r['h'])))
   rows.append(dict(kappa=r['kappa'],h=r['h'],method=method,ref=r['ref'],source=path,candidate_state_count=len(history),all_saved_candidate_joint_pass_count=sum(x['joint_pass'] for x in history),history=history,selection_changed=False,scope='All saved accepted growth and bounded top4 probe states, development only; source distinguishes probes from final accepted growth. Not a deployable oracle selector'))
 dump(OUT/'failure_mechanisms/growth_audit.json',rows);print('growth audit',point['kappa'],point['h'],flush=True)
