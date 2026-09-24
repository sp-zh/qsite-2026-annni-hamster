"""Evidence inventory from raw indices, including missing work; safe during a run."""
import sys,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_rows,measurement_rows
items=[]
def item(name,paths,count=None,scope='',expected=None):
 existing=[p for p in paths if p.exists()]
 items.append(dict(name=name,disposition='newly_executed' if existing else 'implemented_not_run',count=count,expected=expected,scope=scope,sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in existing]))
for task,expected in [('development',36),('validation',24),('confirmation',96),('stability',24),('windows',102),('low_map',108),('map',420),('n12',36),('n12_window',16),('n12_192',12)]:
 rows=candidate_rows(task);paths=[p for p in (OUT/'domain_wall_candidates').glob(task+'_*_index.json') if __import__('re').fullmatch(__import__('re').escape(task)+r'_\d+_\d+_index.json',p.name)]
 scope='Coordinate-seed rows, not number of optimizer initializations. Shared component cache is not counted as new execution.'
 if task=='stability':scope+=' These24new rows are seeds743/857 on12coordinates. The full36-row three-seed stability assessment also reuses12seed631confirmation rows, already counted under confirmation.'
 item('candidate_'+task,paths,len(rows),scope,expected)
for task,expected in [('validation',24),('core',48),('windows',51),('confirmation',96),('low_map',108),('map',420),('n12',12)]:
 paths=list((OUT/'end_to_end').glob(task+'_*_index.json'));rows=measurement_rows(paths)
 item('noise_'+task,paths,len(rows),'Actual point-level raw measurement indices; estimator details and all incomplete points remain in source records.',expected)
for task in ['coarse','bounded','followup','controls','final_continuation','h425_size']:
 path=OUT/f'floating_boundary_scan/{task}_index.json';rows=json.loads(path.read_text()) if path.exists() else []
 item('MPS_'+task,[path],len(rows),'Actual solver runs including nonconverged continuations; not independent physical coordinates.')
for name,path in [
 ('independent_reference','reference_atlas/reference_features.csv'),
 ('analytic_Ising_control','reference_atlas/analytic_Ising_reference.json'),
 ('signed_noise_error_decomposition','end_to_end/core_error_decomposition.json'),
 ('same_coordinate_gate_jump_controls','failure_mechanisms/gate_jump_controls.json'),
 ('response_endpoint_sensitivity','end_to_end/response_robustness.json'),
 ('paired_search_basis_ablations','failure_mechanisms/paired_ablations.json'),
 ('reference_scope_v4','reference_atlas/reference_regions_v4.csv'),
 ('reference_scope_v5','reference_atlas/reference_regions_v5.csv'),
 ('reference_scope_v6','reference_atlas/reference_regions_v6.csv'),
 ('failure_attribution','failure_mechanisms/attribution_v2.json'),
 ('offline_translation_sector_diagnostic','failure_mechanisms/translation_sector_diagnostic.json'),
 ('literal_reference_translation_controls','failure_mechanisms/reference_translation_controls.json'),
 ('N12_actual_density_cost','n12_transfer/density_actual_cost.json'),
 ('N12_noise_scope','n12_transfer/noise_scope_interpretation.json'),
 ('N12_same_coordinate_budget_comparison','n12_transfer/paired_budget_128_192.json'),
 ('binary_identifiability','noise_diagnosability/identifiability.json'),
 ('cross_structure_information','noise_diagnosability/same_coordinate_cross_structure.json'),
 ('RN_boundary_reconstruction','end_to_end/boundary_coverage.json'),
 ('ideal_ED_detector_response_control','end_to_end/ideal_ED_detector_boundaries.json'),
 ('detector_boundary_physical_denominators','end_to_end/detector_boundary_coverage.json'),
 ('floating_evidence_v2','floating_boundary_scan/interval_evidence_v2.json'),
 ('floating_evidence_v3','floating_boundary_scan/interval_evidence_v3.json'),
 ('floating_evidence_v4','floating_boundary_scan/interval_evidence_v4.json'),
 ('floating_criterion_explanation_v3','floating_boundary_scan/evidence_bottlenecks_v3.json'),
 ('floating_criterion_explanation_v4','floating_boundary_scan/evidence_bottlenecks_v4.json'),
 ('full_tests','verification/tests_full_final.log' if (OUT/'verification/tests_full_final.log').exists() else 'verification/tests_full_current.log'),
 ('protected_inputs','verification/protected_inputs_verified.json'),
 ('scientific_payload_hashes','verification/artifact_hash_verification.json'),
 ('numerical_completion','verification/numerical_completion.json'),
 ('final_pdf_review','verification/pdf_review_final.json'),
 ('executed_notebook','report/stage6_research.ipynb')]:
 item(name,[OUT/path],scope='Derived analysis/verification may be a partial snapshot while numerical queues are active; inspect source counts and timestamps.')
dump(OUT/'report/EVIDENCE_LEDGER.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),run_id=PLAN['run_id'],deadline=PLAN['deadline'],items=items,historical_reused=dict(base='deliverables/annni_stage5_v1.zip',scope='Original B0/B3/B5 data, baseline ED and upstream; reuse is explicitly tagged in point indices and never counted as a new state optimization.'),interpretation='Existence is not scientific completion. Expected counts, physical denominators and failed runs must be read together. This inventory is generated from actual source indices, not report claims.'))
lines=['# Stage 6 evidence ledger','',f'Generated {datetime.now(timezone.utc).isoformat()}. Existence does not imply scientific completion.','', '| Work | Executed index rows | Requested | Evidence |','|---|---:|---:|---|']
for r in items:
 paths='; '.join(f"[{Path(p['path']).name}](../../../{p['path']})" for p in r['sources']) or 'not run / no output'
 lines.append(f"| {r['name']} | {r['count'] if r['count'] is not None else 'see source'} | {r['expected'] or '-'} | {paths} |")
lines+=['','Historical data: immutable Stage5 base bundle. Candidate components and measurement caches can be shared; use the unique-execution resource ledger for cost.','Full hashes and disposition fields are in EVIDENCE_LEDGER.json.']
(OUT/'report/EVIDENCE_LEDGER.md').write_text('\n'.join(lines)+'\n')
print('Ledger entries',len(items))
