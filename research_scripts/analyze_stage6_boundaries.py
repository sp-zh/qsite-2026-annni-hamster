import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_boundaries import compare,denominator
from annni.stage6_diagnostics import response_curves,peaks_and_primary
from annni.stage6_observation_analysis import ed_measurements
from annni.upgrade_gates import vector,observations
f=json.loads((OUT/'confirmation/method_frozen.json').read_text());refs=json.loads((OUT/'reference_atlas/window_reference.json').read_text());indices={}
for p in (OUT/'end_to_end').glob('windows_*_index.json'):
 for r in json.loads(p.read_text()):indices[(r['kappa'],r['h'])]=r
rows=[];curves={}
for ref in refs:
 k=ref['kappa'];h=np.array(ref['h']);n=8;name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';target=np.array(ref['values']);reference=peaks_and_primary(h,response_curves(h,target,n)[name]);ed_arrays=[np.load(ROOT/ed_measurements(n,k,float(x))['archive']) for x in h]
 for method in ['B3',f['physical_method']]:
  pure=np.array([vector(observations(load(k,float(x),method,task='windows')['state'],n)) for x in h]);p0=compare(h,pure,n,name,reference);rows.append(dict(kappa=k,method=method,p=0,estimator='pure_circuit',budget=None,repeat=None,**p0));curves[f'{k}_{method}_pure']=dict(h=h,values=pure,reference=target)
  for p in [0,.01,.05]:
   for est in ['raw','zne','zne_quadratic','sv']:
    selected=[]
    for x in h:
     entries=indices.get((k,float(x)),{}).get('entries',[]);chosen=next((e['record'] for e in entries if e['method']==method and e['estimator']==est and e['record']['p']==p),None);selected.append(chosen)
    if any(r is None for r in selected):
     rows.append(dict(kappa=k,method=method,p=p,estimator=est,budget=None,repeat=None,reference_resolvable=reference['resolvable'],algorithm_estimatable=False,matched=False,position_error=None,status='not_executed_complete_window',reference=reference));continue
    p0records=[next(e['record'] for e in indices[(k,float(x))]['entries'] if e['method']==method and e['estimator']==est and e['record']['p']==0) for x in h];p0arrays=[np.load(ROOT/r['archive']) for r in p0records]
    arrays=[np.load(ROOT/r['archive']) for r in selected];v=np.array([a['exact'] for a in arrays]);comp=compare(h,v,n,name,reference);rows.append(dict(kappa=k,method=method,p=p,estimator=est,budget=None,repeat=None,shift_from_known_circuit_p0=(comp['result']['primary']['coordinate']-p0['result']['primary']['coordinate']) if comp['result']['primary'] and p0['result']['primary'] else None,**comp));curves[f'{k}_{method}_{p}_{est}']=dict(h=h,values=v,reference=target)
    for b in PLAN['measurement']['budgets']:
     for rep in range(32):
      vv=np.array([a[f'samples_{b}'][rep] for a in arrays]);r=compare(h,vv,n,name,reference);edv=np.array([a[f'samples_{b}'][rep] for a in ed_arrays]);edr=compare(h,edv,n,name,reference);finitep0=compare(h,np.array([a[f'samples_{b}'][rep] for a in p0arrays]),n,name,reference);rawpos=r['raw_maximum_coordinate'];edpos=edr['raw_maximum_coordinate'];rows.append(dict(kappa=k,method=method,p=p,estimator=est,budget=b,repeat=rep,ED_finite_shot_reference=edr,circuit_p0_finite_shot_reference=finitep0,shift_from_finite_circuit_p0=rawpos-finitep0['raw_maximum_coordinate'] if rawpos is not None and finitep0['raw_maximum_coordinate'] is not None else None,raw_maximum_difference_from_finite_ED=rawpos-edpos if rawpos is not None and edpos is not None else None,shift_from_known_circuit_p0=rawpos-p0['raw_maximum_coordinate'] if rawpos is not None and p0['raw_maximum_coordinate'] is not None else None,**r))
 dump(OUT/'end_to_end/boundary_comparison.json',rows);dump(OUT/'end_to_end/boundary_curves.json',curves);print('boundary kappa',k,flush=True)
groups={}
for r in rows:groups.setdefault((r['method'],r['p'],r['estimator'],r['budget']),[]).append(r)
summary={str(key):denominator(v) for key,v in groups.items()};dump(OUT/'end_to_end/boundary_coverage.json',summary);dump(OUT/'end_to_end/boundary_matching_protocol.json',dict(position_tolerance=.05,rule='Largest non-endpoint SAME-named derivative; retain competing>=90% peaks and endpoint maxima; no nearest-reference peak pairing',all_requested_kappa=[r['kappa'] for r in refs],finite_shots='32 independent complete-window repetitions; every repeat including endpoints, ambiguity and failure retained. Raw-maximum differences also saved for unconditional distribution; not statistical confidence intervals.',smoothing=None,interpolation=None,reference='Same N8 PBC ED on identical coordinates; original coarse reference retained separately',cost='Each window replicate requires one prescribed total-budget experiment at every coordinate; no voting aggregation represented as a single-shot-budget map'))
