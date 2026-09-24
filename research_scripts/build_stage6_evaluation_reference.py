"""Independent multi-size evaluation labels; candidate code has no import of this file."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from annni.stage6_diagnostics import physical_reference
parser=argparse.ArgumentParser();parser.add_argument('--task',default='validation');args=parser.parse_args();task=args.task
if task=='development':points=json.loads((OUT/'failure_mechanisms/benchmark.json').read_text())['points']
elif task=='validation':points=[dict(kappa=k,h=h) for k,h in PLAN['validation']]
elif task=='confirmation':points=PLAN['confirmation']
else:points=json.loads((OUT/'n12_transfer/coordinates.json').read_text())
rows=[]
for point in points:
 k,h=point['kappa'],point['h'];data=[record(n,k,h) for n in [8,12,16]];label,level,why=physical_reference(8,k,h,None,data[0],data[0]['binder']);a,b=data[1:];m0ratio=b['structure_factor'][0]/a['structure_factor'][0];apratio=b['structure_factor'][4]/a['structure_factor'][3];gapratio=b['sector_gap']/a['sector_gap'];apbind=[]
 for r in data[1:]:
  s=np.load(ROOT/r['archive'])['state'];_,z,_=geometry(r['n']);m=z@np.exp(1j*np.pi/2*np.arange(r['n']))/r['n'];m2=r['structure_factor'][r['n']//4];apbind.append(float(1-(abs(s)**2@abs(m)**4)/(2*m2**2)))
 if label is None and not any(r['reference_numerical_ambiguous'] for r in data):
  if k<.5 and b['structure_factor'][0]>.45 and b['binder']>.55 and m0ratio>.94:label='ferro-like';level='Rlarge_ED_interior';why='N12/16 ferro order amplitude stable (<6% fall), high Binder; small positive field continuation, finite-size evidence only'
  elif k>.5 and b['structure_factor'][4]>.30 and min(apbind)>.42 and apratio>.94:label='antiphase-like';level='Rlarge_ED_interior';why='N12/16 period4 amplitude stable (<6% fall) and complex-order Binder high; finite-size ordered interior evidence'
  elif b['mx']>.55 and max(m0ratio,apratio)<.90 and gapratio>.90:label='paramagnetic-like';level='Rlarge_ED_interior';why='Both order factors decrease with N12->16, polarization and stable sector gap; finite-size gapped-side evidence, no guarantee against very large xi'
 rows.append(dict(**point,label=label,level=level,evidence=why,bc='PBC',n=[8,12,16],m0_ratio_16_12=m0ratio,ap_ratio_16_12=apratio,gap_ratio_16_12=gapratio,ap_binder=apbind,sources=[r['archive'] for r in data],criteria_sha=sha(__file__),data_disposition='reference_generation_for_evaluation_only_not_candidate_input'));dump(OUT/f'reference_atlas/{task}_evaluation.json',rows)
 print(task,len(rows),label,flush=True)
