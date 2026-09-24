"""Completed clean-circuit RN windows, separate from still-running noisy batches."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_boundaries import compare,denominator
from annni.stage6_diagnostics import response_curves,peaks_and_primary
from annni.upgrade_gates import vector,observations
path=OUT/'reference_atlas/window_reference.json';refs=json.loads(path.read_text());rows=[]
for ref in refs:
 k=ref['kappa'];h=np.array(ref['h']);name='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';target=np.array(ref['values']);reference=peaks_and_primary(h,response_curves(h,target,8)[name])
 for method in ['B3','H6']:
  arms=[load(k,float(x),method,task='windows') for x in h];values=np.array([vector(observations(a['state'],8)) for a in arms]);result=compare(h,values,8,name,reference);rows.append(dict(kappa=k,method=method,feature=name,source_archives=[a['source_archive'] for a in arms],h=h,values=values,ED_values=target,**result));print(k,method,result['status'],result['position_error'])
dump(OUT/'end_to_end/pure_window_reconstruction.json',dict(rows=rows,summary={m:denominator([r for r in rows if r['method']==m]) for m in ['B3','H6']},reference_sha=sha(path),scope='All six fixed17point N8 PBC clean windows. Same named RN features only; no change in peak rules or phase labels; not evidence for thermodynamic critical locations.'))
