"""Frozen response scores plus separately labelled followup curve review."""
import sys,csv,collections,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
from annni.stage6_boundaries import compare
from annni.stage6_diagnostics import response_curves
from annni.upgrade_detection import controls

def csvout(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 if not rows:return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows])

def labels(vs,c):
 out=[];ctrl=controls(8)
 for v in vs:
  if not np.isfinite(v).all():out.append('uncertain');continue
  delta=v-ctrl;dist=np.sqrt((np.mean(delta[:,:8]**2,axis=1)+np.mean((2*delta[:,8:16])**2,axis=1)+delta[:,-1]**2)/3);order=np.argsort(dist);d1=int(order[0]) if dist[order[0]]<=c['d1_max_distance'] and dist[order[1]]-dist[order[0]]>=c['d1_margin'] else 4
  z=(v-np.array(c['mu']))/c['scale'];pc=z@np.array(c['components']).T;dd=np.linalg.norm(pc-np.array(c['centers']),axis=1);j=int(np.argmin(dd));d3=int(c['mapping'][j]) if dd[j]<=c['max_cluster_distance'] else 4
  if d1==3:d3=3
  out.append(c['labels'][d3])
 return out

def audit(comp,h,values,ed,rowpoints,k,p,branches):
 flags=[];y=np.asarray(comp['curve']);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';ey=response_curves(h,ed,8)[name]
 if comp['raw_maximum_endpoint']:flags.append('endpoint_dominated')
 if comp['result']['competing']:flags.append('competing_peaks')
 ratio=float(max(y)/max(ey)) if max(ey)>0 else None
 if ratio is not None and ratio<.1:flags.append('response_amplitude_below_10pct_ED')
 primary=comp['result']['primary'];near=[]
 if primary:
  pos=primary['coordinate'];step=max(np.diff(h));near=[i for i,x in enumerate(h) if abs(x-pos)<=1.51*step]
  if any(not rowpoints[i]['metrics']['observable_pass'] for i in near):flags.append('preparation_observable_failure_near_peak')
  close=[b for b in branches if b['kappa']==k and abs((b['left_h']+b['right_h'])/2-pos)<=1.51*step]
  if close and p>0:flags.append('nearby_branch_noise_effect_not_fully_checked')
 return dict(flags=flags,response_amplitude_ratio=ratio,reference_response_max=float(max(ey)),observed_response_max=float(max(y)),response_rmse=float(np.sqrt(np.mean((y-ey)**2))),all_preparation_joint_failures=sum(not r['metrics']['joint_pass'] for r in rowpoints),branch_switches_in_window=sum(b['kappa']==k for b in branches),quality_supports_position=bool(comp['reference_resolvable'] and comp['algorithm_estimatable'] and not flags))

def main():
 start=time.perf_counter();inputs=read(OUT/'inputs.json');refs=read(OUT/'window_reference.json');branches=[x for x in read(OUT/'branch_switches_historical.json') if x['method']=='B3'];det=read(OUT/'detector_frozen.json');records={};arrays={};source_sets={}
 for task in ['A','B']:
  path=OUT/f'{task}_index.json'
  if path.exists():
   for row in read(path):
    for rel in row['records']:
     r=read(ROOT/rel);key=(r['point_id'],r['p'],r['method'],r['mode'],r['budget']);records[key]=r;source_sets.setdefault(key,set()).add(task)
 rows=[];resource=[];perpoint={}
 reps={(r['kappa'],r['h']) for r in cfg()['representatives']}
 for key,r in records.items():
  a=np.load(ROOT/r['archive']);arrays[key]={k:a[k] for k in ['samples','exact','own_clean']};pt=inputs[r['point_id']];ed=data(pt)['ed'];v=a['samples'];diff=v-ed;own=v-a['own_clean'];pred=labels(v,det);lab=pt['label'];statuses=['unlabelled' if lab is None else 'rejected' if x in ['uncertain','degraded'] else 'correct' if x==lab else 'wrong_accepted' for x in pred];bias=a['exact']-ed;noise=v-a['exact'];roles=[]
  if (pt['kappa'],pt['h']) in reps:roles.append('representative')
  for w in refs:
   if pt['kappa']==w['kappa'] and pt['h'] in w['h']:roles.append('window_'+str(w['kappa']))
  out=dict(point_id=pt['id'],kappa=pt['kappa'],h=pt['h'],p=r['p'],method=r['method'],mode=r['mode'],budget=r['budget'],roles=roles,tasks=sorted(source_sets[key]),MSE_ED=float(np.mean(diff**2)),MSE_own_clean=float(np.mean(own**2)),MSE_C=float(np.mean(diff[:,:8]**2)),MSE_SF=float(np.mean(diff[:,8:16]**2)),MSE_Mx=float(np.mean(diff[:,-1]**2)),bias_squared=float(np.mean(bias**2)),sampling_MSE=float(np.mean(noise**2)),cross_term=float(2*np.mean(noise*bias)),MSE_repeats=np.mean(diff**2,axis=1).tolist(),labels_D3=pred,label_statuses=statuses,physical_label=lab,correct_fraction=statuses.count('correct')/32,wrong_accepted_fraction=statuses.count('wrong_accepted')/32,rejected_fraction=statuses.count('rejected')/32,reference_labelled=lab is not None,observable_pass=pt['metrics']['observable_pass'],state_pass=pt['metrics']['state_pass'],joint_pass=pt['metrics']['joint_pass'],shots_per_repeat=r['shots_per_repeat'],CNOT_shots_per_repeat=r['CNOT_shots_per_repeat'],one_qubit_gate_shots_per_repeat=r['one_qubit_gate_shots_per_repeat'],settings=r['measurement_settings'],disposition=r['disposition'],archive=r['archive'],zero_CNOT_control=r['zero_CNOT_control'])
  np.testing.assert_allclose(out['MSE_ED'],out['bias_squared']+out['sampling_MSE']+out['cross_term'],atol=1e-12)
  out['nonfinite_components']=int((~np.isfinite(v)).sum())
  out['sampling_variance_ddof1']=float(np.mean(np.var(v,axis=0,ddof=1)))
  out['empirical_sampling_bias_squared']=float(np.mean((v.mean(0)-a['exact'])**2))
  np.testing.assert_allclose(out['sampling_MSE'],31/32*out['sampling_variance_ddof1']+out['empirical_sampling_bias_squared'],atol=1e-12)
  out['negative_SF_components']=int((v[:,8:16]<-1e-9).sum())
  out['outside_C_range_components']=int((abs(v[:,:8])>1+1e-9).sum())
  if r['method']=='sv':
   setting=r['settings'][0];xi=setting['bases'].index('X'*8);num=setting['allocations'][xi]
   parity=np.array([(-1)**int(i).bit_count() for i in range(256)])
   out['SV_denominators']=(1+a['counts'][:,xi]@parity/num).tolist()
  else:out['SV_denominators']=None
  rows.append(out);perpoint[key]=out;resource.append({k:r[k] for k in ['point_id','kappa','h','p','method','mode','budget','shots_per_repeat','CNOT_shots_per_repeat','one_qubit_gate_shots_per_repeat','measurement_settings','target_CNOT_shots','zero_CNOT_control','equal_CNOT_verified','budget_shortfall','settings','disposition','seconds']})
 csvout(OUT/'equal_gate_budget/point_metrics.csv',rows);dump(OUT/'equal_gate_budget/point_metrics.json',rows);csvout(OUT/'equal_gate_budget/resource_audit.csv',resource)
 audits=[]
 for key,r in records.items():
  pid,p,method,mode,b=key
  if mode!='equal_gate' or method!='raw':continue
  arms=[records[(pid,p,m,mode,b)] for m in ['raw','zne_quadratic','sv']];costs=[x['CNOT_shots_per_repeat'] for x in arms];assert len(set(costs))==1
  audits.append(dict(point_id=pid,p=p,budget=b,G_equal=costs[0],verified=not r['zero_CNOT_control'],zero_control=r['zero_CNOT_control'],shots={a['method']:a['shots_per_repeat'] for a in arms}))
 dump(OUT/'equal_gate_budget/equality_verification.json',dict(groups=len(audits),all_equal=all(len({records[(r['point_id'],r['p'],m,'equal_gate',r['budget'])]['CNOT_shots_per_repeat'] for m in ['raw','zne_quadratic','sv']})==1 for r in audits),groups_detail=audits))
 summaries=[];paired=[]
 cohorts={'representatives':[r['id'] for r in inputs.values() if (r['kappa'],r['h']) in reps]}
 for k in cfg()['equal_gate_windows']:cohorts['window_'+str(k)]=[r['id'] for r in inputs.values() if r['kappa']==k and r['h'] in next(w['h'] for w in refs if w['kappa']==k)]
 cohorts['all_B']=sorted(set(pid for ids in cohorts.values() for pid in ids))
 for cohort,ids in cohorts.items():
  for mode,b in [('equal_shots',100000)]+[('equal_gate',b) for b in cfg()['equal_gate_base_budgets']]:
   for p in cfg()['p']:
    for m in ['raw','zne_quadratic','sv']:
     rr=[perpoint[(pid,p,m,mode,b)] for pid in ids if (pid,p,m,mode,b) in perpoint and not (mode=='equal_gate' and perpoint[(pid,p,m,mode,b)]['zero_CNOT_control'])]
     if not rr:continue
     mse=np.array([r['MSE_ED'] for r in rr]);labelled=[r for r in rr if r['reference_labelled']];summaries.append(dict(cohort=cohort,mode=mode,budget=b,p=p,method=m,requested_points=len(ids),points=len(rr),MSE_ED_mean=float(mse.mean()),MSE_ED_median=float(np.median(mse)),MSE_ED_q10=float(np.quantile(mse,.1)),MSE_ED_q90=float(np.quantile(mse,.9)),MSE_own_clean=float(np.mean([r['MSE_own_clean'] for r in rr])),bias_squared=float(np.mean([r['bias_squared'] for r in rr])),sampling_MSE=float(np.mean([r['sampling_MSE'] for r in rr])),physical_labelled_points=len(labelled),correct_coordinate_equivalents=sum(r['correct_fraction'] for r in labelled),wrong_coordinate_equivalents=sum(r['wrong_accepted_fraction'] for r in labelled),rejected_coordinate_equivalents=sum(r['rejected_fraction'] for r in labelled),shots_all32=sum(r['shots_per_repeat']*32 for r in rr),CNOT_shots_all32=sum(r['CNOT_shots_per_repeat']*32 for r in rr),one_qubit_gate_shots_all32=sum(r['one_qubit_gate_shots_per_repeat']*32 for r in rr)))
     if m!='raw':
      d=np.array([r['MSE_ED']-perpoint[(r['point_id'],p,'raw',mode,b)]['MSE_ED'] for r in rr]);paired.append(dict(cohort=cohort,mode=mode,budget=b,p=p,method=m,coordinates=len(d),mean_MSE_change=float(d.mean()),median_MSE_change=float(np.median(d)),improved=int(sum(d<0)),worsened=int(sum(d>0)),equal=int(sum(d==0)),coordinate_deltas=d.tolist(),scope='Coordinate-paired mean over32 repeats; historical equal-shots shared streams retained; new gate-budget arms use independent streams. No independence claim between reused analyses.'))
 dump(OUT/'equal_gate_budget/summary.json',summaries);csvout(OUT/'equal_gate_budget/summary.csv',summaries);dump(OUT/'equal_gate_budget/paired.json',paired);csvout(OUT/'equal_gate_budget/paired.csv',paired)
 boundary=[];curves={};costs=[]
 for w in refs:
  k=w['kappa'];h=np.array(w['h']);pts=[point(k,float(x)) for x in h];ed=np.array(w['values']);pure=np.array([data(r)['clean'] for r in pts]);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';reference=w['frozen_reference'];cleancomp=compare(h,pure,8,name,reference);cleanaudit=audit(cleancomp,h,pure,ed,pts,k,0,branches)
  curves[str(k)]=dict(h=h.tolist(),ED=ed.tolist(),clean=pure.tolist(),preparation=[r['metrics'] for r in pts],CNOTs=[r['resources']['cnots'] for r in pts],branches=[b for b in branches if b['kappa']==k],arms={})
  for mode,b in [('equal_shots',x) for x in cfg()['shots']]+([('equal_gate',x) for x in cfg()['equal_gate_base_budgets']] if k in cfg()['equal_gate_windows'] else []):
   for p in cfg()['p']:
    for m in ['raw','zne_quadratic','sv']:
     keys=[(r['id'],p,m,mode,b) for r in pts]
     if not all(key in arrays for key in keys):continue
     aa=[arrays[key] for key in keys];vv=np.array([a['samples'] for a in aa]).transpose(1,0,2);exact=np.array([a['exact'] for a in aa]);armkey=f'{mode}_{b}_{p}_{m}';curves[str(k)]['arms'][armkey]=dict(mean=vv.mean(0).tolist(),q05=np.quantile(vv,.05,axis=0).tolist(),q95=np.quantile(vv,.95,axis=0).tolist(),exact=exact.tolist(),samples=vv.tolist())
     rs=[records[key] for key in keys];costs.append(dict(kappa=k,mode=mode,budget=b,p=p,method=m,points=len(pts),repeats=32,shots_one_window=sum(r['shots_per_repeat'] for r in rs),G_one_window=sum(r['CNOT_shots_per_repeat'] for r in rs),shots_all32=sum(r['shots_per_repeat'] for r in rs)*32,G_all32=sum(r['CNOT_shots_per_repeat'] for r in rs)*32,scope='One p; sum over all3p for complete campaign'))
     for rep,values in [(-1,exact)]+list(enumerate(vv)):
      comp=compare(h,values,8,name,reference);aud=audit(comp,h,values,ed,pts,k,p,branches);pos=comp['result']['primary'];cleanpos=cleancomp['result']['primary'];supported=aud['quality_supports_position'];shift=float(pos['coordinate']-cleanpos['coordinate']) if supported and cleanaudit['quality_supports_position'] and cleanpos else None
      boundary.append(dict(kappa=k,mode=mode,budget=b,p=p,method=m,repeat=rep,frozen_rule_match=comp['matched'],reference_resolvable=comp['reference_resolvable'],frozen_position_error=comp['position_error'],delta_h_ED=comp['position_error'] if supported else None,delta_h_noise=shift,curve_audit_status=aud['flags'],quality_supports_position=supported,**{x:aud[x] for x in aud if x not in ['flags','quality_supports_position']},frozen_result=comp))
      if rep>=0:
       pzero=np.array([arrays[(pt['id'],0,m,mode,b)]['samples'][rep] for pt in pts])
       pc=compare(h,pzero,8,name,reference);pa=audit(pc,h,pzero,ed,pts,k,0,branches);pp=pc['result']['primary']
       boundary[-1].update(delta_h_noise_finite_p0=float(pos['coordinate']-pp['coordinate']) if supported and pa['quality_supports_position'] and pp else None,finite_p0_resolvable=pc['algorithm_estimatable'],finite_p0_curve_issues=pa['flags'],noise_shift_scope='delta_h_noise uses exact clean circuit; delta_h_noise_finite_p0 uses same-estimator/budget/repeat finite p0. Both guarded by named-feature resolution and curve audit; no failed repeats removed.')
 dump(OUT/'window_completion/curves.json',curves);dump(OUT/'window_completion/matches.json',boundary);csvout(OUT/'window_completion/matches.csv',[{k:v for k,v in r.items() if k!='frozen_result'} for r in boundary]);csvout(OUT/'window_completion/window_costs.csv',costs)
 coverage=[]
 for mode,b in [('equal_shots',x) for x in cfg()['shots']]+[('equal_gate',x) for x in cfg()['equal_gate_base_budgets']]:
  for p in cfg()['p']:
   for m in ['raw','zne_quadratic','sv']:
    requested=6 if mode=='equal_shots' else len(cfg()['equal_gate_windows']);ws=refs if mode=='equal_shots' else [w for w in refs if w['kappa'] in cfg()['equal_gate_windows']];resolvable=sum(w['frozen_reference']['resolvable'] for w in ws);details=[]
    for w in ws:
     rr=[r for r in boundary if (r['kappa'],r['mode'],r['budget'],r['p'],r['method'])==(w['kappa'],mode,b,p,m) and r['repeat']>=0];exact=next((r for r in boundary if (r['kappa'],r['mode'],r['budget'],r['p'],r['method'],r['repeat'])==(w['kappa'],mode,b,p,m,-1)),None)
     details.append(dict(kappa=w['kappa'],complete=len(rr)==32,reference_resolvable=w['frozen_reference']['resolvable'],match_fraction=sum(r['frozen_rule_match'] for r in rr)/32,matched_problem_fraction=sum(r['frozen_rule_match'] and bool(r['curve_audit_status']) for r in rr)/32,quality_supported_match_fraction=sum(r['frozen_rule_match'] and r['quality_supports_position'] for r in rr)/32,issues=dict(collections.Counter(x for r in rr for x in r['curve_audit_status'])),exact_match=exact['frozen_rule_match'] if exact else None,exact_audit=exact['curve_audit_status'] if exact else None,all_repeat_position_errors=[r['frozen_position_error'] if r['reference_resolvable'] else None for r in rr]))
    coverage.append(dict(mode=mode,budget=b,p=p,method=m,requested_windows=requested,executed_complete_windows=sum(r['complete'] for r in details),reference_resolvable_windows=resolvable,frozen_matching_window_equivalents=sum(r['match_fraction'] for r in details if r['reference_resolvable']),matched_fraction_given_reference=sum(r['match_fraction'] for r in details if r['reference_resolvable'])/resolvable,matched_problem_window_equivalents=sum(r['matched_problem_fraction'] for r in details if r['reference_resolvable']),quality_supported_match_window_equivalents=sum(r['quality_supported_match_fraction'] for r in details if r['reference_resolvable']),windows=details))
 dump(OUT/'window_completion/coverage.json',coverage);csvout(OUT/'window_completion/coverage.csv',coverage);dump(OUT/'window_completion/old_vs_followup.json',dict(old_B3_noisy_complete=3,new_B3_noisy_complete=len(curves),requested=6,reference_resolvable=5,old_H6_noisy_complete=3,H6_newly_completed=0,change_reason='Execution gap filled with unchanged B3 circuit, peak rule and estimator; no method improvement implied.'))
 # Unique physical/measurement computation counts, not number of roles or plotted results.
 phys=[read(p) for p in (OUT/'probabilities').glob('*.json')];meas=[read(p) for p in (OUT/'measurements').glob('*.json')];new=[r for r in meas if r['disposition']=='newly_executed'];dump(OUT/'verification/execution_statistics.json',dict(measurement_records=len(meas),new_measurement_records=len(new),reused_measurement_records=len(meas)-len(new),new_joint_multinomial_draws=sum(32*r['measurement_settings'] for r in new),new_simulated_shots=sum(32*r['shots_per_repeat'] for r in new),new_CNOT_shots=sum(32*r['CNOT_shots_per_repeat'] for r in new),unique_physical_probability_records=len(phys),new_density_records=sum(r['disposition']=='newly_executed' for r in phys),reused_probability_records=sum(r['disposition']=='historical_reused' for r in phys),density_seconds=sum(r['seconds'] for r in phys if r['disposition']=='newly_executed'),measurement_seconds=sum(r['seconds'] for r in new),peak_rss_bytes=max(r['process_peak_rss_bytes'] for r in phys),window_coordinates=sum(len(w['h']) for w in refs),B_unique_coordinates=len(cohorts['all_B']),representative_coordinates=len(cohorts['representatives']),analysis_seconds=time.perf_counter()-start))
 stat=read(OUT/'verification/execution_statistics.json')
 active_archives={r['archive'] for r in records.values()}
 retained=[r for r in meas if r['archive'] not in active_archives]
 stat.update(active_analysis_measurement_records=len(records),retained_prior_attempt_measurement_records=len(retained),retained_prior_attempt_new_shots=sum(32*r['shots_per_repeat'] for r in retained if r['disposition']=='newly_executed'),retained_prior_attempt_scope='After same-coordinate/different-gate cache rejection, a versioned cache lookup fix changed the implementation fingerprint. Earlier valid counts remain archived and costed, but are not pooled into the final analysis. No invalid cache was consumed.')
 import resource as process_resource
 stat['analysis_process_peak_rss_bytes']=process_resource.getrusage(process_resource.RUSAGE_SELF).ru_maxrss
 stat['active_new_measurement_records']=sum(r['disposition']=='newly_executed' for r in records.values())
 stat['active_reused_measurement_records']=sum(r['disposition']=='historical_reused' for r in records.values())
 stat['active_unique_coordinates']=len({r['point_id'] for r in records.values()})
 dump(OUT/'verification/execution_statistics.json',stat)
 print('Analyzed',len(records),'measurement records;',len(boundary),'window repeat/exact curves')
if __name__=='__main__':main()
