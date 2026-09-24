"""Frozen p0 detection at every new confirmation coordinate, all preparation methods."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_reference_scopes import scopes
from annni.stage6_observation_analysis import predict,label_status
from annni.stage6_wall_features import pure_features
from annni.upgrade_gates import observations,vector
assert (OUT/'confirmation/confirmation_unsealed.json').exists()
preps=json.loads((OUT/'confirmation/confirmation_paired_summary.json').read_text())['rows'];refs={(r['kappa'],r['h']):r for r in json.loads((OUT/'reference_atlas/confirmation_evaluation.json').read_text())};rows=[]
for r in preps:
 reference=refs[(r['kappa'],r['h'])];scope=scopes(reference['label'],reference['level'],reference);state=np.load(ROOT/r['source'])['state'];v=vector(observations(state,r['n']));pred=predict(v,r['n'],pure_features(state,r['n']));rows.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],method=r['method'],region=r['region'],state_pass=r['state_pass'],observable_pass=r['observable_pass'],joint_pass=r['joint_pass'],reference_scope=scope,predictions=pred,physical_status={d:label_status(y,scope['physical_label']) for d,y in pred.items()},RN_proxy_status={d:label_status(y,scope['RN_proxy_label']) for d,y in pred.items()},source=r['source']))
summary=[]
for method in sorted({r['method'] for r in rows}):
 for region in ['all']+sorted({r['region'] for r in rows}):
  subset=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)]
  for detector in ['D1','D3','D4','D5']:
   summary.append(dict(method=method,region=region,detector=detector,coordinates=len(subset),physical_counts=dict(collections.Counter(r['physical_status'][detector] for r in subset)),RN_proxy_counts=dict(collections.Counter(r['RN_proxy_status'][detector] for r in subset)),state_fail_but_physical_label_correct=sum(not r['state_pass'] and r['physical_status'][detector]=='correct' for r in subset),state_pass_but_physical_label_wrong_or_rejected=sum(r['state_pass'] and r['physical_status'][detector] in ['wrong_accepted','rejected'] for r in subset)))
dump(OUT/'confirmation/frozen_detection_p0.json',dict(rows=rows,summary=summary,scope='All96new coordinates, no reference-dependent preparation or detector retuning. Physical-interior labels and RN proxies separately counted. Exact p0 expectations; no finite measurement cost implied.'))
print('p0 detector rows',len(rows))
