"""Explain frozen evidence gates without changing a status or threshold."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
folder=OUT/'floating_boundary_scan'
version=next(v for v in [4,3,2] if (folder/f'evidence_map_v{v}.json').exists())
source=folder/f'evidence_map_v{version}.json';rows=[]
for row in json.loads(source.read_text()):
    reasons=[]
    for key,label in [('all_required_controls_present','required_control_missing'),('all_required_solver_stops','required_solver_stop_missing'),('strict_bond_and_initial_agreement','bond_or_initial_agreement_not_established'),('N96_power_q_consistency','N96_power_wavevector_consistency_missing')]:
        if not row[key]:reasons.append(label)
    if row.get('cross_size_K_conflicts'):reasons.append('converged_size_has_valid_K_outside_floating_range')
    if row.get('larger_size_contradiction'):reasons.append('larger_size_conflicting_signature')
    signatures=[]
    for m in row['metrics']:
        failed=[]
        if not all(x<=.9 for x in m['heldout_ratios']['power']):failed.append('power_not_10_percent_better_than_both_competitors_in_all_windows')
        if not m['K_fit_valid']:failed.append('Friedel_fit_not_valid')
        if not m['K_window_stable']:failed.append('Friedel_windows_not_stable')
        if not all(.25<x<.5 for x in m['K_values']):failed.append('K_outside_open_interval_0.25_0.5')
        if not all(.7<=x<=1.3 for x in m['c_uncorrected']):failed.append('OBC_c_outside_0.7_1.3')
        if min(abs(x-np.pi/2) for x in m['q'])<=.015:failed.append('wavevector_not_resolved_from_pi_over_2')
        signatures.append(dict(n=m['n'],chi=m['chi'],initial=m['initial'],solver_stopping_pass=m['solver_stopping_pass'],failed_signature_checks=failed,power_heldout_ratios=m['heldout_ratios']['power'],K=m['K_values'],c=m['c_uncorrected'],source=m['source']))
        if m['n']==128 and m['chi']==256:reasons.extend(f'{m["initial"]}:{x}' for x in failed)
    rows.append(dict(h=row['h'],original_status=row['status'],unmet_floating_evidence_gates=reasons,signatures=signatures))
dump(folder/f'evidence_bottlenecks_v{version}.json',dict(version=version,source=str(source.relative_to(ROOT)),source_sha256=sha(source),rows=rows,
    scope='Descriptive expansion of the existing frozen criteria, not new phase assignments. The legacy candidate status name can mention missing controls even when all solver/bond/initial controls pass and correlation-model separation instead fails. A10percent predictive-error margin is a predeclared engineering discriminator, not a statistical significance test or a proof excluding a phase.'))
print('Explained evidence v',version)
