import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from annni.stage6_diagnostics import response_curves,peaks_and_primary
O=OUT/'n12_transfer';p=O/'window_coordinates.json'
if p.exists():raise SystemExit('Existing frozen N12 window retained')
rows=json.loads((OUT/'reference_atlas/slices_n12.json').read_text())['0.55'];hs=np.array([r['h'] for r in rows]);vs=np.array([np.r_[r['correlations'],r['structure_factor'],r['mx']] for r in rows]);peaks=peaks_and_primary(hs,response_curves(hs,vs,12)['minus_dmap_dh']);assert peaks['primary'];center=round(peaks['primary']['coordinate']/.0125)*.0125
hs=np.unique(np.round(np.maximum(.01,np.arange(center-.1,center+.1001,.0125)),6));points=[dict(kappa=.55,h=float(h),source_task='n12_window',region='N12_antiphase_response_window') for h in hs];dump(p,points);refs=[record(12,.55,float(h)) for h in hs];dump(O/'window_reference.json',dict(points=points,records=refs,selection='N12 same-size ED named minus_dmAP response; no transfer of N8 boundary',coarse_peak=peaks,coordinate_sha=uid(points),smoothing=None,interpolation=None,step=.0125))
print('Frozen N12 window',len(points),hs[0],hs[-1])
