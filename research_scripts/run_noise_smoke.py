import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import sys
sys.path.insert(0,str(ROOT))
import json,time,hashlib,csv,platform,importlib.metadata
from datetime import datetime,timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.circuits import HVAEngine,observe,qnode,resources
from annni.noise import noisy_density,check_schedule,density_checks
from annni.diagnostics import diagnose

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    start=time.perf_counter()
    out=ROOT/'results/noise_smoke_v1';out.mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'configs/noise_smoke_v1.json').read_text())
    chosen=json.loads((ROOT/'results/calibration_v1/selected.json').read_text())
    protocol=json.loads((ROOT/'results/diagnostics_v1/protocol.json').read_text())
    assert protocol==json.loads((ROOT/'configs/diagnostics_v1.json').read_text())
    files=[ROOT/p for p in ['configs/noise_smoke_v1.json','configs/diagnostics_v1.json','annni/circuits.py',
        'annni/noise.py','annni/diagnostics.py','annni/model.py','scripts/run_noise_smoke.py',
        'requirements.lock.txt','results/calibration_v1/selected.json','results/calibration_v1/selected_params.npz']]
    for point in cfg['point_indices']:
        assert str(point) in chosen, "No stable passing calibration for requested smoke point"
        files.append(ROOT/'results/calibration_v1/runs'/f"{chosen[str(point)]['best_run']}.npz")
    hashes={str(p.relative_to(ROOT)):digest(p) for p in files}
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())['input_hashes']==hashes
    else:manifest.write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),input_hashes=hashes,config=cfg),indent=2))
    rows=[];full={};schedules={};verification=[]
    for point in cfg['point_indices']:
        selected=chosen[str(point)];run=selected['best_run']
        assert selected['best_joint_pass'] and selected['joint_pass_count']>=2
        d=np.load(ROOT/'results/calibration_v1/runs'/f'{run}.npz')
        theta=d['final_params'];ed=d['ed_state'];psi=HVAEngine().state(theta)
        high=np.asarray(qnode()(theta));decomp=np.asarray(qnode(decomposed=True)(theta))
        np.testing.assert_allclose(psi,high,atol=1e-11)
        np.testing.assert_allclose(high,decomp,atol=1e-11)
        ref=observe(ed);pure=observe(psi);k=selected['kappa'];h=selected['h']
        resource=resources(8,len(theta));schedules[str(point)]=resource
        phash=hashlib.sha256(theta.tobytes()).hexdigest()
        base=None
        for p in cfg['probabilities']:
            begin=time.perf_counter()
            schedule=check_schedule(theta,p)
            assert schedule['cnots']==resource['cnots']
            rho=noisy_density(theta,p);checks=density_checks(rho)
            obs=observe(rho)
            if p==0:
                base=obs
                np.testing.assert_allclose(rho,np.outer(psi,psi.conj()),atol=1e-10)
                for key in obs:np.testing.assert_allclose(obs[key],pure[key],atol=1e-10)
            state_fidelity=float(np.vdot(ed,rho@ed).real)
            diag=diagnose(obs['structure_factor'],obs['mx'],protocol)
            row=dict(point=point,kappa=k,h=h,layers=len(theta),run_id=run,p=p,cnots=resource['cnots'],
                depth=resource['unitary_depth'],parameter_sha256=phash,seconds=time.perf_counter()-begin,
                energy=8*(-obs['correlations'][1]+k*obs['correlations'][2]-h*obs['mx']),
                ed_fidelity=state_fidelity,mx=obs['mx'],m2_ferro=float(obs['structure_factor'][0]),
                m2_antiphase=float(obs['structure_factor'][2]),diagnostic=diag['label'],
                prep_c_max=float(np.max(abs(base['correlations']-ref['correlations']))),
                prep_sf_max=float(np.max(abs(base['structure_factor']-ref['structure_factor']))),
                prep_mx=base['mx']-ref['mx'],
                noise_c_max=float(np.max(abs(obs['correlations']-base['correlations']))),
                noise_sf_max=float(np.max(abs(obs['structure_factor']-base['structure_factor']))),
                noise_mx=obs['mx']-base['mx'],**checks)
            key=f'p{point:02d}_noise{p:g}'
            full[key+'_rho']=rho
            full[key+'_correlations']=obs['correlations'];full[key+'_structure_factor']=obs['structure_factor']
            full[key+'_prep_c']=base['correlations']-ref['correlations']
            full[key+'_prep_sf']=base['structure_factor']-ref['structure_factor']
            full[key+'_noise_c']=obs['correlations']-base['correlations']
            full[key+'_noise_sf']=obs['structure_factor']-base['structure_factor']
            rows.append(row)
            np.savez_compressed(out/f'{key}.npz',rho=rho,params=theta,ed_state=ed,
                correlations=obs['correlations'],structure_factor=obs['structure_factor'],
                ed_correlations=ref['correlations'],ed_structure_factor=ref['structure_factor'],
                epsilon_prep_c=full[key+'_prep_c'],epsilon_prep_sf=full[key+'_prep_sf'],
                delta_noise_c=full[key+'_noise_c'],delta_noise_sf=full[key+'_noise_sf'],
                epsilon_prep_mx=base['mx']-ref['mx'],delta_noise_mx=obs['mx']-base['mx'],mx=obs['mx'],
                q=2*np.pi*np.arange(8)/8,p=p,point=point)
            print(f"point={point} L={len(theta)} p={p} F_ED={state_fidelity:.5f} purity={checks['purity']:.5f} {row['seconds']:.2f}s {diag['label']}",flush=True)
        verification.append(dict(point=point,pure_highlevel_maxerror=float(np.max(abs(psi-high))),
            highlevel_decomposed_maxerror=float(np.max(abs(high-decomp))),
            parity_error=float(np.max(abs(psi-psi[::-1]))),
            normalization_error=float(abs(np.vdot(psi,psi)-1))))
    with (out/'observations.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'schedules.json').write_text(json.dumps(schedules,indent=2))
    (out/'verification.json').write_text(json.dumps(verification,indent=2))
    fig,axs=plt.subplots(2,5,figsize=(16,6.5),layout='constrained')
    colors=['#2563eb','#e08018','#bb3344']
    for j,point in enumerate(cfg['point_indices']):
        chosen_point=chosen[str(point)];run=chosen_point['best_run']
        ref=np.load(ROOT/'results/calibration_v1/runs'/f'{run}.npz')
        axs[0,j].plot(np.arange(8)/4,ref['ed_structure_factor'],'k--',label='ED',lw=1)
        group=[r for r in rows if r['point']==point]
        for r,color in zip(group,colors):
            sf=full[f"p{point:02d}_noise{r['p']:g}_structure_factor"]
            axs[0,j].plot(np.arange(8)/4,sf,'.-',color=color,label=f"p={r['p']}")
        axs[0,j].set(title=f"κ={chosen_point['kappa']}, h={chosen_point['h']}\nL={chosen_point['layers']}, CNOT={chosen_point['cnots']}",
                     xlabel='q / π',ylabel='m²(q)',ylim=(-.02,1.02))
        axs[1,j].plot(cfg['probabilities'],[r['ed_fidelity'] for r in group],'o-',label='ED overlap')
        axs[1,j].plot(cfg['probabilities'],[r['mx'] for r in group],'s-',label='Mx')
        axs[1,j].set(xlabel='p per CNOT target',ylim=(-.02,1.02))
    axs[0,0].legend(fontsize=8);axs[1,0].legend(fontsize=8)
    fig.suptitle('Actual gate-noise smoke test | fixed parameters per point | different depths across points')
    fig.savefig(out/'noise_comparison.png',dpi=170);fig.savefig(out/'noise_comparison.pdf');plt.close(fig)
    meta=dict(created_utc=datetime.now(timezone.utc).isoformat(),config=cfg,input_hashes=hashes,
        platform=platform.platform(),python=sys.version,
        versions={p:importlib.metadata.version(p) for p in ['pennylane','numpy','scipy','matplotlib']},
        elapsed_seconds=time.perf_counter()-start,density_simulation_seconds=sum(r['seconds'] for r in rows),
        point_count=5,circuit_runs=15,failures=[],retries=[],cache="none; exact configured representatives rerun",
        state_comparison="F_ED=<psi_ED|rho|psi_ED>, not a pure-state inner product",
        noise_comparison="signed arrays: epsilon_prep=O_circuit(0)-O_ED; delta_noise=O_circuit(p)-O_circuit(0)",
        compilation="literal CNOT-RZ-CNOT, same directions/parameters/counts for all p; target channel after each CNOT",
        connectivity=cfg['connectivity'],not_completed=["no phase boundary shift inference","no noisy retraining","no full grid"])
    (out/'metadata.json').write_text(json.dumps(meta,indent=2))
    lines=['# Actual gate-noise smoke test','',
        'Five calibrated representatives, three noise levels each; all 15 density-matrix simulations actually ran.',
        'No noisy reoptimization. Gate schedule and parameter hashes are identical across p at each point.',
        'Pure/high-level/decomposed and p=0 density comparisons passed; all density matrices passed trace, Hermiticity and PSD checks.','',
        '| κ | h | L | p | ED overlap | purity | Mx | prototype diagnostic |',
        '|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in rows:lines.append(f"|{r['kappa']}|{r['h']}|{r['layers']}|{r['p']}|{r['ed_fidelity']:.6f}|{r['purity']:.6f}|{r['mx']:.6f}|{r['diagnostic']}|")
    lines+=['','Selection reasons:']+[f"- Point {i}: {reason}" for i,reason in cfg['selection_reasons'].items()]
    lines+=['','Full signed preparation/noise errors are in each NPZ; scalar maxima are in observations.csv.',
        'All discrete wavevectors are saved. Mixed overlap means <psi_ED|rho|psi_ED>.',
        'Different depths across points confound a comparison of intrinsic phase robustness. These are smoke checks, not measured boundary shifts.',
        'At high accumulated noise, degraded/uncertain outputs are retained; they are not silently relabeled paramagnetic.',
        f"Measured total elapsed {meta['elapsed_seconds']:.3f} s; density evaluation/check sum {meta['density_simulation_seconds']:.3f} s.",
        '', '![Noise comparison](noise_comparison.png)']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
