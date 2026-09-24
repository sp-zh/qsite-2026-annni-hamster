import sys,argparse,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_observation_analysis import *
from annni.stage6_io import measurement_rows
from annni.stage6_wall_features import pure_features
from annni.stage6_reference_scopes import scopes
parser=argparse.ArgumentParser();parser.add_argument('--task',default='core');args=parser.parse_args();task=args.task
rows=[];labels={}
for p in (OUT/'reference_atlas').glob('*_evaluation.json'):
 for r in json.loads(p.read_text()):labels[(r['kappa'],r['h'])]=r
for batch in [measurement_rows((OUT/'end_to_end').glob(task+'_*_index.json'))]:
 expected={'confirmation':96,'core':48,'validation':24,'windows':51,'n12':12}[task]
 assert len(batch)==expected,('Incomplete measurement cohort: do not publish as a full analysis',task,len(batch),expected)
 for point in batch:
  n,k,h=point['n'],point['kappa'],point['h'];ed=ed_measurements(n,k,h);ea=np.load(ROOT/ed['archive']);target=ea['exact'];ref=record(n,k,h);label=labels.get((k,h),{}).get('label');level=labels.get((k,h),{}).get('level')
  if not level:label,level,_=physical_reference(n,k,h,None,ref,ref['binder'])
  scope=scopes(label,level,labels.get((k,h)));proxy=scope['RN_proxy_label'];label=scope['physical_label'];level=scope['physical_level'];edpred=predict(target,n,ea['wall_exact']);ideal=[]
  for b in PLAN['measurement']['budgets']:
   for rep,(v,w) in enumerate(zip(ea[f'samples_{b}'],ea[f'wall_{b}'])):
    preds=predict(v,n,w);ideal.append(dict(budget=b,repeat=rep,predictions=preds,reference_status={d:label_status(y,label) for d,y in preds.items()},RN_proxy_status={d:label_status(y,proxy) for d,y in preds.items()},**scores(v,target,n)))
  entries=[]
  for entry in point['entries']:
   r=entry['record'];a=np.load(ROOT/r['archive']);exact=a['exact'];own=a['own_clean'];wp=wall_estimates(r);ep=predict(exact,n,wp);source=next(x['archive'] for x in point['sources'] if x['method']==entry['method']);cleanstate=np.load(ROOT/source)['state'];cleanpred=predict(own,n,pure_features(cleanstate,n));samples=[]
   for b in PLAN['measurement']['budgets']:
    ws=wall_estimates(r,b)
    for rep,v in enumerate(a[f'samples_{b}']):
     preds=predict(v,n,None if ws is None else ws[rep]);samples.append(dict(budget=b,repeat=rep,predictions=preds,reference_status={d:label_status(y,label) for d,y in preds.items()},RN_proxy_status={d:label_status(y,proxy) for d,y in preds.items()},error_ED=scores(v,target,n),error_own_p0=scores(v,own,n),measurement_error=scores(v,exact,n)))
   # Attribution is task-specific, not a state-fidelity mask.
   attribution={}
   for d,y in ep.items():
    if y=='unmeasured':tag='measurement_not_available_for_this_estimator'
    elif label is None:tag='reference_unresolved_for_discrete_label'
    elif edpred[d]!=label:tag='detector_limited_on_perfect_ED'
    elif cleanpred[d]!=label:tag='preparation_limited_for_this_detector'
    elif y!=label:tag='noise_or_detector_limited_requires_distribution_evidence'
    else:tag='exact_task_label_reconstructed'
    attribution[d]=tag
   proxy_attribution={}
   for d,y in ep.items():
    if y=='unmeasured':tag='measurement_not_available_for_this_estimator'
    elif proxy is None:tag='RN_discrete_pattern_unresolved_use_continuous_curves'
    elif edpred[d]!=proxy:tag='detector_limited_on_perfect_ED_RN_pattern'
    elif cleanpred[d]!=proxy:tag='preparation_limited_for_RN_detector'
    elif y!=proxy:tag='noise_or_detector_limited_RN_pattern'
    else:tag='exact_RN_pattern_reconstructed'
    proxy_attribution[d]=tag
   entries.append(dict(method=entry['method'],estimator=entry['estimator'],p=r['p'],archive=r['archive'],exact_predictions=ep,RN_proxy_exact_status={d:label_status(y,proxy) for d,y in ep.items()},own_p0_predictions=cleanpred,exact_error_ED=scores(exact,target,n),exact_error_own_p0=scores(exact,own,n),prep_error=scores(own,target,n),attribution=attribution,RN_proxy_attribution=proxy_attribution,samples=samples,cost=r['cost'],quality=r['quality']))
  rows.append(dict(n=n,kappa=k,h=h,reference_label=label,reference_level=level,RN_proxy_label=proxy,reference_scope=scope,reference_ambiguous=ref['reference_numerical_ambiguous'],ed_archive=ed['archive'],ed_exact_predictions=edpred,ed_shots=ideal,entries=entries));dump(OUT/f'end_to_end/{task}_analysis.json',rows)
 print('analyzed',task,len(rows),flush=True)
summary={}
for method,estimator,p in sorted(set((e['method'],e['estimator'],e['p']) for r in rows for e in r['entries'])):
 for b in PLAN['measurement']['budgets']:
  es=[e for r in rows for e in r['entries'] if (e['method'],e['estimator'],e['p'])==(method,estimator,p)];stats={};ss=[s for e in es for s in e['samples'] if s['budget']==b]
  for detector in ['D1','D3','D4','D5']:stats[detector]=dict(physical_label=dict(collections.Counter(s['reference_status'][detector] for s in ss)),RN_proxy=dict(collections.Counter(s['RN_proxy_status'][detector] for s in ss)))
  summary[f'{method}_{estimator}_p{p}_{b}']=dict(physical_coordinates=len(es),measurement_repeats=len(ss),MSE_ED_mean=float(np.mean([s['error_ED']['mse'] for s in ss])),MSE_own_p0_mean=float(np.mean([s['error_own_p0']['mse'] for s in ss])),label_repeat_counts=stats,total_shots=sum(e['cost'][str(b)]['all_reps_shots'] for e in es),total_gate_shots=sum(32*e['cost'][str(b)]['gate_shots_per_rep'] for e in es))
dump(OUT/f'end_to_end/{task}_summary.json',summary)
