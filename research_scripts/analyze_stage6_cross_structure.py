"""Same Hamiltonian coordinate, different literal preparation: circuit-noise control.
Uses already saved pair density matrices; no new quantum shot budget is hidden.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_distinguish import distances
from annni.stage6_reference import record
f=json.loads((OUT/'confirmation/method_frozen.json').read_text());new=f['physical_method'];data=json.loads((OUT/'noise_diagnosability/identifiability.json').read_text());sources={}
for r in data:
 for point,source,prediction in zip([r['pair']['a'],r['pair']['b']],r['probability_records'],r['predictions']):sources[(point['kappa'],point['h'],r['method'],r['p'])]=(source,prediction)
coordinates=sorted({key[:2] for key in sources});rows=[]
for k,h in coordinates:
 if not all((k,h,m,p) in sources for m in ['B3',new] for p in [0,.01,.05]):continue
 ed=record(8,k,h);psi=np.load(ROOT/ed['archive'])['state'];clean=[]
 for m in ['B3',new]:
  source,_=sources[(k,h,m,0)];rho=np.load(ROOT/source['archive'])['rho'];clean.append(float(np.vdot(psi,rho@psi).real))
 for p in [0,.01,.05]:
  refs=[sources[(k,h,m,p)] for m in ['B3',new]];rho=[np.load(ROOT/r[0]['archive'])['rho'] for r in refs];metrics,_,_=distances(*rho);rows.append(dict(kappa=k,h=h,p=p,methods=['B3',new],**metrics,clean_fidelity_to_same_ED=clean,both_clean_state_pass=all(x>=.99 for x in clean),predictions={m:r[1] for m,r in zip(['B3',new],refs)},source_archives=[r[0]['archive'] for r in refs],cnots=[r[0]['cnots'] for r in refs],scope='Same physical target and coordinate, distinct preparation channels; cross-structure output disagreement cannot establish a physical phase change. Clean-ED training uses neither p nor circuit identity.'))
for r in rows:
 base=next(x for x in rows if (x['kappa'],x['h'],x['p'])==(r['kappa'],r['h'],0));r['DQ_minus_p0']=r['trace_distance']-base['trace_distance'];r['TV_minus_p0']=r['xz_joint_total_variation']-base['xz_joint_total_variation']
dump(OUT/'noise_diagnosability/same_coordinate_cross_structure.json',dict(rows=rows,coordinates=len(coordinates),resource='Analysis of previously saved full density matrices and detector outputs; no added measurement samples. State access is not a local-shot resource.',interpretation='Noise may distinguish circuit implementations rather than physical phases. A retained oracle binary signal is not automatically retained universal phase information; same-coordinate controls expose this confound. No common-channel contraction assumption.'))
print('cross-structure coordinates',len(coordinates))
