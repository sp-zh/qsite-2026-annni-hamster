import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json,time
import numpy as np
from annni.stage3 import *
from annni.noise import noisy_density

def old(k,h,seed,L=6):
    cfg=json.loads((ROOT/'configs/calibration_v1.json').read_text())
    i=next(i for i,(a,b) in enumerate(cfg['points']) if np.isclose(a,k) and np.isclose(b,h))
    stem=ROOT/'results/calibration_v1/runs'/f'p{i:02d}_L{L}_s{seed}'
    r=json.loads(stem.with_suffix('.json').read_text());d=np.load(stem.with_suffix('.npz'))
    return r,d['final_params'].copy(),str(stem.with_suffix('.npz').relative_to(ROOT))
def task_a():
    rows=[];L=6;k=.3;h=.4
    for seed in CFG['A']['old_seeds']:
        r,t,source=old(k,h,seed)
        new,_=run_opt(f'A1_target_s{seed}',t,k,h,seed,'A1_parameter_resume',source,1600,r['nit'],r['seconds'])
        rows.append(new)
    for seed in CFG['A']['cold_seeds']:
        r,_=run_opt(f'A2_target_s{seed}',random_init(seed,k,h,L),k,h,seed,'A2_independent_cold','new independent seed')
        rows.append(r)
    for seed in CFG['A']['old_seeds']:
        prior,t,source=old(k,.5,seed)
        prior_it=prior['nit'];prior_sec=prior['seconds']
        for step in [.45,.4]:
            r,t=run_opt(f'A3_h{step:.2f}_s{seed}',t,k,step,seed,'A3_continuation',source,2000,prior_it,prior_sec)
            rows.append(r);source=r['archive'];prior_it=r['cumulative_iterations'];prior_sec=r['cumulative_seconds']
    for idx,(k,h) in enumerate(CFG['A']['extra_points']):
        for seed in CFG['A']['old_seeds']:
            r,t,source=old(k,h,seed)
            new,_=run_opt(f'Aextra{idx}_resume_s{seed}',t,k,h,seed,'Aextra_parameter_resume',source,1600,r['nit'],r['seconds']);rows.append(new)
        for seed in [101,211,307]:
            r,_=run_opt(f'Aextra{idx}_cold_s{seed}',random_init(seed,k,h,L),k,h,seed,'Aextra_independent_cold','new independent seed');rows.append(r)
    assert len(rows)<=60
    write_csv(OUT/'optimization/A_runs.csv',rows);dump(OUT/'optimization/A_runs.json',rows)
    summary=[]
    for group in sorted(set(r['group'] for r in rows)):
        points=sorted(set((r['kappa'],r['h']) for r in rows if r['group']==group))
        for k,h in points:
            g=[r for r in rows if r['group']==group and r['kappa']==k and r['h']==h]
            summary.append(dict(group=group,kappa=k,h=h,runs=len(g),joint_pass=sum(r['joint_pass'] for r in g),
                optimizer_success=sum(r['optimizer_success'] for r in g),best_energy=min(r['energy'] for r in g),
                median_delta_e=float(np.median([r['delta_e'] for r in g])),median_fidelity=float(np.median([r['fidelity'] for r in g])),
                new_seconds=sum(r['end_to_end_seconds'] for r in g)))
    write_csv(OUT/'optimization/A_summary.csv',summary)
    print('A complete',summary,flush=True)

def task_b():
    rows=[];selected=[]
    for i,(k,h) in enumerate(CFG['B']['points']):
        for L in [2,4,6]:
            g=[]
            for seed in [101,211,307]:
                r,_=run_opt(f'B_p{i}_L{L}_s{seed}',random_init(seed,k,h,L),k,h,seed,'B_matched_cold','matched independent cold')
                rows.append(r);g.append(r)
            selected.append(min(g,key=lambda r:r['energy']))
    write_csv(OUT/'matched_noise/optimization.csv',rows)
    dump(OUT/'matched_noise/selection_frozen.json',dict(created_utc=now(),criterion='min noiseless energy; before any B noise',rows=selected))
    results=[]
    for r in selected:
        for p in [0,.01,.05]:
            result=run_noise(r,p,'B',keep_density=True);results.append(result)
            dump(OUT/'matched_noise/records'/f"{r['name']}_p{p}.json",result)
            print('B noise',r['name'],p,result['cache_status'],f"F={result['fidelity_ed']:.4g}",flush=True)
    write_csv(OUT/'matched_noise/observations.csv',results)
    dump(OUT/'matched_noise/observations.json',results)
    print('B complete 45 density evaluations',flush=True)

def benchmark():
    if (OUT/'verification/benchmark.json').exists():return
    rows=[]
    for L in [2,4,6]:
        t=random_init(101,.3,.4,L)
        start=time.perf_counter()
        # Cold object setup included for backend equivalence timing.
        psi=HVAEngine().state(t);puretime=time.perf_counter()-start
        for p in [.01]:
            start=time.perf_counter();rho=dense_literal(t,p);fast=time.perf_counter()-start
            start=time.perf_counter();reference_rho=noisy_density(t,p);qmltime=time.perf_counter()-start
            error=float(np.max(abs(rho-reference_rho)));assert error<2e-11
            start=time.perf_counter();observe(rho);density_checks(rho);post=time.perf_counter()-start
            rows.append(dict(L=L,p=p,pure_setup_state_seconds=puretime,density_numpy_seconds=fast,
                density_pennylane_seconds=qmltime,post_seconds=post,max_matrix_error=error))
    dump(OUT/'verification/benchmark.json',rows);print('Measured backend',rows,flush=True)
if __name__=='__main__':
    init_session();benchmark();task_a();task_b()
