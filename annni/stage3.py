"""Stage 3 experiment storage and exact full-density gate backend.
Old modules/data are used unchanged. No density-sector reduction is performed.
"""
import json,hashlib,time,sys,platform,importlib.metadata
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from .model import Chain
from .circuits import HVAEngine,observe,resources
from .vqe import optimize,metrics
from .noise import check_schedule,density_checks
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage3_v1'
CFG=json.loads((ROOT/'configs/stage3_v1.json').read_text())
VERSIONS={p:importlib.metadata.version(p) for p in ['numpy','scipy','pennylane','matplotlib']}
def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def array_hash(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(obj,indent=2));temp.replace(path)
def fingerprint():
    files=['configs/stage3_v1.json','annni/model.py','annni/circuits.py','annni/vqe.py','annni/noise.py','annni/stage3.py','annni/diagnostics.py','configs/diagnostics_v1.json','requirements.lock.txt']
    return dict(sources={p:sha(ROOT/p) for p in files},versions=VERSIONS,n=8,basis='wire0 MSB')
def init_session():
    OUT.mkdir(exist_ok=True);path=OUT/'manifest.json';fp=fingerprint()
    if path.exists():
        assert json.loads(path.read_text())['fingerprint']==fp,'Stage 3 code/config fingerprint changed'
    else:dump(path,dict(started_utc=now(),fingerprint=fp,config=CFG,python=sys.version,platform=platform.platform()))
    return fp
def remaining_seconds():
    start=datetime.fromisoformat(json.loads((OUT/'manifest.json').read_text())['started_utc'])
    return CFG['wall_budget_minutes']*60-(datetime.now(timezone.utc)-start).total_seconds()
def guard():
    if remaining_seconds()<60:raise TimeoutError("Stage 3 budget reached; checkpoints preserved")
def reference(k,h):
    d=np.load(ROOT/'results/baseline/grid_n8.npz')
    ki=np.flatnonzero(np.isclose(d['kappa'],k));hi=np.flatnonzero(np.isclose(d['h'],h))
    if len(ki)==len(hi)==1 and h>0:
        s=d['states'][ki[0],hi[0]].copy();e=float(8*d['energy_per_site'][ki[0],hi[0]])
        assert np.isfinite(s).all()
        return s,e,'results/baseline/grid_n8.npz'
    path=OUT/'reference_supplement'/f'k{k:.3f}_h{h:.3f}.npz'
    if not path.exists():
        path.parent.mkdir(exist_ok=True);c=Chain(8);r=c.ground_state(k,h)
        np.savez_compressed(path,state=r.state,energy=r.energy,kappa=k,h=h,residual=r.residual,n=8)
    d=np.load(path);assert np.isclose(d['kappa'],k) and np.isclose(d['h'],h)
    return d['state'],float(d['energy']),str(path.relative_to(ROOT))
def random_init(seed,k,h,L):
    return np.random.default_rng(np.random.SeedSequence([seed,round(1000*k),round(1000*h),L])).uniform(-.5,.5,(L,3))
def run_opt(name,init,k,h,seed,group,source,maxiter=2000,prior_iterations=0,prior_seconds=0.):
    guard();start=time.perf_counter();fp=fingerprint()
    options=CFG['options']|{'maxiter':maxiter}
    key=dict(fingerprint=fp,kappa=k,h=h,L=len(init),seed=seed,options=options,initial_hash=array_hash(init))
    cacheid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest()
    cache=OUT/'optimization/cache'/cacheid;cache.parent.mkdir(parents=True,exist_ok=True)
    record=cache.with_suffix('.json');archive=cache.with_suffix('.npz')
    if record.exists():
        row=json.loads(record.read_text());assert row['key']==key and sha(archive)==row['archive_sha256']
        disposition='cached'
    else:
        ed,e,refsource=reference(k,h)
        status,final,state,trace=optimize(init,k,h,options)
        met,obs,ref=metrics(state,ed,e,k,h,CFG['thresholds'])
        row=dict(key=key,created_utc=now(),kappa=k,h=h,layers=len(init),seed=seed,reference_source=refsource,
                 **status)|met
        row['optimizer_success']=row['optimization_success']
        row['end_to_end_seconds']=time.perf_counter()-start
        np.savez_compressed(archive,initial_params=init,final_params=final,state=state,trace=trace,
            correlations=obs['correlations'],structure_factor=obs['structure_factor'],mx=obs['mx'],
            ed_state=ed,ed_energy=e,ed_correlations=ref['correlations'],ed_structure_factor=ref['structure_factor'],ed_mx=ref['mx'],
            q=2*np.pi*np.arange(8)/8)
        row['archive_sha256']=sha(archive);dump(record,row);disposition='executed'
    result=row|dict(name=name,group=group,source=source,archive=str(archive.relative_to(ROOT)),
                   cache_status=disposition,prior_iterations=prior_iterations,prior_seconds=prior_seconds,
                   cumulative_iterations=prior_iterations+row['nit'],
                   cumulative_seconds=prior_seconds+row['end_to_end_seconds'])
    alias=OUT/'optimization/records'/f'{name}.json'
    if alias.exists():
        old=json.loads(alias.read_text());assert old['key']==key
        result['original_cache_status']=old.get('original_cache_status',old['cache_status'])
    dump(alias,result)
    return result,np.load(archive)['final_params'].copy()
def dense_literal(theta,p):
    """Full 256x256 rho, apply original source-ordered CNOT,RZ,CNOT,RX.
    Each target depolarization uses (1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ).
    No gates are canceled and no output symmetrization/normalization is applied.
    """
    n=8;dim=256;ids=np.arange(dim)
    z=1-2*((ids[:,None]>>np.arange(7,-1,-1))&1)
    flips=[ids^(1<<(7-i)) for i in range(n)]
    signs=[z[:,i,None]*z[None,:,i] for i in range(n)]
    cnots={(i,(i+d)%n):ids ^ (((ids>>(7-i))&1) << (7-(i+d)%n)) for d in [1,2] for i in range(n)}
    rho=np.ones((dim,dim),dtype=complex)/dim # exact H^⊗8 |0><0| H^⊗8
    def channel(r,t):
        if p==0:return r # identity channel is evaluated; gate schedule unchanged
        f=flips[t];flipped=r[np.ix_(f,f)];sign=signs[t]
        return (1-p)*r+(p/3)*(flipped+sign*flipped+sign*r)
    for gamma,eta,beta in theta:
        for distance,angle in [(1,gamma),(2,eta)]:
            for control in range(n):
                target=(control+distance)%n;perm=cnots[control,target]
                rho=rho[np.ix_(perm,perm)];rho=channel(rho,target)
                phase=np.exp(-1j*angle*z[:,target])
                rho=phase[:,None]*rho*phase.conj()[None,:]
                rho=rho[np.ix_(perm,perm)];rho=channel(rho,target)
        c,s=np.cos(beta),np.sin(beta)
        for wire in range(n):
            f=flips[wire]
            rho=c*rho-1j*s*rho[f,:]
            rho=c*rho+1j*s*rho[:,f]
    return rho
def run_noise(row,p,group,keep_density=False):
    guard();begin=time.perf_counter()
    opt=np.load(ROOT/row['archive']);theta=opt['final_params'];k=row['kappa'];h=row['h']
    key=dict(fingerprint=fingerprint(),params_sha256=array_hash(theta),kappa=k,h=h,L=len(theta),p=p,
             backend='dense_literal full256',compile='original no cancellation',model=CFG['model'])
    cacheid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest()
    path=OUT/'density_cache'/cacheid;path.parent.mkdir(exist_ok=True)
    meta=path.with_suffix('.json');archive=path.with_suffix('.npz')
    if meta.exists():
        result=json.loads(meta.read_text());assert result['key']==key and result['archive_sha256']==sha(archive)
        with np.load(archive) as saved:
            enough=not keep_density or 'rho' in saved.files
        if enough:return result|dict(cache_status='cached',archive=str(archive.relative_to(ROOT)))
    check_schedule(theta,p)
    t=time.perf_counter();rho=dense_literal(theta,p);evolve_seconds=time.perf_counter()-t
    t=time.perf_counter();checks=density_checks(rho)
    eig=np.linalg.eigvalsh(rho)
    obs=observe(rho);ed=opt['ed_state'];ref=observe(ed);pure=observe(opt['state'])
    if p==0:np.testing.assert_allclose(rho,np.outer(opt['state'],opt['state'].conj()),atol=1e-10)
    sf=obs['structure_factor'];c=obs['correlations'];mx=obs['mx']
    energy=8*(-c[1]+k*c[2]-h*mx)
    np.testing.assert_allclose(c[0],1,atol=1e-10)
    np.testing.assert_allclose(sf,np.fft.fft(c).real/8,atol=1e-12)
    from .diagnostics import diagnose
    diagnostic=diagnose(sf,mx)
    resource=resources(8,len(theta))
    result=dict(key=key,kappa=k,h=h,layers=len(theta),p=p,energy=float(energy),mx=mx,
        fidelity_ed=float(np.vdot(ed,rho@ed).real),**checks,
        r_mix=(checks['purity']-1/256)/(1-1/256),d_mix=float(np.sum(abs(eig-1/256))/2),
        cnot_count=resource['cnots'],depth=resource['unitary_depth'],target_counts=resource['target_counts'],
        params_sha256=key['params_sha256'],preparation_failed=not row['joint_pass'],
        diagnostic_uncertain=diagnostic['label']=='uncertain',noise_degraded=p>0 and diagnostic['label']=='degraded',
        branch_sensitive=False,numerical_error=False,diagnostic=diagnostic['label'],
        epsilon_c_total=float(np.max(abs(c-ref['correlations']))),
        epsilon_sf_total=float(np.max(abs(sf-ref['structure_factor']))),epsilon_mx_total=abs(mx-ref['mx']),
        epsilon_c_noise=float(np.max(abs(c-pure['correlations']))),
        epsilon_sf_noise=float(np.max(abs(sf-pure['structure_factor']))),epsilon_mx_noise=abs(mx-pure['mx']),
        evolution_seconds=evolve_seconds,postprocess_seconds=time.perf_counter()-t,
        source_optimization=row['name'],group_first_evaluated=group,created_utc=now())
    arrays=dict(params=theta,correlations=c,structure_factor=sf,mx=mx,q=2*np.pi*np.arange(8)/8,
        ed_correlations=ref['correlations'],ed_structure_factor=ref['structure_factor'],ed_mx=ref['mx'],
        prep_c=pure['correlations']-ref['correlations'],prep_sf=pure['structure_factor']-ref['structure_factor'],prep_mx=pure['mx']-ref['mx'],
        noise_c=c-pure['correlations'],noise_sf=sf-pure['structure_factor'],noise_mx=mx-pure['mx'],
        total_c=c-ref['correlations'],total_sf=sf-ref['structure_factor'],total_mx=mx-ref['mx'])
    for field in ['c','sf','mx']:np.testing.assert_allclose(arrays['total_'+field],arrays['prep_'+field]+arrays['noise_'+field],atol=1e-12)
    if keep_density:arrays['rho']=rho
    np.savez_compressed(archive,**arrays)
    result['end_to_end_seconds']=time.perf_counter()-begin;result['archive_sha256']=sha(archive)
    dump(meta,result)
    return result|dict(cache_status='executed',archive=str(archive.relative_to(ROOT)))
def write_csv(path,rows):
    import csv
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k,v in r.items() if not isinstance(v,dict)))
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items() if k in keys})
