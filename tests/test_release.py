import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import release

def test_input_cannot_escape_package():
 with pytest.raises(ValueError):release.path('../README.md')

def test_active_cohort_and_full_coordinate_identity():
 rows=release.records();assert len(rows)==2718
 assert len({r['point_id'] for _,r in rows})==110
 ids={r['point_id'] for r in release.read(release.F+'/B_index.json')};assert len(ids)==45
 assert len(release.read(release.F+'/A_index.json'))==102

def test_all_estimator_saved_count_reconstruction():
 for method in ['raw','zne_quadratic','sv']:
  r=next(r for _,r in release.records() if r['method']==method and r['p']==.01)
  with np.load(release.path(r['archive'])) as a:np.testing.assert_allclose(release.samples_from_counts(r,a),a['samples'],atol=2e-12,rtol=2e-12)

def test_h0_and_hmid_contract():
 with np.load(release.path('results/baseline/grid_n8.npz')) as a:
  assert a['chi_f'].shape[1]==len(a['h_mid'])==len(a['h'])-1
  assert np.isnan(a['chi_f'][:,0]).all()

def test_reference_layers_and_uncertainty_retained():
 x=release.read('results/stage6_v1/floating_boundary_scan/interval_evidence_v4.json')
 assert x['supported_samples']['supported_floating_sample']==[]
 assert x['lower_transition_bracket'] is None and x['upper_transition_bracket'] is None
 assert sum(w['frozen_reference']['resolvable'] for w in release.read(release.F+'/window_reference.json'))==5

def test_b3_is_not_c0():
 rows=release.read('figures/release_statistics.json')['extensions']
 assert next(r for r in rows if r['cohort']=='low_field_confirmation' and r['method']=='B3')['median_CNOT']==32
 assert next(r for r in rows if r['cohort']=='n12' and r['method']=='B3')['joint_pass']==23
