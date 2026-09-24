"""Perfect-ED detector response control; no circuit or free StatePrep claim."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_detector import predict as d4
from annni.stage6_wall_features import predict as d5,pure_features
from annni.stage6_reference import record
from annni.stage6_diagnostics import response_curves,peaks_and_primary
f=json.loads((OUT/'confirmation/method_frozen.json').read_text())
source=OUT/'reference_atlas/window_reference.json';windows=json.loads(source.read_text());rows=[]
for window in windows:
    k=window['kappa'];h=np.asarray(window['h']);order=0 if k<.5 else 1
    name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh'
    target=response_curves(h,np.asarray(window['values']),8)[name];reference=peaks_and_primary(h,target)
    wall=[];states=[]
    for x in h:
        r=record(8,k,float(x));wall.append(pure_features(np.load(ROOT/r['archive'])['state'],8));states.append(dict(archive=r['archive'],sha256=r['sha256']))
    for detector in ['D4','D5']:
        predictions=[];contrast=[]
        for value,w in zip(window['values'],wall):
            pred=d4(np.asarray(value),f['detectors']['8']) if detector=='D4' else d5(w,f['wall_detectors']['8'])
            predictions.append(pred);dist=pred.get('distances');contrast.append(dist[2]-dist[order] if dist is not None else np.nan)
        response=-np.diff(contrast)/np.diff(h);result=peaks_and_primary(h,response)
        primary=result['primary'];ref=reference['primary'];error=primary['coordinate']-ref['coordinate'] if primary and ref else None
        matched=bool(reference['resolvable'] and result['resolvable'] and error is not None and abs(error)<=.05)
        rows.append(dict(kappa=k,detector=detector,h=h,h_mid=(h[:-1]+h[1:])/2,contrast=contrast,response=response,
            ED_named_response=target,reference=reference,result=result,reference_resolvable=reference['resolvable'],
            algorithm_estimatable=result['resolvable'],matched=matched,position_error=error,predictions=predictions,state_sources=states))
summary=[]
for detector in ['D4','D5']:
    rr=[r for r in rows if r['detector']==detector];refs=[r for r in rr if r['reference_resolvable']];passed=[r for r in refs if r['matched']]
    summary.append(dict(detector=detector,requested_physical_slices=len(rr),reference_resolvable_physical_slices=len(refs),
        matched_slices=len(passed),matched_kappa=[r['kappa'] for r in passed],failed_resolvable_kappa=[r['kappa'] for r in refs if not r['matched']],
        worst_matched_error=max(abs(r['position_error']) for r in passed) if passed else None))
dump(OUT/'end_to_end/ideal_ED_detector_boundaries.json',dict(rows=rows,summary=summary,
    source=str(source.relative_to(ROOT)),source_sha256=sha(source),frozen_detector_sha256=sha(OUT/'confirmation/method_frozen.json'),
    scope='Offline ideal-information layer: frozen detector contrast on exact same-N ED features compared against the independently named ED physical-observable response, not detector-on-ED self-truth. The physical interpretation of the RN target still needs separate atlas evidence. Full six requested windows retained, no shots, no physical state-preparation circuit. Largest interior same-window contrast peak, frozen .05 matching tolerance; all raw responses and endpoint/competing peaks retained. No detector retraining or altered thresholds.'))
print(summary)
