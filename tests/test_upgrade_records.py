"""Artifact-specific invariants; no expensive campaign reruns."""
import json
from pathlib import Path
import numpy as np
from annni.upgrade_adapt import OUT,ROOT,sha,PLAN
from annni.upgrade_gates import compile_circuit,resources,evolve,observations

def test_frozen_selection_never_oracle():
 rows=json.loads((OUT/'heldout/index.json').read_text())
 assert len(rows)==48
 for point in rows:
  candidates=[r for r in point['candidates'] if r['method']=='cost'];chosen=point['methods']['B3'];best=min(r['energy'] for r in candidates);eligible=[r for r in candidates if r['energy']<=best+8*PLAN['selection_energy_tolerance_per_site']]
  expected=min(eligible,key=lambda r:(r['selected']['cnots'],r['energy']))
  assert expected['archive']==chosen['archive']
  assert len(set(r['ref'] for r in candidates))==3

def test_pilot_actual_23_cnots_and_saved_parameters():
 rows=json.loads((OUT/'ablation/index.json').read_text());pilot=[r['row'] for r in rows if r['kind']=='23-CNOT pilot'];assert len(pilot)==3
 for row in pilot:
  # Fixed-short final checkpoint always has23; energy-selected reference may be saved if better.
  assert row['checkpoints'][-1]['cnots']==23
  s=row['selected'];g=compile_circuit(8,row['ref'],s['words'],s['params']);a=np.load(ROOT/row['archive']);np.testing.assert_allclose(evolve(g,8),a['state'],atol=1e-12)

def test_mitigation_shot_accounting():
 rows=json.loads((OUT/'mitigation/index.json').read_text());assert len(rows)==30
 for row in rows:
  for budget in [10000,100000]:
   for method in ['raw','zne','sv']:assert row['costs'][f'{method}_{budget}']['shots']==budget
   assert row['costs'][f'raw_{budget}']['gate_shots']==budget*row['cnots']
   assert row['costs'][f'sv_{budget}']['groups']==30
   assert row['statistics'][f'zne_{budget}']['replicates']==32

def test_tensor_network_matrix_validation():
 v=json.loads((OUT/'floating/verification.json').read_text());assert v['passed'];assert [r['n'] for r in v['rows']]==[8,12]
 for r in v['rows']:assert r['matrix_max_error']<1e-12 and abs(r['dmrg_energy_error'])<1e-7

def test_dynamics_all_configurations():
 rows=json.loads((OUT/'dynamics/index.json').read_text());assert len(rows)==252
 for row in rows:
  a=np.load(ROOT/row['archive']);assert a['observables'].shape==(11,17)
  np.testing.assert_allclose(a['noise_increment']+a['trotter_error'],a['total_error'],atol=1e-12)
  assert row['cnots']==round(2/row['dt'])*32

def test_search_cost_counts_final_screen_and_no_fixed_pool():
 from annni.upgrade_accounting import search_cost
 base=dict(n=8,key=dict(fixed=False,extended=True),steps=[dict(step=1,nfev=10)],selected=dict(params=[.1]),stop='pool_gradient',nfev=10)
 assert search_cost(base)['pool_gradient_rounds']==2
 base['key']['fixed']=True
 assert search_cost(base)['pool_derivatives']==0
