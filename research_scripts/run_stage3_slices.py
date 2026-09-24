import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json,time
import numpy as np
from annni.stage3 import *

def optimize_slices():
    allrows=[]
    hs=np.round(np.arange(1,41)*.05,2)
    for k in [0.,.3,.8]:
        for L in [4,6]:
            for direction in ['ascending','descending']:
                fields=hs if direction=='ascending' else hs[::-1]
                for seed in [101,211,307]:
                    source='independent chain endpoint';theta=None;iterations=0;seconds=0.
                    for h in fields:
                        if theta is None:theta=random_init(seed,k,h,L)
                        name=f'C_k{k:.2f}_L{L}_{direction}_s{seed}_h{h:.2f}'
                        row,theta=run_opt(name,theta,k,float(h),seed,'C_'+direction,source,2000,iterations,seconds)
                        allrows.append(row);source=row['archive'];iterations=row['cumulative_iterations'];seconds=row['cumulative_seconds']
                    print('C chain complete',k,L,direction,seed,'pass',sum(r['joint_pass'] for r in allrows[-40:]),'/40',flush=True)
    dump(OUT/'slices/optimization_rows.json',allrows);write_csv(OUT/'slices/optimization_rows.csv',allrows)
    selected=[];directional=[];alternates=[]
    for k in [0.,.3,.8]:
        for L in [4,6]:
            previous=None;curve=[]
            for h in hs:
                g=[r for r in allrows if r['kappa']==k and r['layers']==L and np.isclose(r['h'],h)]
                best=min(g,key=lambda r:r['energy'])
                direction=best['group'].split('_',1)[1]
                branch=direction+f"_s{best['seed']}"
                alt=min([r for r in g if r['group']!=best['group']],key=lambda r:r['energy'])
                best=best|dict(direction=direction,branch=branch,branch_switch=previous is not None and previous!=branch)
                psi=np.load(ROOT/best['archive'])['state'];other=np.load(ROOT/alt['archive'])['state']
                best['opposite_direction_infidelity']=float(max(0.,1-abs(np.vdot(psi,other))**2))
                best['opposite_direction_archive']=alt['archive']
                selected.append(best);curve.append((best,alt));previous=branch
                for d in ['ascending','descending']:
                    db=min([r for r in g if r['group']=='C_'+d],key=lambda r:r['energy'])
                    directional.append(db|dict(direction=d))
            candidates=[pair for pair in curve if pair[0]['branch_switch']]
            if not candidates:candidates=curve
            ranked=sorted(candidates,key=lambda pair:pair[0]['opposite_direction_infidelity'],reverse=True)
            for best,alt in ranked[:2]:alternates.append(dict(selected=best,alternate=alt))
    frozen=dict(created_utc=now(),selection='min noiseless energy across six independent direction/seed chains',
                rows=selected,alternate_locations=alternates)
    path=OUT/'slices/selection_frozen.json'
    if path.exists():
        old=json.loads(path.read_text())
        assert [r['archive'] for r in old['rows']]==[r['archive'] for r in selected]
    else:dump(path,frozen)
    write_csv(OUT/'slices/selected.csv',selected);write_csv(OUT/'slices/direction_best.csv',directional)
    print('C selected coverage',[(L,sum(r['joint_pass'] for r in selected if r['layers']==L),120) for L in [4,6]],flush=True)
    return frozen

def simulate(frozen):
    results=[]
    for i,r in enumerate(frozen['rows']):
        for p in [0,.01,.05]:
            n=run_noise(r,p,'C')
            n.update(direction=r['direction'],branch=r['branch'],branch_switch=r['branch_switch'],
                     selected_optimization=r['name'],branch_sensitive=None,branch_checked=False)
            results.append(n)
            dump(OUT/'slices/noise_records'/f"{r['name']}_p{p}.json",n)
        if i%10==9:print('C noise selected states',i+1,'/240',flush=True)
    sensitivities=[]
    for pair in frozen['alternate_locations']:
        chosen=pair['selected'];alt=pair['alternate']
        for p in [0,.01,.05]:
            a=next(r for r in results if r['source_optimization']==chosen['name'] and r['p']==p)
            b=run_noise(alt,p,'C_alternate')
            da=np.load(ROOT/a['archive']);db=np.load(ROOT/b['archive'])
            ec=float(np.max(abs(da['correlations']-db['correlations'])))
            esf=float(np.max(abs(da['structure_factor']-db['structure_factor'])))
            em=abs(float(da['mx']-db['mx']))
            sensitive=ec>.02 or esf>.02 or em>.02
            a['branch_checked']=True;a['branch_sensitive']=bool(sensitive)
            sensitivities.append(dict(kappa=chosen['kappa'],h=chosen['h'],layers=chosen['layers'],p=p,
                main_name=chosen['name'],alternate_name=alt['name'],main_archive=a['archive'],alternate_archive=b['archive'],
                max_c_difference=ec,max_sf_difference=esf,mx_difference=em,branch_sensitive=sensitive,
                description='preparation_protocol_sensitivity; not a statistical error or physical hysteresis'))
    for r in results:dump(OUT/'slices/noise_records'/f"{r['selected_optimization']}_p{r['p']}.json",r)
    dump(OUT/'slices/observations.json',results);write_csv(OUT/'slices/observations.csv',results)
    dump(OUT/'slices/preparation_protocol_sensitivity.json',sensitivities);write_csv(OUT/'slices/preparation_protocol_sensitivity.csv',sensitivities)
    # Explicit array order [L_index,kappa_index,h_index,p_index,(r/q)].
    shape=(2,3,40,3)
    arrays={key:np.empty(shape+(8,)) for key in ['correlations','structure_factor','prep_c','prep_sf','noise_c','noise_sf','total_c','total_sf']}
    for key in ['mx','purity','r_mix','d_mix','energy','fidelity_ed']:
        arrays[key]=np.empty(shape)
    arrays['preparation_failed']=np.empty(shape,dtype=bool)
    for r in results:
        ix=([4,6].index(r['layers']),[0.,.3,.8].index(r['kappa']),round(r['h']/.05)-1,[0,.01,.05].index(r['p']))
        d=np.load(ROOT/r['archive'])
        for key in ['correlations','structure_factor','prep_c','prep_sf','noise_c','noise_sf','total_c','total_sf']:arrays[key][ix]=d[key]
        for key in ['mx','purity','r_mix','d_mix','energy','fidelity_ed','preparation_failed']:arrays[key][ix]=r[key]
    np.savez_compressed(OUT/'slices/arrays.npz',**arrays,layers=[4,6],kappa=[0,.3,.8],h=np.round(np.arange(1,41)*.05,2),p=[0,.01,.05],q=2*np.pi*np.arange(8)/8)
    print('C complete: 720 main +',len(sensitivities),'alternate evaluations',flush=True)
if __name__=='__main__':
    init_session()
    assert (OUT/'matched_noise/observations.json').exists(),'Finish A/B before C'
    frozen=optimize_slices();simulate(frozen)
