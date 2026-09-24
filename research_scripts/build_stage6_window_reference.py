import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from annni.stage6_diagnostics import *
coords=json.loads((OUT/'reference_atlas/circuit_window_coordinates.json').read_text());rows=[]
for k in sorted({x['kappa'] for x in coords}):
 points=[p for p in coords if p['kappa']==k];hs=np.array([x['h'] for x in points]);references=[record(8,k,h) for h in hs];states=[np.load(ROOT/r['archive'])['state'] for r in references];v=np.array([np.r_[r['correlations'],r['structure_factor'],r['mx']] for r in references]);steps=[]
 for stride in [1,2,4]:
  hh=hs[::stride];vv=v[::stride];ss=states[::stride];cur=response_curves(hh,vv,8,ss);steps.append(dict(stride=stride,step=float(np.median(np.diff(hh))),features={name:peaks_and_primary(hh,cur[name]) for name in ['minus_dm0_dh','minus_dmap_dh','dmx_dh','chi_f','unique_feature_speed']}))
 rows.append(dict(n=8,kappa=k,h=hs,values=v,primary_feature=points[0]['feature'],sources=[r['archive'] for r in references],step_checks=steps,reference_level='RN',physical_boundary_claim=False));dump(OUT/'reference_atlas/window_reference.json',rows)
print('Common fine-grid RN references completed',len(rows))
