"""Distinguish parameter-only retry from changes in the finally selected circuit."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump
rows=[];summary=[]
for task in ['map','test','n12test','n12_192','windows','refined']:
 path=OUT/'selector_benchmark'/task/'index.json'
 if not path.exists():continue
 points=json.loads(path.read_text());taskrows=[]
 for r in points:
  details=r['reoptimization']
  if not details['triggered']:continue
  new=details['candidate'];initial=next(c for c in r['candidates'] if c['uid']==new['initial_source']);before=r['selectors']['S2']['candidate'];after=r['B5_selection']['candidate']
  assert (new['ref'],new['words'],new['cnots'])==(initial['ref'],initial['words'],initial['cnots'])
  item=dict(task=task,n=r['n'],kappa=r['kappa'],h=r['h'],initial_uid=initial['uid'],retry_uid=new['uid'],nit=details['nit'],nfev=details['nfev'],seconds=details['seconds'],same_gates_as_retry_initialization=True,initial_joint_pass=initial['joint_pass'],retry_joint_pass=new['joint_pass'],delta_energy_per_site=new['delta_e']-initial['delta_e'],final_uses_retry=after['uid']==new['uid'],selector_joint_before=before['joint_pass'],selector_joint_after=after['joint_pass'],selected_structure_changed=(before['ref'],before['words'])!=(after['ref'],after['words']),selected_cnots_before=before['cnots'],selected_cnots_after=after['cnots'],independent_restart=False)
  rows.append(item);taskrows.append(item)
 summary.append(dict(task=task,coordinates=len(points),triggered=len(taskrows),retry_selected=sum(r['final_uses_retry'] for r in taskrows),joint_gains=sum(not r['selector_joint_before'] and r['selector_joint_after'] for r in taskrows),joint_losses=sum(r['selector_joint_before'] and not r['selector_joint_after'] for r in taskrows),selected_structure_changes=sum(r['selected_structure_changed'] for r in taskrows)))
dump(OUT/'selection_audit/reoptimization_effects.json',dict(rows=rows,summary=summary,scope='Same-gate claim is verified against each retry initialization. Selection can in principle move to another existing structure; actual changes are reported. These are continuations, not independent random starts.'))
print(summary)
