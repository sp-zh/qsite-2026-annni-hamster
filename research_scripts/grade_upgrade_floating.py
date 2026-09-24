import json,numpy as np
from pathlib import Path
O=Path(__file__).resolve().parents[1]/'results/stage4_upgrade_v1/floating';a=json.loads((O/'refine_index.json').read_text());rows=[]
for k,h in json.loads((O/'candidate_windows.json').read_text())['points']:
 group=[r for r in a if r['kappa']==k and r['h']==h and r['init']=='plus'];checks=[];chosen=[]
 for n in [64,96]:
  r=sorted([r for r in group if r['n']==n],key=lambda x:x['chi_max']);low,hi=r[-2:];x=np.load(O.parents[2]/low['archive']);y=np.load(O.parents[2]/hi['archive'])
  checks.append(dict(n=n,chi_low=low['chi_max'],chi_high=hi['chi_max'],delta_energy_per_site=abs(low['energy']-hi['energy'])/n,delta_correlation=float(np.max(abs(x['central_raw']-y['central_raw']))),delta_entropy=float(np.max(abs(x['entropy']-y['entropy'])))))
  chosen.append(hi)
 converged=all(c['delta_energy_per_site']<1e-5 and c['delta_correlation']<.01 and c['delta_entropy']<.03 for c in checks)
 cs=[e['c'] for r in chosen for e in r['entropy_fits']];central=all(.75<c<1.25 for c in cs)
 q=[r['fit_raw'][0]['q'] for r in chosen];incomm=all(abs(v-np.pi/2)>.02 for v in q) and abs(q[0]-q[1])<.1
 power=all(r['fit_raw'][j]['aic']+2<r['fit_raw'][j+1]['aic'] for r in chosen for j in [0,2])
 connected=all(r['fit_connected'][j]['aic']+2<r['fit_connected'][j+1]['aic'] for r in chosen for j in [0,2])
 initchecks=[];initdetails=[]
 for r in chosen:
  alt=[s for s in a if s['n']==r['n'] and s['kappa']==k and s['h']==h and s['chi_max']==r['chi_max'] and s['init']=='antiphase']
  if alt:
   aa=np.load(O.parents[2]/alt[0]['archive']);bb=np.load(O.parents[2]/r['archive']);de=abs(alt[0]['energy']-r['energy'])/r['n'];dc=float(np.max(abs(aa['central_raw']-bb['central_raw'])));ds=float(np.max(abs(aa['entropy']-bb['entropy'])));initchecks.append(de<1e-5 and dc<.01 and ds<.03);initdetails.append(dict(n=r['n'],delta_energy_per_site=de,delta_correlation=dc,delta_entropy=ds))
 initgood=len(initchecks)==2 and all(initchecks)
 supported=converged and central and incomm and power and connected and initgood
 rows.append(dict(kappa=k,h=h,evidence_grade='supported_in_tested_window' if supported else 'candidate' if central or incomm else 'not_resolved',criteria=dict(bond_converged=converged,entropy_windows_near_c1=central,incommensurate_size_stable=incomm,power_aic_preferred_both_windows=power,connected_power_preferred=connected,independent_initializations_available_and_agree=initgood),checks=checks,initialization_checks=initdetails,entropy_c=cs,q=q,claim='Finite OBC numerical evidence; not a phase boundary or a small-N noisy label'))
(O/'evidence_grading.json').write_text(json.dumps(dict(criteria_declared='post-computation transparent evidence review, not training or tuning selection; thresholds solely govern conservative wording',rows=rows),indent=2));print(json.dumps(rows,indent=2))
