import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from annni.stage4 import *

def main():
    audit=read(OUT/'verification/initial_audit.json');skipped=[];runtime_caches=[]
    for name,digest in audit['protected_sha256'].items():
        p=ROOT/name
        if '__pycache__' in p.parts or p.suffix=='.pyc':
            runtime_caches.append(name);continue
        if not p.exists() and name=='results/calibration_v1/notebook_execution.log' and (ROOT/'PACKAGE_EXCLUSIONS.json').exists():skipped.append(name);continue
        assert sha(p)==digest,name
    opt=0;dens=0;pzero=0
    for p in (OUT/'optimization').glob('*.json'):
        r=read(p);assert sha(ROOT/r['archive'])==r['archive_sha256'];d=np.load(ROOT/r['archive']);np.testing.assert_allclose(HVAEngine().state(d['final_params']),d['state'],atol=1e-11);opt+=1
    for p in (OUT/'density').glob('*.json'):
        r=read(p);assert sha(ROOT/r['archive'])==r['archive_sha256'];d=np.load(ROOT/r['archive']);c=d['correlations'];sf=d['structure_factor'];mx=float(d['mx'])
        assert abs(r['trace_real']-1)<1e-10 and abs(r['trace_imag'])<1e-10 and r['hermiticity_error']<1e-10 and r['min_eigenvalue']>=-1e-10
        np.testing.assert_allclose(c[0],1,atol=1e-10);np.testing.assert_allclose(sf,np.fft.fft(c).real/8,atol=1e-12)
        np.testing.assert_allclose(r['energy']/8,-c[1]+r['kappa']*c[2]-r['h']*mx,atol=1e-11)
        if r['p']==0:
            state=HVAEngine().state(d['params']);rho=dense_literal(d['params'],0);np.testing.assert_allclose(rho,np.outer(state,state.conj()),atol=1e-10);np.testing.assert_allclose(observe(rho)['correlations'],c,atol=1e-11);pzero+=1
        dens+=1
    refs=set()
    def walk(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k in ['archive','selection_archive','source','reference_source'] and isinstance(v,str) and v.startswith('results/'):
                    assert (ROOT/v).is_file(),v;refs.add(v)
                walk(v)
        elif isinstance(o,list):
            for v in o:walk(v)
    for p in OUT.rglob('*.json'):
        if 'source_before' not in p.parts:walk(read(p))
    result=dict(passed=True,protected_unchanged=len(audit['protected_sha256'])-len(skipped)-len(runtime_caches),omitted_old_nonessential_logs=skipped,excluded_runtime_caches=runtime_caches,optimization_reloaded=opt,new_density_archives=dens,new_p0_full_density_recomputed=pzero,relative_references_checked=len(refs),physics_fingerprint=physical_fp(),timestamp=now())
    dump(OUT/'verification/verification.json',result);print({k:v for k,v in result.items() if k!='physics_fingerprint'})
if __name__=='__main__':main()
