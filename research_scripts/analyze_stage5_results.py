"""Read-only statistics from completed indices; never manufactures missing results."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump,sha
import numpy as np
from annni.upgrade_detection import predict
O=OUT/'submission';O.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text()) if p.exists() else []
def quantile(v):return np.quantile(v,[0,.25,.5,.75,1]).tolist() if len(v) else []
def csvwrite(path,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r));path.parent.mkdir(exist_ok=True)
 with path.open('w') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
selection=[];failure=[]
for task in ['map','test','n12test','n12_192','windows']:
 rows=read(OUT/f'selector_benchmark/{task}/index.json')
 if not rows:continue
 for rule in ['S0','S1','S2','B5']:
  cc=[r['B5_selection']['candidate'] if rule=='B5' else r['selectors'][rule]['candidate'] for r in rows];selection.append(dict(task=task,rule=rule,n=rows[0]['n'],total=len(rows),joint_pass=sum(c['joint_pass'] for c in cc),observable_pass=sum(c['observable_pass'] for c in cc),state_pass=sum(c['state_pass'] for c in cc),cnots_quantiles=quantile([c['cnots'] for c in cc]),fidelity_quantiles=quantile([c['fidelity'] for c in cc]),delta_e_quantiles=quantile([c['delta_e'] for c in cc]),optimizer_success=sum(bool(c.get('optimizer_success')) and (c.get('reason')!='reference' or bool(c.get('initial_source'))) for c in cc),reference_selections=sum(c.get('reason')=='reference' and not c.get('initial_source') for c in cc),raw_checkpoint_success_flags=sum(bool(c.get('optimizer_success')) for c in cc),selection_unresolved=sum((r['B5_selection'] if rule=='B5' else r['selectors'][rule]).get('selection_unresolved',False) for r in rows),candidate_available=sum(r['oracle'] is not None for r in rows),reoptimization_triggered=sum(r['reoptimization']['triggered'] for r in rows)))
 for r in rows:
  c=r['B5_selection']['candidate']
  if not c['joint_pass']:failure.append(dict(task=task,n=r['n'],kappa=r['kappa'],h=r['h'],cnots=c['cnots'],delta_e=c['delta_e'],epsilon_c=c['epsilon_c'],epsilon_sf=c['epsilon_sf'],epsilon_mx=c['epsilon_mx'],fidelity=c['fidelity'],w0=c['w0'],variance=c['variance'],category=r['failure_category'],source_stop=c.get('source_stop'),unresolved=r['B5_selection']['selection_unresolved']))
csvwrite(O/'selection.csv',selection);csvwrite(O/'failures.csv',failure)
core=read(OUT/'end_to_end/core_index.json');stats=[];risk=[];curves=[]
for method in sorted({e['arm'] for r in core for e in r['entries']}):
 for p in [0,.01,.05]:
  records=[e['record'] for r in core for e in r['entries'] if e['arm']==method and e['record']['p']==p]
  if not records:continue
  for budget in ['10000','100000']:
   for detector in ['D1','D3']:
    anchors=[r for r in records if r['anchor'] is not None];pred=[x for r in anchors for x in r['statistics'][budget][detector]];truth=[r['anchor'] for r in anchors for _ in range(32)];accepted=np.array([x not in ['degraded','uncertain'] for x in pred]);correct=np.array([x==y for x,y in zip(pred,truth)]);wrong=accepted&~correct;allpred=[x for r in records for x in r['statistics'][budget][detector]];ag=[x==r['ED_diagnostic'][detector] for r in records for x in r['statistics'][budget][detector]]
    stats.append(dict(method=method,p=p,shots=int(budget),detector=detector,coordinates=len(records),anchor_coordinates=len(anchors),anchor_trials=len(pred),anchor_correct=int(correct.sum()),anchor_wrong=int(wrong.sum()),anchor_rejected=int((~accepted).sum()),anchor_correct_rate=float(correct.mean()) if len(correct) else None,anchor_wrong_rate=float(wrong.mean()) if len(wrong) else None,accepted_conditional_error=float(wrong.sum()/accepted.sum()) if accepted.sum() else None,anchor_coverage=float(accepted.mean()) if len(accepted) else None,all_coverage=float(np.mean([x not in ['degraded','uncertain'] for x in allpred])),ED_diagnostic_agreement=float(np.mean(ag)),mse_ED=float(np.mean([r['statistics'][budget]['mse_ED'] for r in records])),mse_own_clean=float(np.mean([r['statistics'][budget]['mse_own_clean'] for r in records])),gate_shots_quantiles=quantile([r['cost'][budget]['gate_shots'] for r in records]),scope='Fixed coordinate design; 32 repeated measurement trials, not independent parameter-population samples'))
    # Risk-coverage: abstain further from the frozen classifier; no threshold retuning.
    ranked=[]
    cfg=read(ROOT/'results/stage4_upgrade_v1/detection/frozen.json')
    for r in anchors:
     a=np.load(ROOT/r['archive']);samples=a['samples_'+budget]
     for v,label in zip(samples,r['statistics'][budget][detector]):
      if label in ['degraded','uncertain']:continue
      d=predict(v,cfg)[detector+'_distances'];ranked.append((float(min(d)),label!=r['anchor']))
    ranked.sort()
    for fraction in [0,.25,.5,.75,1]:
     count=round(fraction*len(ranked));risk.append(dict(method=method,p=p,shots=int(budget),detector=detector,accepted=count,denominator=len(pred),coverage=count/len(pred) if pred else 0,risk=float(np.mean([x[1] for x in ranked[:count]])) if count else None,scope='Additional abstention on frozen distance rank; no optimized operating point'))
csvwrite(O/'end_to_end.csv',stats);csvwrite(O/'risk_coverage.csv',risk)
# Matched differences on same coordinates and same total budget. Distinct physical keys have independent streams; identical cached arm keys share counts, as recorded in measurement_randomization_clarification.json.
paired=[]
for p in [.01,.05]:
 for baseline in ['B0_raw','B3_raw']:
  for method in ['B3_raw','B5_raw','B5_zne','B5_sv']:
   if baseline==method:continue
   deltas=[];common=[]
   for point in core:
    ee={e['arm']:e['record'] for e in point['entries'] if e['record']['p']==p}
    if baseline not in ee or method not in ee:continue
    d=float(np.mean(ee[method]['statistics']['100000']['mse_ED'])-np.mean(ee[baseline]['statistics']['100000']['mse_ED']));deltas.append(d)
    if ee[method]['prep_pass'] and ee[baseline]['prep_pass']:common.append(d)
   paired.append(dict(p=p,baseline=baseline,method=method,denominator=len(deltas),mean_MSE_difference=float(np.mean(deltas)) if deltas else None,quantiles=quantile(deltas),win_fraction=float(np.mean(np.array(deltas)<0)) if deltas else None,common_prep_pass_count=len(common),common_prep_pass_mean_difference=float(np.mean(common)) if common else None,common_prep_pass_win_fraction=float(np.mean(np.array(common)<0)) if common else None))
csvwrite(O/'paired.csv',paired)
dump(O/'statistics.json',dict(selection=selection,end_to_end=stats,paired=paired,available_core_points=len(core),historical_audit=read(OUT/'selection_audit/summary.json'),mitigation_freeze=read(OUT/'end_to_end/mitigation_frozen.json'),floating=read(OUT/'floating_validation/evidence_update.json'),dynamics=read(OUT/'dynamics_validation/analysis.json')));print('Statistics:',len(selection),len(core),'core points')
