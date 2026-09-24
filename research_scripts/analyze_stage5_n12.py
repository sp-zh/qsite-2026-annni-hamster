"""Paired candidate, quantum-cap and same-gate-retry contrasts; all coordinates retained."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump,np
from annni.stage5_baseline_selectors import choose
O=OUT/'n12_scaling'
cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector']
old=json.loads((OUT/'selector_benchmark/audit/index.json').read_text())
test=json.loads((OUT/'selector_benchmark/n12test/index.json').read_text())
large=json.loads((OUT/'selector_benchmark/n12_192/index.json').read_text())
pairs=[];prefixes=[]
def quant(v):return np.quantile(v,[0,.25,.5,.75,1]).tolist() if len(v) else []
for r in large:
 small=next(a for a in old+test if a['n']==12 and abs(a['kappa']-r['kappa'])<1e-10 and abs(a['h']-r['h'])<1e-10)
 ss={rule:choose(small['candidates'],rule,cfg)['candidate'] for rule in ['S0','S1','S2']}
 ll=r['B5_selection']['candidate']
 source_rows={}
 for name,point in [('cap128',small),('cap192',r)]:
  sources={c['source'] for c in point['candidates']}
  runs=[json.loads((ROOT/path).read_text()) for path in sorted(sources)]
  source_rows[name]=runs
 pairs.append(dict(kappa=r['kappa'],h=r['h'],cohort='new_test24' if small['group']=='n12test' else 'old_descriptive60',small=ss,large=ll,large_fixed=r['selectors']['S2']['candidate'],reoptimization=r['reoptimization'],small_qualified_candidate=small['oracle'] is not None,large_qualified_candidate=r['oracle'] is not None,small_source_stops=[x['stop'] for x in source_rows['cap128']],large_source_stops=[x['stop'] for x in source_rows['cap192']],small_search_cnots_max=max(c['cnots'] for c in small['candidates']),large_search_cnots_max=max(c['cnots'] for c in r['candidates']),small_adaptive_function_calls=sum(x['nfev'] for x in source_rows['cap128']),large_adaptive_function_calls=sum(x['nfev'] for x in source_rows['cap192']),paired_cold_seed=11,independent_extra_restart=False,extension_protocol='Cold deterministic rerun at192, same reference/seed and per-optimization limits; actual shared prefixes audited separately. Extra cap also allows extra adaptive classical search.'))
 for a in source_rows['cap128']:
  b=next(b for b in source_rows['cap192'] if a['ref']==b['ref'] and a['seed']==b['seed']);prefix=0
  for x,y in zip(a['steps'],b['steps']):
   if x.get('word')!=y.get('word') or len(x['params'])!=len(y['params']) or not np.allclose(x['params'],y['params'],atol=1e-8,rtol=1e-8):break
   prefix+=1
  prefixes.append(dict(kappa=r['kappa'],h=r['h'],ref=a['ref'],seed=a['seed'],matching_prefix_steps=prefix,steps128=len(a['steps']),steps192=len(b['steps']),same_entire128_prefix=prefix==len(a['steps']),tolerance='params atol=rtol=1e-8 plus exact Pauli word; budget eligibility may diverge near128 cap',source128=a['archive'],source192=b['archive']))
summary=[];paired=[]
def candidate(r,label):return r['large'] if label=='B5_192' else r['large_fixed'] if label=='S2_192' else r['small'][label]
for group in ['old_descriptive60','new_test24']:
 rr=[r for r in pairs if r['cohort']==group]
 for label in ['S0','S1','S2','S2_192','B5_192']:
  cc=[candidate(r,label) for r in rr]
  summary.append(dict(cohort=group,method=label,total=len(cc),passed=sum(c['joint_pass'] for c in cc),observable_pass=sum(c['observable_pass'] for c in cc),state_pass=sum(c['state_pass'] for c in cc),optimizer_success=sum(bool(c.get('optimizer_success')) and (c.get('reason')!='reference' or bool(c.get('initial_source'))) for c in cc),reference_selections=sum(c.get('reason')=='reference' and not c.get('initial_source') for c in cc),raw_checkpoint_success_flags=sum(bool(c.get('optimizer_success')) for c in cc),median_cnots=float(np.median([c['cnots'] for c in cc])),cnots_quantiles=quant([c['cnots'] for c in cc]),energy_error_quantiles=quant([c['delta_e'] for c in cc]),fidelity_quantiles=quant([c['fidelity'] for c in cc]),selected_near_cap_count=sum(c['cnots']>= (191 if label in ['S2_192','B5_192'] else 127) for c in cc),cap_warning='Selected cost near cap is not proof every failure is resource limited; per-point candidate availability, maximum searched gates and actual source stops are separate.'))
 for before,after,interpretation in [('S0','S2','fixed128 candidate selection only'),('S2','S2_192','larger quantum cap plus longer adaptive search; not a pure gate-count causal effect'),('S2_192','B5_192','bounded energy-only retry keeps its initialization structure; selected-structure and selected-CNOT changes are reported separately')]:
  aa=[candidate(r,before) for r in rr];bb=[candidate(r,after) for r in rr]
  paired.append(dict(cohort=group,before=before,after=after,total=len(rr),gained_joint=sum(not a['joint_pass'] and b['joint_pass'] for a,b in zip(aa,bb)),lost_joint=sum(a['joint_pass'] and not b['joint_pass'] for a,b in zip(aa,bb)),maxC_error_difference_quantiles=quant([b['epsilon_c']-a['epsilon_c'] for a,b in zip(aa,bb)]),energy_error_difference_quantiles=quant([b['delta_e']-a['delta_e'] for a,b in zip(aa,bb)]),maxC_improved_fraction=float(np.mean([b['epsilon_c']<a['epsilon_c'] for a,b in zip(aa,bb)])),selected_structure_changes=sum((a['ref'],a['words'])!=(b['ref'],b['words']) for a,b in zip(aa,bb)),selected_cnot_difference_quantiles=quant([b['cnots']-a['cnots'] for a,b in zip(aa,bb)]),interpretation=interpretation))
noise=[];noise_paired=[];nr=json.loads((O/'noise_index.json').read_text()) if (O/'noise_index.json').exists() else []
for p in [0,.01,.05]:
 for arm in ['S0_128','S1_128','S2_128','S2_192','B5_192']:
  values=[e['record']['epsilon_c_total'] for r in nr for e in r['entries'] if e['arm']==arm and e['record']['p']==p]
  if values:noise.append(dict(p=p,arm=arm,count=len(values),mean=float(np.mean(values)),quantiles=quant(values)))
 for before,after in [('S0_128','S2_128'),('S2_128','S2_192'),('S2_192','B5_192')]:
  ds=[]
  for r in nr:
   by={e['arm']:e['record'] for e in r['entries'] if e['record']['p']==p}
   if before in by and after in by:ds.append(by[after]['epsilon_c_total']-by[before]['epsilon_c_total'])
  if ds:noise_paired.append(dict(p=p,before=before,after=after,total=len(ds),mean_difference=float(np.mean(ds)),quantiles=quant(ds),improved_fraction=float(np.mean(np.array(ds)<0))))
mitigation=[];path=OUT/'end_to_end/n12_index.json'
if path.exists():
 for p in [0,.01,.05]:
  for method in ['raw','sv']:
   records=[e['record'] for row in json.loads(path.read_text()) for e in row['entries'] if e['record']['p']==p and e['record']['method']==method]
   for budget in ['10000','100000']:
    if records:
     anchor_records=[r for r in records if r['anchor'] is not None];anchor_labels=[(x,r['anchor']) for r in anchor_records for x in r['statistics'][budget]['D1']]
     mitigation.append(dict(p=p,method=method,shots=int(budget),coordinates=len(records),settings=sorted(set(r['cost'][budget]['measurement_settings'] for r in records)),MSE_own_clean=float(np.mean([r['statistics'][budget]['mse_own_clean'] for r in records])),MSE_ED=float(np.mean([r['statistics'][budget]['mse_ED'] for r in records])),gate_shots_quantiles=quant([r['cost'][budget]['gate_shots'] for r in records]),D1_accepted=sum(x not in ['uncertain','degraded'] for r in records for x in r['statistics'][budget]['D1']),measurement_trials=32*len(records),anchor_coordinates=len(anchor_records),anchor_trials=len(anchor_labels),anchor_correct=sum(x==y for x,y in anchor_labels),anchor_wrong=sum(x not in ['uncertain','degraded'] and x!=y for x,y in anchor_labels),anchor_rejected=sum(x in ['uncertain','degraded'] for x,y in anchor_labels),scope='Coverage is not accuracy on these predominantly unlabelled finite-size points.'))
# Both frozen observable detectors are evaluated on the same N12 samples.
if path.exists():
 for item in mitigation:
  records=[e['record'] for row in json.loads(path.read_text()) for e in row['entries'] if e['record']['p']==item['p'] and e['record']['method']==item['method']]
  b=str(item['shots']);labels=[(x,r['anchor']) for r in records if r['anchor'] is not None for x in r['statistics'][b]['D3']]
  item['D3_accepted']=sum(x not in ['uncertain','degraded'] for r in records for x in r['statistics'][b]['D3'])
  item['D3_anchor_correct']=sum(x==y for x,y in labels)
  item['D3_anchor_wrong']=sum(x not in ['uncertain','degraded'] and x!=y for x,y in labels)
  item['D3_anchor_rejected']=sum(x in ['uncertain','degraded'] for x,y in labels)
failures=[]
for point in pairs:
 if point['large']['joint_pass']:continue
 c=point['large'];failures.append(dict(cohort=point['cohort'],kappa=point['kappa'],h=point['h'],selected_cnots=c['cnots'],maximum_searched_cnots=point['large_search_cnots_max'],passing_candidate_exists=point['large_qualified_candidate'],all_reference_stops=point['large_source_stops'],delta_e=c['delta_e'],epsilon_c=c['epsilon_c'],epsilon_sf=c['epsilon_sf'],epsilon_mx=c['epsilon_mx'],fidelity=c['fidelity'],optimizer_success=c['optimizer_success'],interpretation='No qualifying saved candidate and all references reached budget' if not point['large_qualified_candidate'] and all(x=='budget' for x in point['large_source_stops']) else 'See candidate and optimizer records; unresolved cause',caveat='Budget exhaustion does not distinguish expressivity from imperfect optimization or certify a higher cap will solve the point.'))
dump(O/'failure_details.json',failures)
dump(O/'prefix_audit.json',dict(rows=prefixes,exact_entire_prefix_count=sum(r['same_entire128_prefix'] for r in prefixes),total=len(prefixes)))
dump(O/'analysis.json',dict(pairs=pairs,summary=summary,paired_effects=paired,noise=noise,noise_paired=noise_paired,mitigation=mitigation,interpretation='Same-coordinate resource contrast with fixed tolerances; no extrapolation to entire N12 noisy map'));print(summary)
