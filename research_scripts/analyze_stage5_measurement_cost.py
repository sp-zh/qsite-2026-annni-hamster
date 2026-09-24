"""Audit the already executed local measurement rotations; no new quantum result."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,sha,dump
current_archives=set()
for name in ['validation','core','refined','full_best','full_raw','n12']:
 index=OUT/'end_to_end'/f'{name}_index.json'
 if not index.exists():continue
 for point in json.loads(index.read_text()):
  records=[point] if 'statistics' in point else [e['record'] for e in point['entries']]
  current_archives.update(r['archive'] for r in records)
rows=[]
for path in sorted((OUT/'end_to_end/measurements').glob('*.json')):
 r=json.loads(path.read_text())
 for budget,groups in r['sampling'].items():
  settings=[]
  for scale,group in enumerate(groups):
   for basis,shots in zip(group['bases'],group['allocations']):
    assert set(basis)<=set('XYZ') and len(basis)==r['n']
    settings.append(dict(scale_index=scale,basis=basis,shots=shots,H=basis.count('X'),RX_pi_over_2=basis.count('Y'),extra_cnots=0))
  rows.append(dict(used_in_current_frozen_analysis=r['archive'] in current_archives,record=str(path.relative_to(ROOT)),archive=r['archive'],n=r['n'],kappa=r['kappa'],h=r['h'],p=r['p'],method=r['method'],shots_per_repetition=int(budget),repetitions=32,settings=settings,one_qubit_rotation_shots=sum(s['shots']*(s['H']+s['RX_pi_over_2']) for s in settings),extra_measurement_cnot_shots=0,preparation_cnot_shots_per_repetition=r['cost'][budget]['gate_shots']))
dump(OUT/'end_to_end/measurement_cost_audit.json',dict(rows=rows,implementation_sha=sha(ROOT/'annni/upgrade_mitigation.py'),basis_rotation='Z: identity; X: Hadamard; Y: RX(+pi/2), followed by Z measurement. The signed parity products are classical postprocessing.',noise_scope='Official noise only follows actual CNOTs. Local measurement rotations have no added CNOT; no additional routing/ancilla is required. Their one-qubit cost is recorded separately.',cost_units='All listed shots and gate-shots are per repetition. Multiply by32 for the executed statistical-repeat campaign. Density simulation computes exact distributions; sampled counts are generated classically, not paid hardware shots.'))
print('Measurement setting audits:',len(rows))
