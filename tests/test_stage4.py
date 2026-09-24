import numpy as np
import pytest
from annni.stage4 import ROOT,OUT,OLD,read,branch_id,coord_id,array_hash,params,CFG
from annni.stage4_diagnostics import derivative_peaks,coarsen_edges

def test_actual_same_direction_seed_switch_identity():
    rows=read(OUT/'branch_audit/comparisons.json')
    r=next(r for r in rows if r['kappa']==.3 and r['layers']==4 and r['right_h']==.85 and r['comparison_p']==.01)
    assert '/descending/seed101/' in r['left_branch_id']
    assert '/descending/seed307/' in r['right_branch_id']
    assert r['actual_switch_pair_sensitive'] and r['opposite_direction_sensitive'] is False

def test_all_pair_endpoints_same_coordinate_and_hashes():
    for r in read(OUT/'branch_audit/comparisons.json'):
        for endpoint,h in zip(r['endpoints'],[r['left_h'],r['right_h']]):
            a,b=endpoint['density_a'],endpoint['density_b']
            assert a['h']==b['h']==h and a['p']==b['p']==r['comparison_p']
            assert endpoint['comparison_parameter_hashes']==[a['params_sha256'],b['params_sha256']]
            for d in [a,b]:assert array_hash(np.load(ROOT/d['archive'])['params'])==d['params_sha256']

def test_not_applicable_and_unchecked_are_not_false():
    rows=read(OUT/'branch_audit/intervals.json')
    for r in rows:
        if r['status']=='not_applicable':assert r['actual_switch_pair_checked'] is None and r['actual_switch_pair_sensitive'] is None
    assert any(r['opposite_direction_checked'] is None for r in read(OUT/'branch_audit/comparisons.json'))

def test_sensitivity_is_per_p_and_pair():
    rows=read(OUT/'branch_audit/regression_cases.json');r=[x for x in rows if x['case']=='case2']
    assert len(r)==3
    assert not r[0]['actual_switch_pair_sensitive'] and r[1]['actual_switch_pair_sensitive']
    assert all(x['both_preparations_pass'] for x in r)

def test_repair_replaces_all_three_parameters_together():
    reps=read(OUT/'grid_v2/replacement_map.json');rows=read(OUT/'grid_v2/observations.json')
    for r in reps:
        group=[s for s in rows if s['kappa']==r['kappa'] and s['h']==r['h']]
        assert sorted(s['p'] for s in group)==[0,.01,.05]
        assert {s['params_sha256'] for s in group}=={array_hash(params(r['new']))}
        if r['changed']:assert all(s['actual_switch_pair_checked'] is None and s['protocol_changed_neighborhood'] for s in group)

def test_unchanged_physics_reused():
    rows=read(OUT/'grid_v2/observations.json');assert sum(r['cache_status']=='reused_stage3' for r in rows)>=1200
    for r in rows:
        if r['cache_status']=='reused_stage3':assert r['archive'].startswith('results/stage3_v1/density_cache/')

def test_fine_coordinate_ids_unique():
    coords=[i/80 for i in range(20,101)]
    assert len({coord_id(.3,h) for h in coords})==len(coords)
    assert coord_id(.3,.3125)!=coord_id(.3,.31)

def test_no_stencil_crosses_invalid_stitch_or_failure():
    h=np.arange(9)*.0125;y=h*h;valid=np.ones(9,bool);valid[4]=False;edge=np.ones(8,bool);edge[6]=False
    d,pp=derivative_peaks(h,y,valid,edge,CFG['diagnostics'])
    assert np.isnan(d[4]) and np.isnan(d[7:]).all()
    for p in pp:
        ids=p['support_indices'];assert 4 not in ids and not (6 in ids and 7 in ids)
    assert not coarsen_edges(np.array([0,4,8]),edge)[1]

def test_flat_curve_not_resolved():
    h=np.arange(10)*.0125
    d,p=derivative_peaks(h,np.ones(10)*.125,np.ones(10,bool),np.ones(9,bool),CFG['diagnostics'])
    assert not any(r['resolved_under_protocol'] for r in p)

def test_exact_switch_difference_decomposition():
    for row in read(OUT/'branch_audit/comparisons.json'):
        for d in row['decomposition'].values():np.testing.assert_allclose(d['total'],np.array(d['same_chain_change'])+d['switch_change_at_right'],atol=1e-12)

def test_saved_case_density_state_and_invariants():
    from annni.noise import density_checks
    from annni.circuits import observe
    for r in read(OUT/'branch_audit/regression_cases.json'):
        if r['case']!='case2':continue
        for row in r['full_density']:
            d=np.load(ROOT/row['archive']);rho=d['rho'];density_checks(rho);o=observe(rho)
            if row['p']==0:np.testing.assert_allclose(rho,np.outer(d['ideal_state'],d['ideal_state'].conj()),atol=1e-10)
            np.testing.assert_allclose(row['energy']/8,-o['correlations'][1]+.3*o['correlations'][2]-.7*o['mx'],atol=1e-11)
            np.testing.assert_allclose(o['structure_factor'],np.fft.fft(o['correlations']).real/8,atol=1e-12)

def test_pair_comparison_rejects_different_h():
    from annni.stage4 import compare
    r=read(OUT/'branch_audit/regression_cases.json')[0]['candidates']
    with pytest.raises(AssertionError,match='share k,h,L'):compare(r[0],r[1]|{'h':r[1]['h']+.0125},.01)

def test_submission_relative_assets_and_executed_notebook():
    import re
    sub=ROOT/'submission'
    for file in [sub/'report.md',sub/'presentation.html']:
        paths=re.findall(r'\]\((figures/[^)]+)\)|src="(figures/[^"]+)"',file.read_text())
        assert paths
        for pair in paths:
            for p in pair:
                if p:assert (sub/p).is_file()
    nb=read(sub/'submission.ipynb');cells=[c for c in nb['cells'] if c['cell_type']=='code']
    assert [c['execution_count'] for c in cells]==list(range(1,len(cells)+1))
    assert not any(o['output_type']=='error' for c in cells for o in c['outputs'])
    assert any('grid_main.png' in ''.join(c['source']) for c in cells)
