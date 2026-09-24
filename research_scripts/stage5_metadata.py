import sys,json,csv,platform,time,importlib.metadata
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,PLAN,sha,dump
rows=[];optimizer_steps=[]
legacy_coordinates={r['metadata']:(r['kappa'],r['h']) for r in json.loads((OUT/'verification/hva_legacy_coordinate_audit.json').read_text())['legacy_runs']}
for p in (OUT/'adaptive/cache').glob('*.json'):
 r=json.loads(p.read_text());s=r['selected'];rows.append(dict(kind='energy-only ADAPT campaign',inner_optimizer_calls=len(r['steps']),optimizer_success=None if s.get('reason')=='reference' else s['optimizer_success'],selected_checkpoint_reason=s.get('reason'),n=r['n'],kappa=r['kappa'],h=r['h'],ref=r['ref'],seed=r['key']['seed'],budget=r['key']['budget'],seconds=r.get('seconds'),stop=r.get('stop'),nit=r.get('nit'),nfev=r.get('nfev'),cnots=s['cnots'],joint_pass=s['joint_pass'],delta_e=s['delta_e'],fidelity=s['fidelity'],archive=r['archive'],raw_record=str(p.relative_to(ROOT))))
 for i,step in enumerate(r['steps']):optimizer_steps.append(dict(kind='ADAPT inner minimization',n=r['n'],kappa=r['kappa'],h=r['h'],ref=r['ref'],seed=r['key']['seed'],budget=r['key']['budget'],step=i+1,nit=step['nit'],nfev=step['nfev'],success=step['success'],message=step['message'],energy=step['energy'],initial_params=json.dumps(step['initial']),final_params=json.dumps(step['params']),source=str(p.relative_to(ROOT))))
adaptive_rows=list(rows)
for p in list((OUT/'end_to_end/hva').glob('*.json'))+list((OUT/'end_to_end/hva_v2').glob('*.json')):
 r=json.loads(p.read_text())
 if str(p.relative_to(ROOT)) in legacy_coordinates:r['kappa'],r['h']=legacy_coordinates[str(p.relative_to(ROOT))]
 for trial_i,(seed,t) in enumerate(zip(r['seeds'],r['trials'])):
  import numpy as np
  a=np.load(p.with_suffix('.npz'));optimizer_steps.append(dict(kind='HVA baseline',used_for_current_comparison=p.parent.name=='hva_v2',kappa=r.get('kappa'),h=r.get('h'),seed=seed,n=8,nit=t['nit'],nfev=t['nfev'],success=t['optimization_success'],message=t['message'],energy=t['energy'],initial_params=json.dumps(a['initials'][trial_i].tolist()),final_params=json.dumps(a['finals'][trial_i].tolist()),source=str(p.relative_to(ROOT))))
  rows.append(dict(kind='HVA auxiliary baseline',used_for_current_comparison=p.parent.name=='hva_v2',kappa=r.get('kappa'),h=r.get('h'),seed=seed,n=8,seconds=t['seconds'],nit=t['nit'],nfev=t['nfev'],optimizer_success=t['optimization_success'],exit_message=t['message'],energy=t['energy'],archive=str(p.with_suffix('.npz').relative_to(ROOT)),raw_record=str(p.relative_to(ROOT))))
for p in (OUT/'reopt').glob('*.json'):
 r=json.loads(p.read_text()); c=r['candidate'];rows.append(dict(kind='bounded energy retry',n=c['n'],kappa=c['kappa'],h=c['h'],ref=c['ref'],seconds=r['seconds'],nit=r['nit'],nfev=r['nfev'],optimizer_success=c['optimizer_success'],exit_message=r['message'],raw_record=str(p.relative_to(ROOT))))
 initial=json.loads((ROOT/c['source']).read_text())['checkpoints'][c['checkpoint']]['params'];optimizer_steps.append(dict(kind='bounded energy retry',n=c['n'],kappa=c['kappa'],h=c['h'],ref=c['ref'],nit=r['nit'],nfev=r['nfev'],success=c['optimizer_success'],message=r['message'],energy=c['energy'],initial_params=json.dumps(initial),final_params=json.dumps(c['params']),source=str(p.relative_to(ROOT))))
if optimizer_steps:
 with (OUT/'all_optimizer_steps.csv').open('w') as f:w=csv.DictWriter(f,list(dict.fromkeys(k for r in optimizer_steps for k in r)));w.writeheader();w.writerows(optimizer_steps)
if rows:
 with (OUT/'all_optimization_runs.csv').open('w') as f:w=csv.DictWriter(f,list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
code={str(p.relative_to(ROOT)):sha(p) for d,pat in [('annni','stage5*.py'),('scripts','*stage5*'),('tests','test_stage5.py'),('configs','stage5_v1.json')] for p in (ROOT/d).glob(pat) if p.is_file()};now=datetime.now(timezone.utc);started=datetime.fromisoformat(PLAN['started_utc'] if 'started_utc' in PLAN else PLAN['started']);mps=list((OUT/'floating_validation').glob('*.pkl'));versions={x:importlib.metadata.version(x) for x in ['numpy','scipy','pennylane','matplotlib','pytest','nbformat','nbclient']};meta=dict(run_id=PLAN['run_id'],started=started.isoformat(),snapshot_time=now.isoformat(),deadline=PLAN['deadline'],wall_elapsed_seconds=(now-started).total_seconds(),platform=platform.platform(),python=platform.python_version(),versions=versions,code_hashes=code,plan_sha=sha(OUT/'experiment_plan.json'),selector_sha=sha(OUT/'selector_frozen.json'),protected_inputs_manifest=sha(OUT/'verification/protected_inputs.json'),new_adaptive_runs=len(adaptive_rows),optimization_campaign_rows=len(rows),all_optimizer_invocations=len(optimizer_steps),adaptive_call_seconds=sum(r['seconds'] or 0 for r in adaptive_rows),all_optimizer_call_seconds=sum(r['seconds'] or 0 for r in rows),mps_checkpoint_count=len(mps),mps_checkpoint_bytes=sum(p.stat().st_size for p in mps),model='PBC circuit N8/N12; OBC MPS; J1=1; wire0 MSB; squared fidelities; h>0',noise='Target-only channel after every literal CNOT, including references and folding, same ideal parameters across p',access='S2 ideal-state assisted design; D2 full-density simulator cross-check not charged as simple local shot measurement',independence='Three distinct reference starts at common fixed seed11; not three independent random-seed replications. 128/192 share deterministic seed and prefix.',failures_preserved=True,source_disposition='Each cache metadata differentiates historical_reused and newly_executed; no unavailable result fabricated')
costs={}
for label,directory in [('noise','noise/cache'),('measurement_probabilities','end_to_end/probabilities'),('dynamics','dynamics_validation')]:
 records=[json.loads(p.read_text()) for p in (OUT/directory).glob('*.json')];records=[r for r in records if isinstance(r,dict)];new=[r for r in records if str(r.get('disposition','')).startswith('newly_executed') and 'seconds' in r];costs[label]=dict(new_records=len(new),summed_call_wall_seconds=sum(r['seconds'] for r in new),historical_reuse_records=sum(r.get('disposition')=='historical_reused' for r in records))
fr=json.loads((OUT/'floating_validation/index.json').read_text());costs['mps_main']=dict(new_records=len(fr),summed_call_wall_seconds=sum(r['seconds'] for r in fr));extras=[]
for name in ['chi512_index.json','size_extension_index.json']:
 p=OUT/'floating_validation'/name
 if p.exists():extras+=json.loads(p.read_text())
costs['mps_followups']=dict(new_records=len(extras),summed_call_wall_seconds=sum(r['seconds'] for r in extras));meta['phase_costs']=costs;meta['timing_limits']='Recorded section times overlap across processes and are not CPU time or total run wall time. Noise records time density evolution only; observation extraction, compression and orchestration are covered by overall elapsed time, not that kernel sum. Standalone selector timing was not separately instrumented; task progress logs provide elapsed checkpoints. Archive verification/export/packaging timing recorded separately.'
measurement_pilot=OUT/'verification/measurement_reuse.json'
if measurement_pilot.exists():
 pilot=json.loads(measurement_pilot.read_text());meta['measurement_probability_optimization_pilot']=pilot
 meta['phase_costs']['measurement_implementation_crosscheck']=dict(recorded_wall_seconds=pilot['literal_rotation_seconds']+pilot['reused_representation_seconds'],scope='Additional simulator validation cost; no generated hardware shots or extra physical circuit executions.')
meta['failed_preparation_counts']=[dict(task=r['task'],rule=r['rule'],failed=r['total']-r['joint_pass'],total=r['total']) for r in json.loads((OUT/'submission/statistics.json').read_text())['selection']]
meta['retry_campaigns']=sum(r['kind']=='bounded energy retry' for r in rows)
meta['input_hash_policy']='All historical scientific inputs are frozen in verification/protected_inputs.json; cache keys include physical gates/parameters, model/backend hashes, and frozen software environment is checked before verification/resume.'
meta['cache_corrections']=['verification/s0_compatibility_corrections.json','verification/hva_cache_correction.json']
meta['sampling_policy']='All archived measurement records include superseded B0 comparisons; costs preserve those actually executed records. Current-analysis membership is explicit in end_to_end/measurement_cost_audit.json. Statistical shots are classical samples from exact probabilities, not hardware calls.'
meta['sampled_shots_all_archives']=sum(32*sum(int(b) for b in json.loads(p.read_text())['cost']) for p in (OUT/'end_to_end/measurements').glob('*.json'))
meta['not_implemented']=['Hardware translation-projector measurement; S2 remains simulator-state-assisted', 'Thermodynamic phase-boundary certification or full N12 noisy map']
meta['artifact_qa_records']=['submission/notebook_execution.json','submission/presentation_visual_qa.json','submission/export_status.json']
dump(OUT/'metadata.json',meta);print(meta['new_adaptive_runs'],meta['wall_elapsed_seconds'])
