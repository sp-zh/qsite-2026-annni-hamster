"""Coordinate/region-level denominators and six-level detection outcomes."""
import sys,argparse,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_observation_analysis import label_status
parser=argparse.ArgumentParser();parser.add_argument('--task',default='core');task=parser.parse_args().task;data=json.loads((OUT/f'end_to_end/{task}_analysis.json').read_text());rows=[]
def memberships(r):
 k,h=r['kappa'],r['h'];out=['all']
 if .4-1e-12<=k<=.6+1e-12 and .01<=h<=.35+1e-12:out.append('low_field')
 if .6<=k<=1 and .2<=h<=.7:out.append('antiphase_transition_band')
 if r['reference_label'] is not None:out.append('independently_supported_interiors')
 return out
for r in data:
 regions=memberships(r);label=r['reference_label']
 for detector,y in r['ed_exact_predictions'].items():
  rows.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,reference_label=label,reference_level=r['reference_level'],method='ED_ideal_information',estimator='exact',p=0,budget=None,detector=detector,layer=1,reference_status=label_status(y,label),correct_fraction=float(y==label) if label else None,repeat_count=0))
  for budget in PLAN['measurement']['budgets']:
   ss=[x for x in r['ed_shots'] if x['budget']==budget];statuses=collections.Counter(x['reference_status'][detector] for x in ss);rows.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,reference_label=label,reference_level=r['reference_level'],method='ED_ideal_information',estimator='shots',p=0,budget=budget,detector=detector,layer=2,reference_status_counts=dict(statuses),correct_fraction=sum(x['predictions'][detector]==label for x in ss)/len(ss) if label else None,repeat_count=len(ss)))
 for e in r['entries']:
  for detector,y in e['exact_predictions'].items():
   rows.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,reference_label=label,reference_level=r['reference_level'],method=e['method'],estimator=e['estimator'],p=e['p'],budget=None,detector=detector,layer=3 if e['p']==0 else 4,reference_status=label_status(y,label),correct_fraction=float(y==label) if label else None,repeat_count=0,attribution=e['attribution'][detector],MSE_ED=e['exact_error_ED']['mse'],MSE_own_p0=e['exact_error_own_p0']['mse']))
   for budget in PLAN['measurement']['budgets']:
    ss=[x for x in e['samples'] if x['budget']==budget];statuses=collections.Counter(x['reference_status'][detector] for x in ss);correct=sum(x['predictions'][detector]==label for x in ss)/len(ss) if label else None;rows.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,reference_label=label,reference_level=r['reference_level'],method=e['method'],estimator=e['estimator'],p=e['p'],budget=budget,detector=detector,layer=5 if e['estimator']=='raw' else 6,reference_status_counts=dict(statuses),correct_fraction=correct,repeat_count=len(ss),MSE_ED=float(np.mean([x['error_ED']['mse'] for x in ss])),MSE_own_p0=float(np.mean([x['error_own_p0']['mse'] for x in ss])),measurement_MSE=float(np.mean([x['measurement_error']['mse'] for x in ss])),attribution='measurement_limited_for_this_detector' if label is not None and y==label and correct<.5 else e['attribution'][detector]))
summary=[]
for region in ['all','low_field','antiphase_transition_band','independently_supported_interiors']:
 selected=[r for r in rows if region in r['regions']];groups={}
 for r in selected:groups.setdefault((r['method'],r['estimator'],r['p'],r['budget'],r['detector'],r['layer']),[]).append(r)
 for key,group in groups.items():
  labelled=[r for r in group if r['reference_label'] is not None];stats=collections.Counter()
  for r in group:
   if r['repeat_count']:
    for status,count in r['reference_status_counts'].items():stats[status]+=count/r['repeat_count']
   else:stats[r['reference_status']]+=1
  summary.append(dict(region=region,method=key[0],estimator=key[1],p=key[2],budget=key[3],detector=key[4],layer=key[5],physical_coordinates=len(group),reference_labelled_coordinates=len(labelled),reference_label_coverage=len(labelled)/len(group),reference_level_counts=dict(collections.Counter(r['reference_level'] for r in group)),macro_phase_correct_fraction=float(np.mean([np.mean([r['correct_fraction'] for r in labelled if r['reference_label']==phase]) for phase in sorted({r['reference_label'] for r in labelled})])) if labelled else None,mean_correct_fraction_given_label=float(np.mean([r['correct_fraction'] for r in labelled])) if labelled else None,coordinate_weighted_outcome_counts=dict(stats),total_measurement_repetitions=sum(r['repeat_count'] for r in group),MSE_ED_mean=float(np.mean([r['MSE_ED'] for r in group])) if 'MSE_ED' in group[0] else None,attribution_counts=dict(collections.Counter(r.get('attribution','ideal_information_reference') for r in group))))
dump(OUT/f'end_to_end/{task}_regional_ladder.json',dict(rows=rows,summary=summary,region_scope='Fixed low rectangle [.4,.6]x[.01,.35], AP-band [.6,1]x[.2,.7], and independently supported labelled interiors. Interiors can overlap rectangles; region summaries are not summed. All coordinates retained; repeats normalized within coordinate. Missing labels give no accuracy.',noise_information_scope='No classifier rejection alone establishes information loss. Pair trace-distance/known-template evidence is in noise_diagnosability; binary template success is not full phase accuracy.',measurement_limited_rule='Perfect expectation label correct, but <50% of32 repeats correct at the stated total budget; descriptive repeated-measurement failure, not a new deployed detector.'))
print(task,len(data),'coordinates',len(summary),'regional layer rows')
