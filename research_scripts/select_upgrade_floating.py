import json,numpy as np
from pathlib import Path
O=Path('results/stage4_upgrade_v1/floating');rows=json.loads((O/'coarse_index.json').read_text());candidates=[];centers=[];points=[]
for k in [.6,.8,1.]:
 a=[r for r in rows if r['kappa']==k];scores=[]
 for r in a:
  power=r['fit_raw'][0];exponential=r['fit_raw'][1];c=r['entropy_fits'][-1]['c'];q=power['q']
  score=np.clip(c,0,1.5)+.25*np.tanh((exponential['aic']-power['aic'])/10)+.2*min(abs(q-np.pi/2)/.2,1)
  scores.append(dict(kappa=k,h=r['h'],score=float(score),c=c,q=q,power_minus_exp_aic=power['aic']-exponential['aic']))
 best=max([s for s in scores if .2<=s['h']<=1.1],key=lambda s:s['score']);centers.append([k,best['h']]);points += [[k,round(best['h']+delta,2)] for delta in [-.1,0,.1]];candidates+=scores
x=dict(frozen_before_refinement=True,selection='coarse OBC entropy coefficient, fitted incommensurability and power/exponential AIC; no literature formula selection',scores=candidates,centers=centers,points=points,evidence_grade='candidate selection only')
(O/'candidate_windows.json').write_text(json.dumps(x,indent=2));print(centers)
