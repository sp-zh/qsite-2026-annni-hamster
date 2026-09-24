import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json,numpy as np
from annni.stage3 import *

def main():
    init_session()
    coverage=json.loads((OUT/'slices/coverage.json').read_text())
    qualifying=[int(L) for L,v in coverage.items() if v['passed']/v['total']>=.9]
    verified='33 passed' in (OUT/'verification/regression_tests.txt').read_text()
    if not qualifying or not verified:
        dump(OUT/'grid/execution.json',dict(status='not_started',reason='coverage or technical gate failed',coverage=coverage,verified=verified));return
    L=max(qualifying,key=lambda L:(coverage[str(L)]['passed'],-32*L))
    decision=dict(created_utc=now(),layers=L,coverage=coverage,technical_verified=verified,
        diagnostic_scope='Continuous observables and masks only; unresolved or unchecked branch neighborhoods cannot support boundary claims',
        resource_remaining_seconds=remaining_seconds(),estimated_seconds=1200,estimate_basis='Measured slice optimization and density timings, conservative allowance',
        selection='maximum noiseless joint coverage then lowest CNOT',kappa=[0,1,.05],h=[.1,2,.1])
    if remaining_seconds()<1500:
        dump(OUT/'grid/execution.json',dict(status='not_started',reason='insufficient reserved budget',decision=decision));return
    path=OUT/'grid/decision_frozen.json'
    if not path.exists():dump(path,decision)
    else:assert json.loads(path.read_text())['layers']==L
    slices=json.loads((OUT/'slices/selection_frozen.json').read_text())['rows']
    chains=json.loads((OUT/'slices/optimization_rows.json').read_text())
    hs=np.round(np.arange(1,21)*.1,2);allrows=[];selected=[]
    for k in np.round(np.arange(21)*.05,2):
        if any(np.isclose(k,v) for v in [0,.3,.8]):
            selected.extend([r|{'grid_parameter_source':'exact slice selection'} for r in slices if np.isclose(r['kappa'],k) and r['layers']==L and any(np.isclose(r['h'],v) for v in hs)])
            continue
        local=[]
        for direction in ['ascending','descending']:
            fields=hs if direction=='ascending' else hs[::-1]
            for seed in [101,211,307]:
                nearest=min([0,.3,.8],key=lambda v:abs(v-k));endpoint=float(fields[0])
                src=next(r for r in chains if r['kappa']==nearest and r['layers']==L and r['seed']==seed and r['group']=='C_'+direction and np.isclose(r['h'],endpoint))
                theta=np.load(ROOT/src['archive'])['final_params'];source=src['archive'];iterations=0;seconds=0.
                for h in fields:
                    row,theta=run_opt(f'G_k{k:.2f}_L{L}_{direction}_s{seed}_h{h:.2f}',theta,float(k),float(h),seed,'G_'+direction,source,2000,iterations,seconds)
                    local.append(row);allrows.append(row);source=row['archive'];iterations=row['cumulative_iterations'];seconds=row['cumulative_seconds']
        previous=None
        for h in hs:
            best=min([r for r in local if np.isclose(r['h'],h)],key=lambda r:r['energy'])
            direction=best['group'].split('_',1)[1];branch=direction+f"_s{best['seed']}"
            selected.append(best|dict(direction=direction,branch=branch,branch_switch=previous is not None and branch!=previous,grid_parameter_source='independent seeded continuation'))
            previous=branch
        print('Grid optimization kappa',k,'selected pass',sum(r['joint_pass'] for r in selected if np.isclose(r['kappa'],k)),'/20',flush=True)
    dump(OUT/'grid/optimization_rows.json',allrows);write_csv(OUT/'grid/optimization_rows.csv',allrows)
    frozen=OUT/'grid/selection_frozen.json'
    if frozen.exists():assert [r['archive'] for r in json.loads(frozen.read_text())['rows']]==[r['archive'] for r in selected]
    else:dump(frozen,dict(created_utc=now(),rows=selected,criterion='noiseless energy only; frozen before grid density evaluation'))
    write_csv(OUT/'grid/selected.csv',selected)
    slice_quality=json.loads((OUT/'slices/observations.json').read_text())
    results=[]
    for i,r in enumerate(selected):
        for p in [0,.01,.05]:
            n=run_noise(r,p,'G');n.update(direction=r['direction'],branch=r['branch'],branch_switch=r['branch_switch'],branch_sensitive=None,branch_checked=False,selected_optimization=r['name'])
            prior=next((v for v in slice_quality if v['params_sha256']==n['params_sha256'] and v['kappa']==n['kappa'] and v['h']==n['h'] and v['p']==p),None)
            if prior is not None:n.update(branch_sensitive=prior['branch_sensitive'],branch_checked=prior['branch_checked'])
            results.append(n);dump(OUT/'grid/noise_records'/f"k{r['kappa']:.2f}_h{r['h']:.2f}_p{p}.json",n)
        if i%20==19:print('Grid density',i+1,'/420',flush=True)
    dump(OUT/'grid/observations.json',results);write_csv(OUT/'grid/observations.csv',results)
    arrays={key:np.empty((21,20,3,8)) for key in ['correlations','structure_factor','prep_c','prep_sf','noise_c','noise_sf','total_c','total_sf']}
    for key in ['mx','purity','r_mix','d_mix','energy','fidelity_ed','preparation_failed']:arrays[key]=np.empty((21,20,3))
    for r in results:
        ix=(round(r['kappa']/.05),round(r['h']/.1)-1,[0,.01,.05].index(r['p']));d=np.load(ROOT/r['archive'])
        for key in arrays:arrays[key][ix]=d[key] if key in d else r[key]
    np.savez_compressed(OUT/'grid/arrays.npz',**arrays,kappa=np.round(np.arange(21)*.05,2),h=hs,p=[0,.01,.05],q=2*np.pi*np.arange(8)/8,layers=L)
    dump(OUT/'grid/execution.json',dict(status='complete',layers=L,points=len(selected),evaluations=len(results),joint_pass=sum(r['joint_pass'] for r in selected),noise_executed=sum(r['cache_status']=='executed' for r in results),noise_cached=sum(r['cache_status']=='cached' for r in results),new_optimization_records=len(allrows)))
if __name__=='__main__':main()
