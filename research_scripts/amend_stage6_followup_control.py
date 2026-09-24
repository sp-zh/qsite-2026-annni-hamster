"""Pre-B coverage correction: include a declared antiphase interior control."""
import sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
from annni.stage6_arms import arm
from annni.upgrade_gates import h_action,geometry
from annni.stage6_diagnostics import physical_reference
assert not (OUT/'B_index.json').exists(),'Cannot change the cohort after B begins'
c=cfg();old=dict(c);k,h=.8,.1
if any(x['kappa']==k and x['h']==h for x in c['representatives']):raise SystemExit('Already amended')
shutil.copy(OUT/'config.json',OUT/'verification/config_initial_before_control_correction.json')
c['representatives']=[dict(kappa=k,h=h,region='interior_control') if x['kappa']==.7 and x['h']==1.5 else x for x in c['representatives']]
c['selection_rule']+=' Before B sampling: replace benchmark32(.7,1.5), which has no independent interior label, with benchmark33(.8,.1) to include the declared antiphase interior. No equal-resource outcomes existed.'
dump(OUT/'config.json',c);dump(ROOT/'configs/stage6_followup_v1.json',c)
rr=next(x for x in read(OLD/'legacy_b3/development_index.json') if x['kappa']==k and x['h']==h);a=arm(rr['selected']);ed=next(read(p) for p in (OLD/'reference_atlas/cache').glob('*.json') if (lambda r:r['n']==8 and r['kappa']==k and r['h']==h)(read(p)));target=np.load(ROOT/ed['archive'])['state'];v=vector(observations(a['state'],8));ev=vector(observations(target,8));e=float(np.vdot(a['state'],h_action(a['state'],8,k,h)).real);de=(e-ed['energy'])/8;ec=float(max(abs(v[:8]-ev[:8])));es=float(max(abs(v[8:16]-ev[8:16])));em=float(abs(v[-1]-ev[-1]));F=float(abs(np.vdot(target,a['state']))**2);op=de<=.001 and max(ec,es,em)<=.02;label,level,reason=physical_reference(8,k,h,target,observations(target,8),ed['binder']);key=uid(dict(n=8,kappa=k,h=h,bc='PBC'));f=OUT/'inputs'/f'{key}.npz';np.savez_compressed(f,state=a['state'],ed_state=target,ed=ev,clean=v)
inputs=read(OUT/'inputs.json');inputs[key]=dict(id=key,n=8,kappa=k,h=h,gates=a['gates'],source=a['source_archive'],source_sha=sha(ROOT/a['source_archive']),reference_source=ed['archive'],reference_sha=sha(ROOT/ed['archive']),archive=str(f.relative_to(ROOT)),sha256=sha(f),selected_parameters=rr['selected']['selected'],reference=rr['selected']['ref'],seed=rr['selected']['seed'],label=label,label_level=level,label_reason=reason,metrics=dict(delta_e=de,epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,fidelity=F,observable_pass=bool(op),state_pass=F>=.99,joint_pass=bool(op and F>=.99)),resources=resources(a['gates'],8),roles=['representative']);dump(OUT/'inputs.json',inputs)
oldm=read(OUT/'historical_measurements.json');protected=read(OUT/'verification/protected_inputs.json')
for path in (OLD/'end_to_end').glob('core_*_index.json'):
 for point in read(path):
  if point['kappa']==k and point['h']==h:
   for entry in point['entries']:
    if entry['method']=='B3':
     r=entry['record'];assert sha(ROOT/r['archive'])==r['sha256'];oldm.append(dict(kappa=k,h=h,p=r['p'],estimator=entry['estimator'],record=r))
     for name in ['archive','counts_archive']:
      if name in r:protected[r[name]]=sha(ROOT/r[name])
for path in [a['source_archive'],ed['archive']]:protected[path]=sha(ROOT/path)
dump(OUT/'historical_measurements.json',oldm);dump(OUT/'verification/protected_inputs.json',protected);dump(OUT/'verification/control_cohort_amendment.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),old_coordinate=[.7,1.5],new_coordinate=[.8,.1],reason='Missing antiphase physical-interior control discovered during input review',B_sampling_started=False,old_configuration_retained='verification/config_initial_before_control_correction.json',new_config_sha=sha(OUT/'config.json'),deadline_unchanged=c['deadline']))
print('Antiphase control frozen before B:',label)
