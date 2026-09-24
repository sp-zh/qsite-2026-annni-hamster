"""Energy-selected saved checkpoints at64/96/128; no ED-based selection.
This is a truncated-growth diagnostic, not independent optimization at each cap.
"""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_rows
from annni.stage6_candidates import evaluate
from annni.stage6_assess import assess
assert (OUT/'confirmation/confirmation_unsealed.json').exists()
old=json.loads((OUT/'legacy_b3/confirmation_index.json').read_text());rows=[]
old_tolerance=json.loads((ROOT/'results/stage4_upgrade_v1/experiment_plan.json').read_text())['selection_energy_tolerance_per_site']
for point in candidate_rows('confirmation'):
 n,k,h=point['n'],point['kappa'],point['h'];methods={m:[json.loads((ROOT/p).read_text()) for p in v['runs']] for m,v in point['methods'].items()}
 b=next(x for x in old if (x['kappa'],x['h'])==(k,h));methods['B3']=b['runs']
 for method,runs in methods.items():
  tolerance=old_tolerance if method=='B3' else 1e-6
  for cap in [64,96,128]:
   choices=[]
   for run in runs:
    checkpoints=[c for c in run['checkpoints'] if c['cnots']<=cap]
    if not checkpoints:continue
    emin=min(c['energy'] for c in checkpoints);chosen=min([c for c in checkpoints if c['energy']<=emin+n*tolerance],key=lambda c:(c['cnots'],c['energy']));choices.append((run,chosen))
   emin=min(c['energy'] for r,c in choices);r,c=min([(r,c) for r,c in choices if c['energy']<=emin+n*tolerance],key=lambda rc:(rc[1]['cnots'],rc[1]['energy']))
   state=evaluate(c['params'],c['words'],n,r.get('basis','physical'),r['ref'],k,h)[2]
   if cap==128:
    original=b['selected'] if method=='B3' else point['methods'][method]['selected'];np.testing.assert_allclose(state,np.load(ROOT/original['archive'])['state'],atol=1e-10)
   metric=assess(state,n,k,h);rows.append(dict(kappa=k,h=h,region=point['region'],method=method,checkpoint_cap=cap,actual_cnots=c['cnots'],parameter_count=len(c['params']),joint_pass=metric['joint_pass'],observable_pass=metric['observable_pass'],state_pass=metric['state_pass'],fidelity=metric['fidelity'],delta_e=metric['delta_e'],source=r['archive'],checkpoint_reason=c['reason'],selected_params=c['params'],selected_words=c['words']))
summary=[]
for method,cap,region in __import__('itertools').product(sorted(methods),[64,96,128],['all','low_field','antiphase_band','interior']):
 selected=[r for r in rows if r['method']==method and r['checkpoint_cap']==cap and (region=='all' or r['region']==region)]
 summary.append(dict(method=method,cap=cap,region=region,coordinates=len(selected),joint_pass=sum(r['joint_pass'] for r in selected),observable_pass=sum(r['observable_pass'] for r in selected),median_actual_cnots=float(np.median([r['actual_cnots'] for r in selected]))))
dump(OUT/'confirmation/checkpoint_budget_diagnostic.json',dict(rows=rows,summary=summary,scope='Same frozen energy/resource rules applied to saved growth checkpoints. Main128-cap choices exactly reload the original deployed states. Lower-cap checkpoints are not independently reoptimized fixed-budget experiments and retain the search cost of generating the full trajectory. Equal maximum cap is not equal actual gate count. No confirmation oracle is used for selection.'))
print('Checkpoint diagnostic rows',len(rows))
