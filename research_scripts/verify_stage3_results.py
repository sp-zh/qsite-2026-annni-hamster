import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json,numpy as np
from annni.stage3 import *

def main():
    init_session();audit=json.loads((OUT/'verification/input_audit.json').read_text())
    omitted=[]
    for p,digest in audit['protected_sha256'].items():
        if not (ROOT/p).exists() and p=='results/calibration_v1/notebook_execution.log' and (ROOT/'PACKAGE_EXCLUSIONS.json').exists():
            omitted.append(p);continue
        assert sha(ROOT/p)==digest,p
    for L in [2,4,6]:dump(OUT/f'verification/gate_schedule_L{L}.json',resources(8,L))
    checked=0;density=0;maxtrace=0.;maxherm=0.;mineig=1.
    for p in (OUT/'optimization/cache').glob('*.json'):
        r=json.loads(p.read_text());assert sha(p.with_suffix('.npz'))==r['archive_sha256'];checked+=1
        d=np.load(p.with_suffix('.npz'));state=HVAEngine().state(d['final_params'])
        np.testing.assert_allclose(state,d['state'],atol=1e-10)
    for p in (OUT/'density_cache').glob('*.json'):
        r=json.loads(p.read_text());assert sha(p.with_suffix('.npz'))==r['archive_sha256'];density+=1
        d=np.load(p.with_suffix('.npz'));c=d['correlations'];sf=d['structure_factor']
        np.testing.assert_allclose(r['energy']/8,-c[1]+r['kappa']*c[2]-r['h']*float(d['mx']),atol=1e-11)
        np.testing.assert_allclose(sf,np.fft.fft(c).real/8,atol=1e-11)
        for f in ['c','sf','mx']:np.testing.assert_allclose(d['total_'+f],d['prep_'+f]+d['noise_'+f],atol=1e-12)
        assert r['cnot_count']==32*r['layers'];assert sum(r['target_counts'].values())==r['cnot_count'] if isinstance(r['target_counts'],dict) else sum(r['target_counts'])==r['cnot_count']
    for group in ['slices','grid']:
        f=OUT/group/'observations.json'
        if not f.exists():continue
        rows=json.loads(f.read_text());a=np.load(OUT/group/'arrays.npz')
        for r in rows:
            group_rows=[x for x in rows if x['kappa']==r['kappa'] and x['h']==r['h'] and x['layers']==r['layers']]
            assert len(set(x['params_sha256'] for x in group_rows))==1
            ix=([4,6].index(r['layers']),[0,.3,.8].index(r['kappa']),round(r['h']/.05)-1,[0,.01,.05].index(r['p'])) if group=='slices' else (round(r['kappa']/.05),round(r['h']/.1)-1,[0,.01,.05].index(r['p']))
            np.testing.assert_allclose(a['structure_factor'][ix],np.load(ROOT/r['archive'])['structure_factor'])
    result=dict(passed=True,protected_files_unchanged=len(audit['protected_sha256'])-len(omitted),packaged_nonessential_log_omissions=omitted,optimization_archives_recomputed=checked,density_archives_hash_and_identities=density,completed_utc=now())
    dump(OUT/'verification/result_audit.json',result);print(result)
if __name__=='__main__':main()
