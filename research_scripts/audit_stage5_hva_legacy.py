"""Recover each actually optimized legacy coordinate from stored RNG initials and energies."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,PLAN,dump,np
from annni.circuits import HVAEngine
from annni.stage5_e2e import hva_gates
coords=PLAN['end_to_end']+json.loads((OUT/'end_to_end_amendment_v1.json').read_text())['additional_coordinates']+json.loads((OUT/'end_to_end/grid_refinement_frozen.json').read_text())['coordinates'];coords=sorted(set(map(tuple,coords)));engine=HVAEngine(8);rows=[]
for p in (OUT/'end_to_end/hva').glob('*.json'):
 r=json.loads(p.read_text());a=np.load(p.with_suffix('.npz'));matches=[]
 for k,h in coords:
  initials=np.array([np.random.default_rng(np.random.SeedSequence([seed,round(k*1e6),round(h*1e6)])).uniform(-.2,.2,(6,3)) for seed in r['seeds']])
  if np.array_equal(initials,a['initials']):matches.append((k,h))
 assert len(matches)==1,(p,matches)
 k,h=matches[0];errors=[abs(engine.value_grad(t.ravel(),k,h)[0]-fit['energy']) for t,fit in zip(a['finals'],r['trials'])];assert max(errors)<1e-8
 rows.append(dict(metadata=str(p.relative_to(ROOT)),archive=str(p.with_suffix('.npz').relative_to(ROOT)),kappa=k,h=h,initials_exactly_matched=True,energy_errors=errors,gates=json.loads(json.dumps(hva_gates(a['theta'],8)))))
affected=[]
for name in ['core','refined']:
 for point in json.loads((OUT/'verification/hva_before_fix'/f'{name}_index.json').read_text()):
  b0=next(e['record'] for e in point['entries'] if e['arm']=='B0_raw' and e['record']['p']==0)
  for legacy in rows:
   if b0['key']['gates']==legacy['gates'] and (abs(point['kappa']-legacy['kappa'])>1e-12 or abs(point['h']-legacy['h'])>1e-12):affected.append(dict(view=name,kappa=point['kappa'],h=point['h'],actually_optimized_at=[legacy['kappa'],legacy['h']],legacy_source=legacy['metadata']))
dump(OUT/'verification/hva_legacy_coordinate_audit.json',dict(legacy_runs=rows,affected_point_records=affected,affected_coordinates=len(set((r['kappa'],r['h']) for r in affected)),scope='Coordinates established by exact stored three-seed initial vectors and final energy recomputation, not inferred from corrupted names. Old physical execution records remain preserved; corrected comparisons use hva_v2.'))
print('Legacy actual optimizations',len(rows),'aliased comparison coordinates',len(set((r['kappa'],r['h']) for r in affected)))
