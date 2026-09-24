"""At most one predeclared, measurement-limited boundary window gets1M shots."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_estimators import measurement
from annni.stage6_diagnostics import response_curves,peaks_and_primary
from annni.stage6_boundaries import compare,denominator
base=json.loads((OUT/'end_to_end/boundary_comparison.json').read_text());refs=json.loads((OUT/'reference_atlas/window_reference.json').read_text());mf=json.loads((OUT/'end_to_end/mitigation_frozen.json').read_text());f=json.loads((OUT/'confirmation/method_frozen.json').read_text());options=[]
for k in [.45,.55,.8]:
 ref=next(r for r in refs if r['kappa']==k);h=np.array(ref['h']);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';edcurve=response_curves(h,np.array(ref['values']),8)[name]
 for method in ['B3',f['physical_method']]:
  est=mf['selected'][method]
  for p in [.01,.05]:
   exact=next(r for r in base if r['kappa']==k and r['method']==method and r['estimator']==est and r['p']==p and r['budget'] is None);samples=[r for r in base if r['kappa']==k and r['method']==method and r['estimator']==est and r['p']==p and r['budget']==100000]
   if not samples or 'curve' not in exact:continue
   bias=float(np.mean((np.array(exact['curve'])-edcurve)**2));variance=float(np.mean((np.array([r['curve'] for r in samples])-exact['curve'])**2));success=sum(r['matched'] for r in samples)/len(samples);eligible=exact['matched'] and success<.5 and variance>bias;options.append(dict(kappa=k,method=method,p=p,exact_matched=exact['matched'],match_fraction_100k=success,derivative_bias_mse=bias,derivative_sampling_mse=variance,eligible=eligible,ratio=variance/max(bias,1e-12)))
choices=[x for x in options if x['eligible']];decision=dict(options=options,selected=max(choices,key=lambda x:x['ratio']) if choices else None,rule='Exactly matched finite-size order-response but<50% measured-window matches at100k and derivative sampling MSE exceeds derivative bias MSE. Highest ratio; at most1kappa, both preparations, all3p,32independent repeats,1M totalshots each coordinate/estimator.',timestamp=datetime.now(timezone.utc).isoformat());dump(OUT/'end_to_end/variance_extension_decision.json',decision)
if not choices:
 print('No window meets predeclared variance-dominant trigger; no1M extension')
 raise SystemExit(0)
k=decision['selected']['kappa'];ref=next(r for r in refs if r['kappa']==k);h=np.array(ref['h']);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';reference=peaks_and_primary(h,response_curves(h,np.array(ref['values']),8)[name]);rows=[];peaks=[]
for method in ['B3',f['physical_method']]:
 est=mf['selected'][method];sets={}
 for p in [0,.01,.05]:
  rs=[measurement(load(k,float(x),method,task='windows'),p,est,budgets=[1000000]) for x in h];sets[p]=rs;rows.append(dict(kappa=k,h=h,method=method,p=p,estimator=est,records=rs));dump(OUT/'end_to_end/windows_1M_records.json',rows)
 for p in [0,.01,.05]:
  arrays=[np.load(ROOT/r['archive']) for r in sets[p]];p0arrays=[np.load(ROOT/r['archive']) for r in sets[0]]
  for rep in range(32):
   r=compare(h,np.array([a['samples_1000000'][rep] for a in arrays]),8,name,reference);p0=compare(h,np.array([a['samples_1000000'][rep] for a in p0arrays]),8,name,reference);rp=r['raw_maximum_coordinate'];r0=p0['raw_maximum_coordinate'];peaks.append(dict(method=method,kappa=k,p=p,estimator=est,budget=1000000,repeat=rep,**r,finite_p0_reference=p0,shift_from_finite_p0=rp-r0 if rp is not None and r0 is not None else None))
 dump(OUT/'end_to_end/windows_1M_peaks.json',peaks)
dump(OUT/'end_to_end/windows_1M_cost.json',dict(total_shots=len(h)*2*3*32*1000000,coordinates=len(h),preparations=2,p_values=3,repeats=32,shots_per_coordinate_p_preparation_repeat=1000000,total_gate_shots=sum(32*r['cost']['1000000']['gate_shots_per_rep'] for row in rows for r in row['records']),note='Same chosen estimator per preparation as validation; all p and full window charged. No successful-repeat filtering.'))
