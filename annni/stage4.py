"""Stage4 storage: physical, selection and diagnostic identities remain separate."""
import json,hashlib,time,sys,platform
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from .stage3 import dense_literal,sha,array_hash,dump,write_csv,VERSIONS
from .circuits import HVAEngine,observe,resources
from .noise import check_schedule,density_checks
from .vqe import optimize,metrics
from .model import Chain
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage4_v1';OLD=ROOT/'results/stage3_v1'
CFG=json.loads((ROOT/'configs/stage4_v1.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.now(timezone.utc).isoformat()
def guard():
    elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(read(OUT/'session.json')['started_utc'])).total_seconds()
    if elapsed>5340:raise TimeoutError('Stage4 wall budget reached; checkpoint files preserved')
def physical_fp():return {'sources':{p:sha(ROOT/p) for p in ['annni/model.py','annni/circuits.py','annni/noise.py','annni/stage3.py']},'versions':VERSIONS,'basis':'wire0 MSB','n':8,'compile':'literal unchanged NN NNN RX, target channel after every CNOT'}
def coord_id(k,h):return f'k{float(k).hex()}_h{float(h).hex()}'
def params(row):
    p=ROOT/row['archive']
    if 'archive_sha256' in row:assert sha(p)==row['archive_sha256']
    return np.load(p)['final_params'].copy()
def branch_id(row):
    direction=row.get('direction',row.get('group','').split('_',1)[-1])
    return f"stage3_slices/k{row['kappa']}/L{row['layers']}/{direction}/seed{row['seed']}/independent_endpoint"
def fail_metrics(r):
    return [k for k in ['delta_e','epsilon_c','epsilon_sf','epsilon_mx'] if r[k]>CFG['thresholds'][k]]+(['fidelity'] if r['fidelity']<CFG['thresholds']['fidelity'] else [])
def reference(k,h):
    grid=np.load(ROOT/'results/baseline/grid_n8.npz');ki=np.flatnonzero(np.isclose(grid['kappa'],k,atol=1e-12,rtol=0));hi=np.flatnonzero(np.isclose(grid['h'],h,atol=1e-12,rtol=0))
    if len(ki)==len(hi)==1:return grid['states'][ki[0],hi[0]],float(grid['energy_per_site'][ki[0],hi[0]]*8),'results/baseline/grid_n8.npz'
    old=OLD/'reference_supplement'/f'k{k:.3f}_h{h:.3f}.npz'
    if old.exists():
        d=np.load(old)
        if abs(float(d['h'])-h)<1e-12:return d['state'],float(d['energy']),str(old.relative_to(ROOT))
    p=OUT/'reference_supplement'/(coord_id(k,h)+'.npz');p.parent.mkdir(exist_ok=True)
    if not p.exists():
        r=Chain(8).ground_state(k,h);np.savez_compressed(p,state=r.state,energy=r.energy,kappa=k,h=h,residual=r.residual)
    d=np.load(p);return d['state'],float(d['energy']),str(p.relative_to(ROOT))
def run_opt(name,theta,k,h,seed,source,maxiter=4000):
    guard();path=OUT/'optimization'/name;path.parent.mkdir(exist_ok=True)
    key={'physics':physical_fp(),'initial':array_hash(theta),'coordinate':coord_id(k,h),'seed':seed,'options':CFG['optimizer_options']|{'maxiter':maxiter},'optimizer_source':sha(ROOT/'annni/vqe.py')}
    if path.with_suffix('.json').exists():
        r=read(path.with_suffix('.json'));assert r['key']==key and sha(ROOT/r['archive'])==r['archive_sha256'];return r|{'cache_status':'cached'}
    start=time.perf_counter();ed,e,ref=reference(k,h);status,final,state,trace=optimize(theta,k,h,key['options']);met,o,eo=metrics(state,ed,e,k,h,CFG['thresholds'])
    archive=path.with_suffix('.npz');np.savez_compressed(archive,initial_params=theta,final_params=final,state=state,trace=trace,ed_state=ed,ed_energy=e,correlations=o['correlations'],structure_factor=o['structure_factor'],mx=o['mx'],ed_correlations=eo['correlations'],ed_structure_factor=eo['structure_factor'],ed_mx=eo['mx'])
    r=dict(key=key,name=name,kappa=k,h=h,layers=len(theta),seed=seed,source=source,reference_source=ref,archive=str(archive.relative_to(ROOT)),archive_sha256=sha(archive),end_to_end_seconds=time.perf_counter()-start,cache_status='executed',created_utc=now(),**status)|met
    r['failed_metrics']=fail_metrics(r);dump(path.with_suffix('.json'),r);return r
_OLD_INDEX=None

def noise(row,p,keep=False):
    global _OLD_INDEX
    guard();theta=params(row);ph=array_hash(theta);k=float(row['kappa']);h=float(row['h']);key=dict(physics=physical_fp(),params=ph,coordinate=coord_id(k,h),p=float(p))
    digest=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();path=OUT/'density'/digest;path.parent.mkdir(exist_ok=True)
    if path.with_suffix('.json').exists():
        r=read(path.with_suffix('.json'));assert r['key']==key and sha(ROOT/r['archive'])==r['archive_sha256']
        if not keep or 'rho' in np.load(ROOT/r['archive']):return r|{'cache_status':'cached_stage4'}
    if _OLD_INDEX is None:
        _OLD_INDEX={}
        for f in (OLD/'density_cache').glob('*.json'):
            r=read(f);_OLD_INDEX[(r['params_sha256'],float(r['kappa']),float(r['h']),float(r['p']))]=(r,f)
    old=_OLD_INDEX.get((ph,k,h,float(p)))
    if old:
        r,f=old;archive=f.with_suffix('.npz');assert sha(archive)==r['archive_sha256']
        # Verify historical physics source/version fingerprint, not derived flags.
        for src,d in physical_fp()['sources'].items():assert r['key']['fingerprint']['sources'][src]==d
        assert r['key']['fingerprint']['versions']==VERSIONS
        if not keep or 'rho' in np.load(archive):return r|{'archive':str(archive.relative_to(ROOT)),'cache_status':'reused_stage3','physical_key':key}
    start=time.perf_counter();schedule=check_schedule(theta,p);rho=dense_literal(theta,p);checks=density_checks(rho);o=observe(rho);psi=HVAEngine().state(theta)
    if p==0:np.testing.assert_allclose(rho,np.outer(psi,psi.conj()),atol=1e-10)
    ed,e,ref=reference(k,h);eo=observe(ed);pure=observe(psi);c=o['correlations'];sf=o['structure_factor'];mx=o['mx'];energy=8*(-c[1]+k*c[2]-h*mx)
    np.testing.assert_allclose(c[0],1,atol=1e-10);np.testing.assert_allclose(sf,np.fft.fft(c).real/8,atol=1e-12)
    arrays={'params':theta,'correlations':c,'structure_factor':sf,'mx':mx,'q':np.arange(8)*2*np.pi/8}
    for short,long in [('c','correlations'),('sf','structure_factor'),('mx','mx')]:
        arrays['prep_'+short]=pure[long]-eo[long];arrays['noise_'+short]=o[long]-pure[long];arrays['total_'+short]=o[long]-eo[long]
    if keep:arrays.update(rho=rho,ideal_state=psi,ed_state=ed)
    archive=path.with_suffix('.npz');np.savez_compressed(archive,**arrays)
    eig=np.linalg.eigvalsh(rho);r=dict(key=key,archive=str(archive.relative_to(ROOT)),archive_sha256=sha(archive),kappa=k,h=h,layers=len(theta),p=p,params_sha256=ph,energy=energy,mx=mx,fidelity_ed=float(np.vdot(ed,rho@ed).real),r_mix=(checks['purity']-1/256)/(1-1/256),d_mix=float(np.sum(abs(eig-1/256))/2),cnot_count=schedule['cnots'],target_counts=schedule['target_counts'],end_to_end_seconds=time.perf_counter()-start,cache_status='executed',created_utc=now(),**checks)
    dump(path.with_suffix('.json'),r);return r

def compare(a,b,p):
    assert a['kappa']==b['kappa'] and abs(a['h']-b['h'])<1e-12 and a['layers']==b['layers'],'Pair must share k,h,L'
    ra=noise(a,p);rb=noise(b,p);da=np.load(ROOT/ra['archive']);db=np.load(ROOT/rb['archive'])
    diff={key:(db[key]-da[key]).tolist() for key in ['correlations','structure_factor','mx']}
    ec=float(np.max(abs(np.array(diff['correlations']))));es=float(np.max(abs(np.array(diff['structure_factor']))));em=abs(float(diff['mx']))
    return dict(p=p,h=a['h'],pair_complete=True,both_preparations_pass=bool(a['joint_pass'] and b['joint_pass']),actual_switch_pair_checked=True,actual_switch_pair_sensitive=max(ec,es,em)>.02,comparison_parameter_hashes=[ra['params_sha256'],rb['params_sha256']],comparison_metrics=dict(epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,signed=diff),density_a=ra,density_b=rb)
