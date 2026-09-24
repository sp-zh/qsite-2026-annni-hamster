"""Deduplicate actual execution records; never sum H6's shared C0 cache twice."""
import sys,csv,collections,platform
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
folders={
 'new_candidate_optimization':'domain_wall_candidates/cache',
 'B3_optimization':'legacy_b3/adaptive/cache',
 'fixed_energy_restart':'failure_mechanisms/fixed_energy_restarts',
 'oracle_fidelity_fit_not_deployable':'failure_mechanisms/oracle_expressivity',
 'energy_continuation':'failure_mechanisms/energy_continuation',
 'ED_reference':'reference_atlas/cache',
 'density_and_measurement_probabilities':'end_to_end/probabilities',
 'finite_measurement':'end_to_end/measurements',
 'ideal_ED_measurement':'noise_diagnosability/ed_measurements',
 'MPS':'floating_boundary_scan/cache',
 'fresh_HVA_control':'end_to_end/hva',
 'oracle_binary_query':'noise_diagnosability/pair_cache',
}
rows=[];seen=set()
for category,folder in folders.items():
 for path in sorted((OUT/folder).glob('*.json')):
  r=json.loads(path.read_text())
  if category=='fresh_HVA_control' and 'trials' in r:
   r=dict(r,seconds=sum(t['seconds'] for t in r['trials']),nfev=sum(t['nfev'] for t in r['trials']),nit=sum(t['nit'] for t in r['trials']))
  if category=='oracle_binary_query':
   r=dict(r,archive=r['counts_archive'],cost={str(x['shots_per_query']):dict(all_reps_shots=2*x['repeats_per_hypothesis']*x['shots_per_query'],gate_shots_per_rep=x['shots_per_query']*sum(p['cnots'] for p in r['probability_records'])) for x in r['oracle_measurement']})
  if not isinstance(r,dict) or 'archive' not in r:continue
  archive=r['archive'];key=(category,archive)
  if key in seen:continue
  seen.add(key);shared=r.get('shared_quantum_data_with');cost=r.get('cost',{})
  shots=sum(c.get('all_reps_shots',c.get('shots_per_repeat',0)*c.get('repeats',0)) for c in cost.values()) if not shared else 0
  gate_shots=sum(c.get('gate_shots_per_rep',0)*32 for c in cost.values()) if not shared else 0
  rows.append(dict(category=category,record=str(path.relative_to(ROOT)),archive=archive,n=r.get('n',r.get('key',{}).get('n')),kappa=r.get('kappa',r.get('key',{}).get('kappa')),h=r.get('h',r.get('key',{}).get('h')),p=r.get('p'),seconds=r.get('seconds'),nfev=r.get('nfev',0),nit=r.get('nit',0),pool_gradient_evaluations=r.get('pool_gradient_evaluations',0),simulated_shots=shots,gate_weighted_simulated_shots=gate_shots,shared_counts_source=shared,disposition=r.get('disposition','newly_executed_record'),record_sha256=sha(path)))
summary={}
for category in folders:
 a=[r for r in rows if r['category']==category]
 coordinates={(r['n'],r['kappa'],r['h']) for r in a if all(r[k] is not None for k in ['n','kappa','h'])}
 summary[category]=dict(unique_records=len(a),coordinates=len(coordinates),coordinate_count_scope='Distinct complete literal(n,kappa,h) tuples; not repeated shots. Pair-only records have no single-coordinate count.',coordinate_groups_14_decimals_reporting_only=len({(n,round(k,14),round(h,14)) for n,k,h in coordinates}),records_without_single_coordinate=sum(any(r[k] is None for k in ['n','kappa','h']) for r in a),records_without_timing=sum(r['seconds'] is None for r in a),summed_record_seconds=sum(r['seconds'] or 0 for r in a),nfev=sum(r['nfev'] or 0 for r in a),iterations=sum(r['nit'] or 0 for r in a),pool_gradients=sum(r['pool_gradient_evaluations'] or 0 for r in a),simulated_shots=sum(r['simulated_shots'] for r in a),gate_weighted_simulated_shots=sum(r['gate_weighted_simulated_shots'] for r in a))
incomplete={str(p.relative_to(ROOT)):json.loads(p.read_text()) for p in OUT.rglob('*failures.json')}
result=dict(timestamp=datetime.now(timezone.utc).isoformat(),run_id=PLAN['run_id'],started=PLAN['started_utc'],deadline=PLAN['deadline'],elapsed_wall_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(PLAN['started_utc'])).total_seconds(),summary=summary,incomplete_execution_records=incomplete,scope='Unique archived execution records. Sum of individual measured seconds is not elapsed wall time and does not include all orchestration/plotting/test overhead or incomplete runs without a final archive. Those failure records are retained separately here; unavailable timings are not zero. Reused H6 components are counted once. Derived quadratic ZNE estimates add zero quantum samples. All shots are classical simulator draws, not hardware execution.',resources=PLAN['resources'])
dump(OUT/'verification/resource_summary.json',result)
with (OUT/'verification/unique_execution_records.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps(result,indent=2))
