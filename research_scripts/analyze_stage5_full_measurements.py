"""Frozen-anchor descriptive full-map raw/ZNE comparison, no detector changes."""
import json,sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump,np
rows=[];paired=[]
indices={name:json.loads((OUT/'end_to_end'/file).read_text()) for name,file in [('B5_raw','full_raw_index.json'),('B5_zne','full_best_index.json')]}
for name,points in indices.items():
 assert len(points)==420
 for p in [0,.01,.05]:
  rec=[e['record'] for point in points for e in point['entries'] if e['record']['p']==p]
  for budget in ['10000','100000']:
   for detector in ['D1','D3']:
    anchors=[r for r in rec if r['anchor'] is not None];lab=[l for r in anchors for l in r['statistics'][budget][detector]];truth=[r['anchor'] for r in anchors for _ in range(32)];accepted=np.array([l not in ['uncertain','degraded'] for l in lab]);correct=np.array([l==t for l,t in zip(lab,truth)]);wrong=accepted&~correct
    rows.append(dict(method=name,p=p,shots=int(budget),detector=detector,coordinates=420,anchor_coordinates=len(anchors),anchor_trials=len(lab),correct=int(correct.sum()),wrong=int(wrong.sum()),rejected=int((~accepted).sum()),coverage=float(accepted.mean()),conditional_error=float(wrong.sum()/accepted.sum()) if accepted.sum() else None,all_diagnostic_coverage=float(np.mean([l not in ['uncertain','degraded'] for r in rec for l in r['statistics'][budget][detector]])),MSE_ED=float(np.mean([r['statistics'][budget]['mse_ED'] for r in rec])),MSE_own_clean=float(np.mean([r['statistics'][budget]['mse_own_clean'] for r in rec])),interpretation='Full old descriptive grid; same frozen physical anchor range/qualification as core, no newly tuned labels. All other points have no classification truth.'))
for p in [.01,.05]:
 for budget in ['10000','100000']:
  delta=[];common=[]
  for a,b in zip(indices['B5_raw'],indices['B5_zne']):
   assert (a['kappa'],a['h'])==(b['kappa'],b['h']);aa=next(e['record'] for e in a['entries'] if e['record']['p']==p);bb=next(e['record'] for e in b['entries'] if e['record']['p']==p);d=float(np.mean(bb['statistics'][budget]['mse_ED'])-np.mean(aa['statistics'][budget]['mse_ED']));delta.append(d)
   if aa['prep_pass'] and bb['prep_pass']:common.append(d)
  paired.append(dict(p=p,shots=int(budget),coordinates=len(delta),ZNE_minus_raw_ED_MSE_quantiles=np.quantile(delta,[0,.25,.5,.75,1]).tolist(),improved_fraction=float(np.mean(np.array(delta)<0)),common_prep_pass_count=len(common),common_prep_pass_mean_difference=float(np.mean(common))))
dump(OUT/'end_to_end/full_measurement_analysis.json',dict(rows=rows,paired=paired))
with (OUT/'submission/full_map_measurements.csv').open('w') as f:w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
print('Full-map finite-shot summaries:',len(rows))
