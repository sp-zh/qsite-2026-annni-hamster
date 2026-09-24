"""N12 PBC local curves with their own same-coordinate ED reference."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_reference import record
from annni.stage6_diagnostics import response_curves,peaks_and_primary
from annni.stage6_boundaries import compare,denominator
from annni.stage6_io import measurement_rows
from annni.upgrade_gates import observations,vector
O=OUT/'n12_transfer';coords=json.loads((O/'window_coordinates.json').read_text());h=np.array([x['h'] for x in coords]);k=coords[0]['kappa'];n=12;name='minus_dmap_dh';f=json.loads((OUT/'confirmation/method_frozen.json').read_text());methods=['B3','C0','C1',f['physical_method']];refs=[record(n,k,float(x)) for x in h];target=np.array([np.r_[r['correlations'],r['structure_factor'],r['mx']] for r in refs]);ref=peaks_and_primary(h,response_curves(h,target,n)[name]);curves={};rows=[]
for method in methods:
 values=np.array([vector(observations(load(k,float(x),method,n,task='n12_window')['state'],n)) for x in h]);curves[method]=values;rows.append(dict(method=method,p=0,estimator='pure_circuit',coordinates=len(h),budget=None,repeat=None,**compare(h,values,n,name,ref)))
np.savez_compressed(O/'window_curves.npz',h=h,ED=target,**curves)
# Only six of these coordinates were preselected for N12 exact-density noise.
# Use the identical sparse coordinates for each method/p and its own ED diagnostic.
points=[p for p in measurement_rows((OUT/'end_to_end').glob('n12_*_index.json')) if p['kappa']==k and any(abs(p['h']-x)<1e-12 for x in h)]
points.sort(key=lambda r:r['h']);noisycurves={}
if points:
 nh=np.array([x['h'] for x in points]);nt=np.array([target[np.argmin(abs(h-x))] for x in nh]);nr=peaks_and_primary(nh,response_curves(nh,nt,n)[name])
 for method in ['B3',f['physical_method']]:
  for p in [0,.01,.05]:
   entries=[next(e['record'] for e in r['entries'] if e['method']==method and e['estimator']=='raw' and e['record']['p']==p) for r in points];arrays=[np.load(ROOT/e['archive']) for e in entries];v=np.array([a['exact'] for a in arrays]);noisycurves[f'{method}_p{p}']=v;rows.append(dict(method=method,p=p,estimator='raw_sparse_window',coordinates=len(nh),budget=None,repeat=None,**compare(nh,v,n,name,nr)))
   for b in PLAN['measurement']['budgets']:
    for rep in range(32):rows.append(dict(method=method,p=p,estimator='raw_sparse_window',coordinates=len(nh),budget=b,repeat=rep,**compare(nh,np.array([a[f'samples_{b}'][rep] for a in arrays]),n,name,nr)))
 np.savez_compressed(O/'window_noise_curves.npz',h=nh,ED=nt,**noisycurves)
summary={}
for key in sorted({(r['method'],r['p'],r['estimator'],str(r['budget'])) for r in rows}):summary[str(key)]=denominator([r for r in rows if (r['method'],r['p'],r['estimator'],str(r['budget']))==key])
dump(O/'window_boundary_comparison.json',dict(rows=rows,summary=summary,full_reference=ref,full_h=h,noise_h=nh if points else [],scope='N12 PBC finite-size AP-response feature, not N8 labels or thermodynamic boundary. Full p0 curve and preselected sparse noisy curve have separate ED references and denominators. Missing full-resolution noisy coordinates are explicitly unexecuted.'))
print('N12 full window',len(h),'noise window',len(points))
