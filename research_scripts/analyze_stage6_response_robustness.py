"""Post-hoc curve/endpoint interpretation; frozen peak scores are never rewritten."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_diagnostics import response_curves
source=OUT/'end_to_end/boundary_curves.json';curves=json.loads(source.read_text());errors=[]
for key,r in curves.items():
    k=float(key.split('_')[0]);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';h=np.array(r['h'])
    pred=response_curves(h,np.array(r['values']),8)[name];truth=response_curves(h,np.array(r['reference']),8)[name]
    e=pred-truth
    errors.append(dict(curve=key,kappa=k,response=name,intervals=len(e),response_RMSE=float(np.sqrt(np.mean(e**2))),response_max_error=float(abs(e).max()),reference_response_max=float(truth.max()),negative_response_intervals=int(np.sum(pred<0)),reference_negative_response_intervals=int(np.sum(truth<0)),scope='No smoothing, normalization or peak retuning. Curve accuracy is separate from primary-peak coordinate agreement.'))
data=json.loads((OUT/'end_to_end/boundary_comparison.json').read_text());groups={}
for r in data:
    groups.setdefault((r['method'],r['p'],r['estimator'],r['budget']),[]).append(r)
endpoints=[]
for key,rr in groups.items():
    executed=[r for r in rr if 'raw_maximum_endpoint' in r]
    endpoints.append(dict(method=key[0],p=key[1],estimator=key[2],budget=key[3],requested_physical_slices=6,
        executed_physical_slices=len({r['kappa'] for r in executed}),executed_curve_repetitions=len(executed),
        frozen_matched_repetitions=sum(r['matched'] for r in executed),
        endpoint_global_maximum_repetitions=sum(r['raw_maximum_endpoint'] for r in executed),
        frozen_matched_but_endpoint_global_maximum=sum(r['matched'] and r['raw_maximum_endpoint'] for r in executed),
        matched_without_endpoint_global_maximum=sum(r['matched'] and not r['raw_maximum_endpoint'] for r in executed),
        by_kappa=[dict(kappa=k,curve_repetitions=len(v),matched=sum(r['matched'] for r in v),matched_endpoint=sum(r['matched'] and r['raw_maximum_endpoint'] for r in v)) for k in sorted({r['kappa'] for r in executed}) for v in [[r for r in executed if r['kappa']==k]]]))
dump(OUT/'end_to_end/response_robustness.json',dict(generated_utc=datetime.now(timezone.utc).isoformat(),curve_source_sha=sha(source),curve_errors=errors,endpoint_audit=endpoints,
    scope='Secondary descriptive audit after viewing results, not a newly validated detector or replacement matching rule. Original frozen rule selects the largest interior peak and retains endpoints separately. An endpoint-dominated matched curve is not claimed as robust physical-boundary recovery. All32 repeats and all6 requested slices remain explicit; no successful-repeat filtering.'))
print('Audited',len(errors),'exact curves and',len(endpoints),'endpoint groups')
