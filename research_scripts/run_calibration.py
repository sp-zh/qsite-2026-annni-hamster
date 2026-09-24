"""Bounded energy-only VQE calibration. Hash-verified per-run checkpoints."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
import argparse,csv,json,hashlib,platform,time,importlib.metadata
from datetime import datetime,timezone
import numpy as np
from annni.vqe import optimize,metrics
from annni.circuits import resources

OUT=ROOT/'results/calibration_v1'
CONFIG=ROOT/'configs/calibration_v1.json'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write_json(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2));tmp.replace(path)
def csv_write(path,rows):
    if not rows: return
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def inputs():
    paths=[CONFIG,ROOT/'requirements.lock.txt',ROOT/'annni/model.py',ROOT/'annni/circuits.py',
           ROOT/'annni/vqe.py',Path(__file__),ROOT/'results/baseline/grid_n8.npz']
    return {str(p.relative_to(ROOT)):digest(p) for p in paths}
def ref_at(data,kappa,h):
    ki=np.flatnonzero(np.isclose(data['kappa'],kappa));hi=np.flatnonzero(np.isclose(data['h'],h))
    assert len(ki)==len(hi)==1 and h>0
    state=data['states'][ki[0],hi[0]].copy()
    assert np.isfinite(state).all() and state.shape==(256,)
    return state,float(8*data['energy_per_site'][ki[0],hi[0]])
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--fallback',action='store_true')
    args=parser.parse_args()
    cfg=json.loads(CONFIG.read_text());OUT.mkdir(exist_ok=True);(OUT/'runs').mkdir(exist_ok=True)
    manifest=inputs()
    stamp=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    frozen=OUT/'run_manifest.json'
    if frozen.exists():
        assert json.loads(frozen.read_text())['hashes']==manifest, "Input/code/config changed: use a new versioned directory"
    else:
        write_json(frozen,dict(created_utc=now(),hashes=manifest,fingerprint=stamp,configuration=cfg))
    data=np.load(ROOT/'results/baseline/grid_n8.npz')
    start=time.perf_counter();cached=[];executed=[]
    main_summaries=json.loads((OUT/'summary.json').read_text()) if args.fallback else []
    fallback_points=set()
    if args.fallback:
        for i in range(len(cfg['points'])):
            valid=[r for r in main_summaries if r['point']==i and r['layers']<=6 and
                   r['joint_pass_count']>=2 and r['best_joint_pass']]
            if not valid: fallback_points.add(i)
        decision=OUT/'fallback_decision.json'
        if not decision.exists():
            write_json(decision,dict(time_utc=now(),reason="Prespecified rescue: no L<=6 stable passing energy-best candidate",
                failed_point_indices=sorted(fallback_points),config_unchanged=True,
                initializer="Each independent seed's own L6 result plus two small random layers; not three copies of best seed",
                budget_runs=3*len(fallback_points),maxiter=400))
    for i,(kappa,h) in enumerate(cfg['points']):
        if args.fallback and i not in fallback_points: continue
        layers=[8] if args.fallback else cfg['layers']
        ed,ed_e=ref_at(data,kappa,h)
        for L in layers:
            for seed in cfg['seeds']:
                if args.pilot and (i,L,seed) not in [(0,1,11),(7,2,23),(11,6,37)]: continue
                key=f'p{i:02d}_L{L}_s{seed}'
                path=OUT/'runs'/f'{key}.json'
                if path.exists():
                    old=json.loads(path.read_text());assert old['fingerprint']==stamp
                    archive=path.with_suffix('.npz')
                    assert archive.exists() and digest(archive)==old['archive_sha256']
                    cached.append(key);continue
                rng=np.random.default_rng(np.random.SeedSequence([seed,i,L]))
                if L==8:
                    oldpath=OUT/'runs'/f'p{i:02d}_L6_s{seed}.npz'
                    init=np.vstack([np.load(oldpath)['final_params'],rng.uniform(-.05,.05,(2,3))])
                    source=str(oldpath.relative_to(ROOT))
                else:
                    init=rng.uniform(cfg['initialization']['low'],cfg['initialization']['high'],(L,3))
                    source='independent_uniform'
                record=dict(run_id=key,point=i,kappa=kappa,h=h,layers=L,seed=seed,
                            initialization_source=source,started_utc=now(),fingerprint=stamp)
                status,final,state,trace=optimize(init,kappa,h,cfg['options'])
                metric,obs,ref=metrics(state,ed,ed_e,kappa,h,cfg['thresholds'])
                record.update(status);record.update(metric)
                resource=resources(8,L)
                record.update({k:resource[k] for k in ['parameters','cnots','high_level_gates','compiled_unitary_gates','unitary_depth','depth_with_channels']})
                archive=path.with_suffix('.npz')
                np.savez_compressed(archive,initial_params=init,final_params=final,state=state,ed_state=ed,
                    correlations=obs['correlations'],structure_factor=obs['structure_factor'],mx=obs['mx'],
                    ed_correlations=ref['correlations'],ed_structure_factor=ref['structure_factor'],ed_mx=ref['mx'],
                    q=2*np.pi*np.arange(8)/8,trace=trace)
                record['archive_sha256']=digest(archive);write_json(path,record);executed.append(key)
                print(key,f"de={metric['delta_e']:.3g} F={metric['fidelity']:.6f} pass={metric['joint_pass']} nit={status['nit']} {status['seconds']:.2f}s",flush=True)
    rows=[json.loads(p.read_text()) for p in sorted((OUT/'runs').glob('*.json'))]
    csv_write(OUT/'all_runs.csv',rows)
    summary=[];selected={}
    for i,point in enumerate(cfg['points']):
        for L in cfg['layers']+[8]:
            group=[r for r in rows if r['point']==i and r['layers']==L]
            if not group:continue
            best=min(group,key=lambda r:r['energy'])
            s=dict(point=i,kappa=point[0],h=point[1],layers=L,n_runs=len(group),best_run=best['run_id'],
                   best_seed=best['seed'],best_joint_pass=best['joint_pass'],
                   observable_pass_count=sum(r['observable_pass'] for r in group),
                   state_pass_count=sum(r['state_pass'] for r in group),
                   joint_pass_count=sum(r['joint_pass'] for r in group),
                   optimization_success_count=sum(r['optimization_success'] for r in group),
                   cnots=best['cnots'],unitary_depth=best['unitary_depth'])
            for name in ['energy','delta_e','epsilon_c','epsilon_sf','epsilon_mx','fidelity','seconds']:
                s['energy_best_'+name]=best[name]
                s['median_'+name]=float(np.median([r[name] for r in group]))
                s['min_'+name]=min(r[name] for r in group);s['max_'+name]=max(r[name] for r in group)
            summary.append(s)
        candidates=[s for s in summary if s['point']==i and s['n_runs']==3 and s['joint_pass_count']>=2 and s['best_joint_pass']]
        if candidates:
            chosen=min(candidates,key=lambda s:s['layers']);selected[str(i)]=chosen
    csv_write(OUT/'summary.csv',summary);write_json(OUT/'summary.json',summary)
    write_json(OUT/'selected.json',selected)
    payload={}
    for i,s in selected.items():
        d=np.load(OUT/'runs'/f"{s['best_run']}.npz")
        payload['params_p'+i]=d['final_params'];payload['state_p'+i]=d['state']
    np.savez_compressed(OUT/'selected_params.npz',**payload)
    for L in cfg['layers']+[8]:
        write_json(OUT/f'resources_L{L}.json',resources(8,L))
    audit=json.loads((OUT/'input_audit.json').read_text())
    for p,d in audit['protected_sha256'].items(): assert digest(ROOT/p)==d,f"Protected input changed: {p}"
    meta=dict(updated_utc=now(),python=sys.version,platform=platform.platform(),
        versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','pennylane','matplotlib']},
        manifest=manifest,configuration=cfg,all_run_count=len(rows),
        total_optimizer_seconds=sum(r['seconds'] for r in rows),
        this_invocation_seconds=time.perf_counter()-start,executed=executed,cached=cached,
        cache_policy="Every JSON fingerprint and NPZ SHA256 verified; input/config/code manifest must match",
        optimization_failures=[r['run_id'] for r in rows if not r['optimization_success']],
        joint_failures=[r['run_id'] for r in rows if not r['joint_pass']],
        stable_selected_points=list(selected),not_completed=["full noisy parameter scan","hardware","h=0 VQE"],
        model="periodic N=8; wire0 MSB; full SF retains self terms; squared fidelity; no output projection",
        gradient="exact NumPy statevector adjoint, cross-checked against PennyLane autograd and finite differences",
        initialization=cfg['initialization'],environment_changes=[])
    write_json(OUT/'metadata.json',meta)
    history=OUT/'invocations.jsonl'
    with history.open('a') as f:f.write(json.dumps(dict(time_utc=now(),argv=sys.argv,executed=executed,cached=cached,seconds=time.perf_counter()-start))+'\n')
    print(f"done {len(rows)} runs; stable selected {len(selected)}/15",flush=True)
if __name__=='__main__': main()
