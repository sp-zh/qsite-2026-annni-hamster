"""Actual selected reference branches evaluated on both sides at identical coordinates."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_assess import assess_run
new=json.loads((OUT/'confirmation/method_frozen.json').read_text())['physical_method'];sources={}
for p in (OUT/'domain_wall_candidates').glob('windows_*_index.json'):
 for r in json.loads(p.read_text()):sources.setdefault(new,[]).append(dict(kappa=r['kappa'],h=r['h'],selected=r['methods'][new]['selected'],runs=[json.loads((ROOT/x).read_text()) for x in r['methods'][new]['runs']]))
sources['B3']=json.loads((OUT/'legacy_b3/windows_index.json').read_text());rows=[]
def identity(r):return (r.get('basis','physical'),r['ref'],r['seed'])
for method,points in sources.items():
 for k in sorted(set(r['kappa'] for r in points)):
  ps=sorted([r for r in points if r['kappa']==k],key=lambda r:r['h'])
  for a,b in zip(ps[:-1],ps[1:]):
   aa,bb=identity(a['selected']),identity(b['selected'])
   if aa==bb:continue
   compared=[]
   for point in [a,b]:
    at_coordinate=[]
    for branch in [aa,bb]:
     actual=next((r for r in point['runs'] if identity(r)==branch),None)
     at_coordinate.append(dict(branch=branch,source=actual['archive'] if actual else None,metrics=assess_run(actual) if actual else None,status='actual_saved_same_coordinate_branch' if actual else 'unavailable_no_surrogate'))
    compared.append(dict(kappa=k,h=point['h'],branches=at_coordinate))
   rows.append(dict(method=method,kappa=k,left_h=a['h'],right_h=b['h'],actual_selected_before=aa,actual_selected_after=bb,same_coordinate_comparisons=compared,scope='Independent per-coordinate growth per fixed seed/reference. This is an actual selected-reference switch, not a claimed directional continuation-chain switch. No opposite-direction surrogate.'))
dump(OUT/'failure_mechanisms/actual_branch_switches.json',rows);print('Actual switches with paired saved branches:',len(rows))
