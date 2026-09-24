import json,hashlib,platform,sys,os,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
import psutil,numpy as np,importlib.metadata as im
R=Path(__file__).resolve().parents[1]; O=R/'results/stage4_upgrade_v1';O.mkdir(exist_ok=True)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
if (O/'experiment_plan.json').exists():raise SystemExit('Plan exists; do not reset deadline')
now=datetime.now(timezone.utc)
dev=json.loads((R/'configs/calibration_v1.json').read_text())['points']+[[.45,.15],[.5,.15],[.55,.15]]
held=[[k,h] for k in [.025,.175,.325,.475,.525,.675,.825,.975] for h in [.15,.35,.55,.85,1.25,1.75]]
plan=dict(run_id='upgrade_'+now.strftime('%Y%m%dT%H%M%SZ'),started_utc=now.isoformat(),deadline=(now+timedelta(hours=12)).isoformat(),wall_budget_seconds=43200,
 resources=dict(cpu=os.cpu_count(),ram_total=psutil.virtual_memory().total,ram_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(R).free,working_memory_cap_bytes=3*2**30,max_heavy_processes=1,blas_threads=1),
 budgets_fraction=dict(main=.35,n12=.15,floating=.2,detection=.1,mitigation=.1,dynamics=.05,submission=.05),
 development=dev,validation=[[.1,.3],[.25,.65],[.4,.25],[.6,.45],[.75,.7],[.9,1.5]],held_out=held,final_map=[[round(k*.05,3),round(h*.1,3)] for k in range(21) for h in range(1,21)],slices=[[k,round(h*.1,3)] for k in [0,.3,.8] for h in range(1,21)],
 refs=['plus','ghz','antiphase'],development_seeds=[11,23,37],map_seeds=[11],cnots_checkpoints=[16,32,64,96,128],n12_cnots_checkpoints=[32,64,96,128],
 pool=['YZ','ZY on directed NN and NNN'],extended_pool=['YXZ','ZXY on consecutive triples'],maxiter=400,ftol=1e-12,gtol=1e-7,selection_energy_tolerance_per_site=.0001,gradient_stop=1e-5,improvement_stop=1e-8,
 selection='minimum CNOT candidate within N*1e-4 of minimum candidate energy, then energy; no ED used; evaluate all references',
 seed_protocol='independent tie-breaking and initial appended angle U[-.01,.01]; deterministic per seed and point; no copied warm starts',
 thresholds=json.loads((R/'configs/calibration_v1.json').read_text())['thresholds'],
 mitigation_points=[[0,.2],[0,1],[0,1.8],[.3,.2],[.3,.4],[.8,.2],[.8,.5],[.8,1.2]],mitigation_windows=[[0,[.8,.9,1,1.1,1.2]],[.3,[.3,.4,.5,.6]]],mitigation_folds=[1,3,5],mitigation_shots=[10000,100000],mitigation_replicates=32,zne_primary='linear least squares intercept at scale zero; quadratic Richardson separate',
 n12_noise_points=[[k,h] for k in [0,.3,.8] for h in [.2,.5,1,1.8]],trajectory_batches=[512,2048,8192],trajectory_target_halfwidth=.025,trajectory_interval='Bonferroni over 3 looks and N C plus N SF plus Mx; normal approximation labelled MC, independent validation batch if selected',
 floating=dict(ns=[32,64,96],chi=[64,128,256],kappa=[.6,.8,1.],h=[round(.1*i,2) for i in range(1,13)],bc='open',max_sweeps=20,controls=[[0,1],[0,.2],[0,1.8]]),
 dynamics=dict(n=8,kappa=[.3,.8],h=[.2,.4,.6,.8,1.,1.4,1.8],heldout_h=[.6,1.4],initial=['zero','0011'],dt=[.2,.1,.05],p=[0,.01,.05],times=[round(.2*i,2) for i in range(11)],features=['time average C1 SF0 SFpi2 Mx return','early return decay t=.2'],order=2),
 conventions=dict(n8_bc='periodic',J1=1,basis='wire0 MSB',noise='after each actual CNOT target: probabilities I=1-p,X=Y=Z=p/3',p=[0,.01,.05],connections='direct NN/NNN ring; three-site paths use nearest neighbor CNOT chain',sf_self=True,h0='ED incoherent mixture; absent from circuit runs'),
 disposition='newly_executed; historical inputs explicitly identified',old_output_collision='results/stage4_v1 already exists; protected, using stage4_upgrade_v1',python=sys.version,platform=platform.platform(),versions={x:im.version(x) for x in ['numpy','scipy','pennylane','matplotlib']})
dump(O/'experiment_plan.json',plan);dump(R/'configs/stage4_upgrade_v1.json',plan)
files={}
for base in ['upstream','results/baseline','results/calibration_v1','results/diagnostics_v1','results/noise_smoke_v1','results/stage3_v1','results/stage4_v1','annni','configs','tests','submission']:
 for p in (R/base).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
files['requirements.lock.txt']=hashlib.sha256((R/'requirements.lock.txt').read_bytes()).hexdigest()
dump(O/'verification/protected_inputs.json',files)
(O/'verification/README_before.md').write_bytes((R/'README.md').read_bytes())
info={}
for name in ['grid_n8','slices_n8','slices_n12','slices_n16']:
 with np.load(R/f'results/baseline/{name}.npz') as a:
  info[name]={k:dict(shape=list(a[k].shape),dtype=str(a[k].dtype)) for k in a.files}
dump(O/'verification/npz_schema.json',info)
print(plan['run_id'],plan['deadline'],len(files),len(held))
