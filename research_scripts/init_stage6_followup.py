"""Read-only Stage6 intake; freeze the directed followup before sampling."""
import sys,json,csv,hashlib,shutil,platform
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_arms import arm
from annni.upgrade_gates import resources,observations,vector,h_action
from annni.stage6_diagnostics import physical_reference,response_curves,peaks_and_primary
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'results/stage6_followup_v1';OLD=R/'results/stage6_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uid(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else x.item()))
def csvout(p,rows):
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if (O/'config.json').exists():raise SystemExit('Existing followup: inspect config and resume, do not reinitialize')
now=datetime.now(timezone.utc);refs=json.loads((OLD/'reference_atlas/window_reference.json').read_text())
# Fixed cohort: six first difficult benchmark entries plus every second interior control.
benchmark=json.loads((OLD/'failure_mechanisms/benchmark.json').read_text())['points'];reps=[benchmark[i] for i in [0,1,2,3,4,5,24,26,28,30,32,34]]
# First registered resolvable ferro-side window and last registered resolvable competing-side window.
eqks=[refs[0]['kappa'],refs[-1]['kappa']]
config=dict(run_id='stage6_followup_'+now.strftime('%Y%m%dT%H%M%SZ'),started_utc=now.isoformat(),deadline=(now+timedelta(hours=4)).isoformat(),stage='post_Stage6_directed_followup_not_original_preregistration',n=8,p=[0,.01,.05],shots=[10000,100000],repeats=32,seed=9230626,equal_gate_base_budgets=[100000,300000],representatives=reps,equal_gate_windows=eqks,selection_rule='Benchmark indices0..5 plus24,26,28,30,32,34; first and last registered resolvable windows. Frozen before followup sampling, not chosen by mitigation outcome.',allocation='Original equal-scale/equal-setting largest-remainder allocation; maximal ZNE totalshots not exceeding target equivalent CNOT budget; raw/SV totalshots exactly equal sum(fold*ZNE scale shots).',curve_audit='Secondary post-Stage6 interpretation, not replacement peak classifier; endpoint maximum, frozen competing peaks, response peak amplitude<10%ED, preparation failure and unverified structure switch are separate flags.',resources=dict(heavy_workers=1,blas_threads=1,memory_budget_gib=6),original_plan_sha=sha(OLD/'experiment_plan.json'))
dump(O/'config.json',config);dump(R/'configs/stage6_followup_v1.json',config)
required=['configs/stage6_v1.json','results/stage6_v1/report/REPORT.md','results/stage6_v1/report/EVIDENCE_LEDGER.json','results/stage6_v1/metadata.json','results/stage6_v1/verification/numerical_completion.json','results/stage6_v1/end_to_end/boundary_coordinate_coverage.json','results/stage6_v1/end_to_end/response_robustness.json','results/stage6_v1/end_to_end/detector_boundary_coverage.json','results/stage6_v1/end_to_end/boundary_curves.json','results/stage6_v1/failure_mechanisms/actual_branch_switches.json','results/stage6_v1/end_to_end/mitigation_frozen.json','requirements.lock.txt']
protected={p:sha(R/p) for p in required}
for folder in ['annni','scripts','tests','configs']:
 for p in (R/folder).glob('*'):
  if p.is_file() and 'followup' not in p.name:protected[str(p.relative_to(R))]=sha(p)
# Record metadata for all old research files, plus cryptographic hashes of all actual consumed inputs.
oldstat={str(p.relative_to(R)):[p.stat().st_size,p.stat().st_mtime_ns] for p in OLD.rglob('*') if p.is_file()}
dump(O/'verification/old_file_stat_inventory.json',oldstat)
inputs={};oldmeasure={};inventory=[]
for task in ['windows','core']:
 for p in sorted((OLD/'end_to_end').glob(task+'_*_index.json')):
  protected[str(p.relative_to(R))]=sha(p)
  for point in json.loads(p.read_text()):
   for e in point['entries']:
    if e['method']=='B3':oldmeasure[(point['kappa'],point['h'],e['record']['p'],e['estimator'])]=e['record']
windowruns=json.loads((OLD/'legacy_b3/windows_index.json').read_text());devruns=json.loads((OLD/'legacy_b3/development_index.json').read_text());edmeta={}
for p in (OLD/'reference_atlas/cache').glob('*.json'):
 r=json.loads(p.read_text())
 if r['n']==8:edmeta[(r['kappa'],r['h'])]=r
points=[dict(kappa=w['kappa'],h=float(h),source_task='windows') for w in refs for h in w['h']]+[dict(kappa=x['kappa'],h=x['h'],source_task='development') for x in reps]
for point in points:
 k,h=point['kappa'],point['h'];key=uid(dict(n=8,kappa=k,h=h,bc='PBC'))
 if key in inputs:continue
 runs=windowruns if point['source_task']=='windows' else devruns
 rr=next(r for r in runs if abs(r['kappa']-k)<1e-14 and abs(r['h']-h)<1e-14);a=arm(rr['selected']);ed=edmeta.get((k,h))
 if ed is None:ed=next(v for (kk,hh),v in edmeta.items() if abs(kk-k)<1e-14 and abs(hh-h)<1e-14)
 protected[a['source_archive']]=sha(R/a['source_archive']);protected[ed['archive']]=sha(R/ed['archive'])
 target=np.load(R/ed['archive'])['state'];v=vector(observations(a['state'],8));ev=vector(observations(target,8));e=float(np.vdot(a['state'],h_action(a['state'],8,k,h)).real);de=(e-ed['energy'])/8;assert de>-1e-9
 ec=float(max(abs(v[:8]-ev[:8])));es=float(max(abs(v[8:16]-ev[8:16])));em=float(abs(v[-1]-ev[-1]));F=float(abs(np.vdot(target,a['state']))**2);op=de<=.001 and max(ec,es,em)<=.02
 label,level,reason=physical_reference(8,k,h,target,observations(target,8),ed['binder'])
 f=O/'inputs'/f'{key}.npz';f.parent.mkdir(exist_ok=True);np.savez_compressed(f,state=a['state'],ed_state=target,ed=ev,clean=v)
 inputs[key]=dict(id=key,n=8,kappa=k,h=h,gates=a['gates'],source=a['source_archive'],source_sha=sha(R/a['source_archive']),reference_source=ed['archive'],reference_sha=sha(R/ed['archive']),archive=str(f.relative_to(R)),sha256=sha(f),selected_parameters=rr['selected']['selected'],reference=rr['selected']['ref'],seed=rr['selected']['seed'],label=label,label_level=level,label_reason=reason,metrics=dict(delta_e=de,epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,fidelity=F,observable_pass=bool(op),state_pass=F>=.99,joint_pass=bool(op and F>=.99)),resources=resources(a['gates'],8),roles=['window' if point['source_task']=='windows' else 'representative'])
for w in refs:
 reference=peaks_and_primary(w['h'],response_curves(w['h'],w['values'],8)['minus_dm0_dh' if w['kappa']<.5 else 'minus_dmap_dh']);w['frozen_reference']=reference
 for h in w['h']:
  inventory.append(dict(kappa=w['kappa'],h=h,reference_resolvable=reference['resolvable'],registered_grid_sha=uid(w['h']),parameter_source=inputs[uid(dict(n=8,kappa=w['kappa'],h=float(h),bc='PBC'))]['source'],completed=json.dumps([(p,m,[10000,100000]) for p in config['p'] for m in ['raw','zne_quadratic','sv'] if (w['kappa'],h,p,m) in oldmeasure]),missing=json.dumps([(p,m) for p in config['p'] for m in ['raw','zne_quadratic','sv'] if (w['kappa'],h,p,m) not in oldmeasure])))
dump(O/'inputs.json',inputs);dump(O/'window_reference.json',refs)
old=[]
for (k,h,p,m),r in oldmeasure.items():
 if any(abs(x['kappa']-k)<1e-14 and abs(x['h']-h)<1e-14 for x in inputs.values()):
  old.append(dict(kappa=k,h=h,p=p,estimator=m,record=r))
  for field,hfield in [('archive','sha256'),('counts_archive',None)]:
   if field in r:
    path=R/r[field];actual=sha(path)
    if hfield:assert actual==r[hfield]
    protected[r[field]]=actual
resource=[]
for x in old:
 r=x['record']
 for b,c in r['cost'].items():resource.append(dict(kappa=x['kappa'],h=x['h'],p=x['p'],estimator=x['estimator'],budget=b,comparison='equal_total_shots',equal_CNOT_shots_completed=False,gate_shots=c['gate_shots_per_rep'],counts=r.get('counts_archive',r['archive']),fingerprint=uid(r['key']),scope='raw/SV same-circuit costs coincide; no three-arm gate-matched experiment'))
csvout(O/'window_inventory.csv',inventory);csvout(O/'resource_experiment_inventory.csv',resource);dump(O/'historical_measurements.json',old)
shutil.copy(OLD/'failure_mechanisms/actual_branch_switches.json',O/'branch_switches_historical.json')
shutil.copy(R/'results/stage4_upgrade_v1/detection/frozen.json',O/'detector_frozen.json')
dump(O/'verification/protected_inputs.json',protected);dump(O/'verification/environment.json',dict(python=sys.version,platform=platform.platform(),numpy=np.__version__))
print(config['run_id'],config['deadline'],'inputs',len(inputs),'historical measurements',len(old))
