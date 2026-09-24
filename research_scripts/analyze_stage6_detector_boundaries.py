"""Frozen prototype-contrast responses versus independent named ED order-response features."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_observation_analysis import wall_estimates
from annni.stage6_detector import predict as d4
from annni.stage6_wall_features import predict as d5,features
from annni.stage6_diagnostics import response_curves,peaks_and_primary
from annni.stage6_boundaries import denominator
f=json.loads((OUT/'confirmation/method_frozen.json').read_text());indices={}
for p in (OUT/'end_to_end').glob('windows_*_index.json'):
 for r in json.loads(p.read_text()):indices[(r['kappa'],r['h'])]=r
refs=json.loads((OUT/'reference_atlas/window_reference.json').read_text());rows=[]
for ref in refs:
 k=ref['kappa'];h=np.array(ref['h']);order=0 if k<.5 else 1;name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';reference=peaks_and_primary(h,response_curves(h,np.array(ref['values']),8)[name]);rp=reference['primary']
 for method in ['B3',f['physical_method']]:
  for p in [0,.01,.05]:
   for est in ['raw','zne','zne_quadratic','sv']:
    rs=[]
    for x in h:rs.append(next((e['record'] for e in indices.get((k,float(x)),{}).get('entries',[]) if e['method']==method and e['estimator']==est and e['record']['p']==p),None))
    for detector in ['D4','D5']:
     if any(r is None for r in rs) or (detector=='D5' and est=='sv'):
      rows.append(dict(kappa=k,method=method,p=p,estimator=est,detector=detector,budget=None,repeat=None,reference_resolvable=reference['resolvable'],algorithm_estimatable=False,matched=False,position_error=None,status='complete_window_not_executed' if any(r is None for r in rs) else 'D5_high_order_wall_histogram_not_measured_in_SV'));continue
     arrays=[np.load(ROOT/r['archive']) for r in rs];wv=[wall_estimates(r) for r in rs] if detector=='D5' else None;ws=[wall_estimates(r,100000) for r in rs] if detector=='D5' else None
     for rep in [None,*range(32)]:
      values=[a['exact'] if rep is None else a['samples_100000'][rep] for a in arrays];wall=wv if rep is None else [w[rep] for w in ws] if ws is not None else None;contrasts=[]
      for j,v in enumerate(values):
       pred=d4(v,f['detectors']['8']) if detector=='D4' else d5(wall[j],f['wall_detectors']['8']);dd=pred.get('distances');contrasts.append(dd[2]-dd[order] if dd is not None else np.nan)
      curve=-np.diff(contrasts)/np.diff(h);result=peaks_and_primary(h,curve);primary=result['primary'];error=primary['coordinate']-rp['coordinate'] if primary and rp else None;matched=bool(reference['resolvable'] and result['resolvable'] and abs(error)<=.05)
      rows.append(dict(kappa=k,method=method,p=p,estimator=est,detector=detector,budget=None if rep is None else 100000,repeat=rep,reference_resolvable=reference['resolvable'],algorithm_estimatable=result['resolvable'],matched=matched,position_error=error,result=result,reference=reference,contrast=contrasts,response=curve,status='RN_order_response_matched' if matched else 'reference_unresolved' if not reference['resolvable'] else 'detector_feature_mismatch_or_unresolved',scope='Prototype contrast primary peak compared to predeclared ED m0/AP response. Not detector-on-ED self-truth; competing band may contain additional unresolved physical features.'))
 dump(OUT/'end_to_end/detector_boundary_comparison.json',rows);print('detector boundary',k,flush=True)
groups={}
for r in rows:groups.setdefault((r['method'],r['p'],r['estimator'],r['detector'],r['budget']),[]).append(r)
dump(OUT/'end_to_end/detector_boundary_row_statistics.json',dict(scope='Row/repetition counts only, not physical-slice coverage. Use detector_boundary_coverage.json for the complete requested-slice denominator.',groups={str(k):denominator(v) for k,v in groups.items()}))
import subprocess
subprocess.run([sys.executable,'scripts/summarize_stage6_detector_boundary_denominators.py'],check=True,cwd=ROOT)
