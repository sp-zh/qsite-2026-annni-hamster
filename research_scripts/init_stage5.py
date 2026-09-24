import json,hashlib,platform,sys,os,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np,psutil
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';O.mkdir(exist_ok=True)
if (O/'experiment_plan.json').exists():raise SystemExit('Plan exists; do not reset')
old=json.loads((R/'configs/stage4_upgrade_v1.json').read_text());rng=np.random.default_rng(51023);used=set(tuple(x) for key in ['development','validation','held_out','final_map','slices'] for x in old[key]);used.update(tuple(x) for x in old['mitigation_points'])
for _,hs in old['mitigation_windows']:pass
for k,hs in old['mitigation_windows']:used.update((k,h) for h in hs)
def coordinates(m):
 a=[]
 for i in range(m):
  while True:
   k,h=([rng.uniform(0,1),rng.uniform(.08,.45)] if i%3==0 else [rng.uniform(.4,.65),rng.uniform(.1,.9)] if i%3==1 else [rng.uniform(0,1),rng.uniform(1.2,2)])
   v=tuple(np.round([k,h],6))
   if v not in used:used.add(v);a.append(list(v));break
 return a
now=datetime.now(timezone.utc);windows=[[0,[round(x,3) for x in np.arange(.8,1.201,.025)]],[.3,[round(x,3) for x in np.arange(.3,.601,.025)]],[.8,[round(x,3) for x in np.arange(.4,.701,.025)]]]
p=dict(old);p.update(run_id='stage5_'+now.strftime('%Y%m%dT%H%M%SZ'),started_utc=now.isoformat(),deadline=(now+timedelta(hours=12)).isoformat(),validation_v2=coordinates(24),test_v2=coordinates(72),n12_test_v2=coordinates(24),windows=windows,coordinate_seed=51023,source_stage4='results/stage4_upgrade_v1',stage5_budgets=dict(selection=.25,end_to_end=.30,n12=.15,floating=.20,dynamics_submission=.10),resources=dict(cpu=os.cpu_count(),ram_total=psutil.virtual_memory().total,ram_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(R).free,working_memory_cap_bytes=6*2**30,max_heavy_processes=2,blas_threads_requested=1),selector_candidates=[dict(w0_min=w,parity_min=.999999,energy_tolerance_per_site=e) for w in [.99,.999] for e in [1e-6,1e-8]],selector_numerical_tie_total=1e-10,reopt=dict(maxiter=2000,starts=1,max_candidates=1,trigger='No symmetry-qualified candidate or best qualified energy exceeds minimum by >1e-3 per site',objective='unpenalized physical energy; no additional gates',seed=501),n12_cnots_checkpoints=[32,64,96,128,160,192],new_quenches=[[.3,.3],[.3,.7],[.3,1.6],[.8,.3],[.8,.7],[.8,1.6]],quench_dt=[.1,.05],anchor_protocol=dict(ferro='k<=.15 and h<=.2',antiphase='k>=.85 and h<=.2',paramagnetic='k<=.3 and h>=1.8',qualification='independent ED: SF0>=.8 ferro, SFpi/2>=.4 antiphase, Mx>=.85 paramagnetic; else unlabelled',frozen_before_noisy_results=True),floating_validation=dict(centers=[[.6,.2],[.8,.5],[1,.7]],offset=.025,center_n=128,chi=[128,256],initial=['plus','antiphase'],neighbors_n=[96,128],neighbor_chi=[128,256],controls=[[0,1],[0,.2],[0,1.8]],control_n=64,fit_windows=['r=2..N/3','r=4..N/2-2'],entropy_edges=[.15,.25],model='signed A*cos(q*r+phi) times power or exponential, same 4 parameters; block held-out distances final25%',grade=dict(delta_e_per_site=1e-5,delta_c=.01,delta_s=.03,c_range=[.75,1.25],q_size_change=.1),chi512_trigger='delta_c>=.01 or delta_s>=.03 or delta_e/N>=1e-5',max_sweeps=24),scope='Old grid and heldout are development/descriptive, never fresh tests')
p['end_to_end']=sorted(set(tuple(v) for v in old['slices'])|{(k,h) for k,hs in windows for h in hs});p['n12_mitigation_points']=[[k,h] for k in [0,.3,.8] for h in [.5,1.8]]
for folder in ['verification','selection_audit','selector_benchmark','n8_maps','end_to_end','n12_scaling','floating_validation','dynamics_validation','submission','ed','adaptive/cache']: (O/folder).mkdir(parents=True,exist_ok=True)
def dump(path,a):path.write_text(json.dumps(a,indent=2))
dump(O/'experiment_plan.json',p);dump(R/'configs/stage5_v1.json',p)
files={}
for base in ['upstream','results/baseline','results/stage3_v1','results/stage4_v1','results/stage4_upgrade_v1','annni','configs','tests']:
 for f in (R/base).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':files[str(f.relative_to(R))]=hashlib.sha256(f.read_bytes()).hexdigest()
dump(O/'verification/protected_inputs.json',files);(O/'verification/README_before.md').write_bytes((R/'README.md').read_bytes());print(p['run_id'],p['deadline'],len(files),len(p['end_to_end']))
