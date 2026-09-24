"""Bounded same-coordinate controls using the actual two switched branches."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
from annni.upgrade_gates import compile_circuit
refs=read(OUT/'window_reference.json');switches=[r for r in read(OUT/'branch_switches_historical.json') if r['method']=='B3'];planpath=OUT/'window_completion/branch_control_plan.json'
if not planpath.exists():
 chosen=[]
 for w in refs:
  k=w['kappa'];rows=[r for r in switches if r['kappa']==k];primary=w['frozen_reference']['primary'];loc=primary['coordinate'] if primary else float(np.mean(w['h']))
  nearest=min(rows,key=lambda r:abs((r['left_h']+r['right_h'])/2-loc))
  biggest=max(rows,key=lambda r:abs(point(k,r['left_h'])['resources']['cnots']-point(k,r['right_h'])['resources']['cnots']))
  for r in [nearest,biggest]:
   if r not in chosen:chosen.append(r)
 dump(planpath,dict(frozen_utc=datetime.now(timezone.utc).isoformat(),rule='Per window nearest actual switch to frozen ED primary (window center if no primary) plus largest actual selected CNOT jump; same-coordinate actual before/after branches, no surrogate. Selection uses historical inputs only.',switches=chosen))
results=[]
for idx,switch in enumerate(read(planpath)['switches']):
 pairs=switch['same_coordinate_comparisons'];pair=min(pairs,key=lambda x:abs(x['h']-(switch['left_h']+switch['right_h'])/2));branches=pair['branches'];values=[]
 for b in branches:
  guard();source=ROOT/b['source'];raw=read(source.with_suffix('.json'));assert sha(ROOT/raw['archive'])==raw['sha256'];c=raw['selected'];g=compile_circuit(8,raw['ref'],c['words'],c['params']);state=np.load(source)['state'];np.testing.assert_allclose(evolve(g,8),state,atol=1e-10);base=OUT/'branch_inputs'/uid(dict(source=str(source.relative_to(ROOT)),sha=sha(source)));base.parent.mkdir(exist_ok=True);a=base.with_suffix('.npz');np.savez_compressed(a,state=state,clean=vector(observations(state,8)));row=dict(n=8,kappa=pair['kappa'],h=pair['h'],gates=g,resources=resources(g,8),archive=str(a.relative_to(ROOT)));records=[]
  for p in cfg()['p']:
   d,r=physical(row,p);records.append(dict(p=p,probability=r,observables=np.load(ROOT/r['archive'])['observables'].tolist()))
  values.append(dict(branch=b['branch'],source=str(source.relative_to(ROOT)),sha256=sha(source),source_metadata_sha=sha(source.with_suffix('.json')),gates=g,parameters=c['params'],cnots=row['resources']['cnots'],records=records))
 differences=[]
 for p in cfg()['p']:
  aa=[np.array(next(x['observables'] for x in v['records'] if x['p']==p)) for v in values];differences.append(dict(p=p,max_C_difference=float(max(abs(aa[0][:8]-aa[1][:8]))),max_SF_difference=float(max(abs(aa[0][8:16]-aa[1][8:16]))),Mx_difference=float(abs(aa[0][-1]-aa[1][-1]))))
 results.append(dict(kappa=switch['kappa'],left_h=switch['left_h'],right_h=switch['right_h'],same_coordinate_h=pair['h'],branches=values,differences=differences,scope='Exact controlled branch difference, not a boundary uncertainty interval; other switches remain unverified under noise.'))
 dump(OUT/'window_completion/branch_controls.json',results);print('branch control',idx+1,len(read(planpath)['switches']),flush=True)
