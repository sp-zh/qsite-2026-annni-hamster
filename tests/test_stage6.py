import numpy as np
from annni.stage6_candidates import *
from annni.stage6_reference import sector,solve,ising_reference

def test_cached_measurement_replay_cannot_shrink_completed_index(tmp_path):
 import json,copy,pytest
 from annni.stage6_checkpoint_index import save_measurement_prefix
 def row(h):return dict(n=8,kappa=.5,h=h,entries=[dict(method='B3',estimator='raw',record=dict(p=.01,archive=str(h),sha256='abc',metadata_sha256='def'))])
 path=tmp_path/'index.json';rows=[row(.1),row(.2)]
 assert save_measurement_prefix(path,rows)
 assert not save_measurement_prefix(path,rows[:1])
 assert len(json.loads(path.read_text()))==2
 altered=copy.deepcopy(rows);altered[0]['entries'][0]['record']['sha256']='wrong'
 with pytest.raises(AssertionError):save_measurement_prefix(path,altered)
 assert save_measurement_prefix(path,rows+[row(.3)])
 assert len(json.loads(path.read_text()))==3

def test_completed_noise_summaries_keep_full_coordinate_denominators():
 import json
 from pathlib import Path
 root=Path('results/stage6_v1/end_to_end')
 for task,expected in [('confirmation',96),('validation',24),('core',48),('windows',51),('n12',12)]:
  path=root/f'{task}_summary.json'
  if not path.exists():continue
  for row in json.loads(path.read_text()).values():
   assert row['physical_coordinates']==expected
   assert row['measurement_repeats']==32*expected
   for detector in row['label_repeat_counts'].values():
    assert sum(detector['physical_label'].values())==32*expected

def test_executed_N12_budget_comparison_uses_identical_coordinates():
 import json
 from pathlib import Path
 path=Path('results/stage6_v1/n12_transfer/paired_budget_128_192.json')
 if not path.exists():
  import pytest
  pytest.skip('Paired budget analysis not yet executed')
 data=json.loads(path.read_text());rows=data['rows']
 assert len(rows)==48 and len({(r['kappa'],r['h']) for r in rows})==12
 for method in ['B3','C0','C1','H6']:
  rr=[r for r in rows if r['method']==method]
  assert len(rr)==12 and {r['seed'] for r in rr}=={631}
  assert all(r['cap128']['cnots']<=128 and r['cap192']['cnots']<=192 for r in rr)
  summary=next(r for r in data['summary'] if r['method']==method and r['region']=='all')
  assert sum(summary['outcomes'].values())==12
  for cap in ['cap128','cap192']:
   assert summary[cap]['joint_pass']==sum(r[cap]['joint_pass'] for r in rr)

def test_executed_detector_boundary_physical_denominators():
 import json
 from pathlib import Path
 path=Path('results/stage6_v1/end_to_end/detector_boundary_coverage.json')
 if not path.exists():
  import pytest
  pytest.skip('Detector boundary analysis not yet executed')
 data=json.loads(path.read_text())
 assert data['version']>=2 and len(data['rows'])==96
 for r in data['rows']:
  assert r['requested_physical_slices']==6
  assert r['reference_resolvable_physical_slices']==5
  assert len(r['slices'])==6
  if r['budget'] is not None:
   missing=[s for s in r['slices'] if s['kappa'] in [0.,.3,.5]]
   assert all(s['measurement_repeats']==0 and s['match_fraction']==0 for s in missing)
   expected=0 if r['detector']=='D5' and r['estimator']=='sv' else 3*32
   assert r['total_measurement_window_repeats']==expected
   assert r['mean_match_fraction_given_reference']<=3/5+1e-12

def test_executed_boundary_denominators_keep_missing_windows():
 import json
 from pathlib import Path
 path=Path('results/stage6_v1/end_to_end/boundary_coordinate_coverage.json')
 if not path.exists():
  import pytest
  pytest.skip('Complete window analysis not yet executed')
 data=json.loads(path.read_text())
 assert data['version']>=2
 for r in data['rows']:
  assert r['requested_physical_slices']==6
  assert r['reference_resolvable_physical_slices']==5
  assert len(r['slices'])==6
  if r['budget'] is not None:
   missing=[s for s in r['slices'] if s['kappa'] in [0.,.3,.5]]
   assert all(s['measurement_repeats']==0 and s['match_fraction']==0 for s in missing)
   assert r['total_measurement_window_repeats']==3*32

def test_executed_same_coordinate_distribution_bound():
 import json
 from pathlib import Path
 path=Path('results/stage6_v1/noise_diagnosability/same_coordinate_cross_structure.json')
 if not path.exists():
  import pytest
  pytest.skip('Same-coordinate controls not yet executed')
 rows=json.loads(path.read_text())['rows']
 assert len(rows)==26*3
 for r in rows:
  assert -1e-10<=r['xz_joint_total_variation']<=r['trace_distance']+1e-9<=1+1e-8

def test_compact_measurement_index_preserves_scientific_records():
 import json
 from pathlib import Path
 from annni.stage6_index_records import compact_measurement_record,expand_measurement_record
 from annni.stage6_observation_analysis import wall_estimates
 found={}
 for path in Path('results/stage6_v1/end_to_end/measurements').glob('*.json'):
  r=json.loads(path.read_text())
  found.setdefault(r['method'],r)
  if all(m in found for m in ['raw','zne','zne_quadratic','sv']):break
 if not found:
  import pytest
  pytest.skip('Measurement experiments have not yet executed')
 assert all(m in found for m in ['raw','zne','zne_quadratic','sv'])
 for r in found.values():
  compact=compact_measurement_record(r)
  assert expand_measurement_record(compact)==r
  assert len(json.dumps(compact))<len(json.dumps(r))
  for budget in [None,10000]:
   a,b=wall_estimates(r,budget),wall_estimates(compact,budget)
   if a is None:assert b is None
   else:np.testing.assert_array_equal(a,b)
def test_dw_identity_and_even_walls():
 for n in [8,12]:
  ids,z,_=geometry(n);d=(1-z*np.roll(z,-1,axis=1))//2
  assert np.all(d.sum(1)%2==0)
  for k in [.4,.5,.6,.8]:
   hz=-(z*np.roll(z,-1,axis=1)).sum(1)+k*(z*np.roll(z,-2,axis=1)).sum(1)
   dw=n*(k-1)+(2-4*k)*d.sum(1)+4*k*(d*np.roll(d,-1,axis=1)).sum(1);np.testing.assert_allclose(hz,dw,atol=1e-12)
def test_decode_all_basis_states_and_closure():
 for n in [8,12]:
  b,inv=decode_indices(n);y=np.arange(1<<n);bits=(b[:,None]>>np.arange(n-1,-1,-1))&1;yb=(y[:,None]>>np.arange(n-1,-1,-1))&1
  np.testing.assert_array_equal(bits[:,0],yb[:,0]);np.testing.assert_array_equal(bits[:,:-1]^bits[:,1:],yb[:,1:]);np.testing.assert_array_equal(bits[:,-1]^bits[:,0],yb[:,1:].sum(1)%2);np.testing.assert_array_equal(b[inv],y)
  # all computational basis permutations compared to the actual gate loop
  ids=y.copy()
  for i in range(n-1):ids^=((ids>>(n-1-i))&1)<<(n-2-i)
  np.testing.assert_array_equal(ids,b)
def test_dw_gradient_and_literal_gates():
 rng=np.random.default_rng(17)
 for basis,ref in [('physical','antiphase'),('wall','alternating'),('wall','uniform')]:
  n=8;words=words_pool(n,basis)[::3][:9];p=rng.normal(0,.2,len(words));e,g,s=evaluate(p,words,n,basis,ref,.51,.035)
  fd=[]
  for j in range(len(p)):
   t=p.copy();t[j]+=1e-6;l=evaluate(t,words,n,basis,ref,.51,.035)[0];t[j]-=2e-6;r=evaluate(t,words,n,basis,ref,.51,.035)[0];fd.append((l-r)/2e-6)
  np.testing.assert_allclose(g,fd,atol=2e-8);np.testing.assert_allclose(evolve(gate_table(n,basis,ref,words,p),n),s,atol=1e-12);np.testing.assert_allclose(s,s[::-1],atol=1e-12);assert abs(np.vdot(s,s)-1)<1e-12
def test_sector_ed_and_reference_limit():
 n=8;k=.501;h=.01;s,e,r=solve(n,k,h);assert r['residual']<1e-10
 np.testing.assert_allclose(h_action(s,n,k,h),e*s,atol=1e-10);np.testing.assert_allclose(s,s[::-1],atol=1e-12)
 ids=np.arange(1<<n);shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1));np.testing.assert_allclose(s[shift],s,atol=1e-12)
 assert ising_reference(0)==1;assert abs(ising_reference(1e-9)-1)<1e-8
def test_wall_number_changes_not_restricted_mixer():
 n=8;s=evolve(gate_table(n,'wall','empty',['IYIIIIII'],[.3]),n);_,z,_=geometry(n);d=((1-z*np.roll(z,-1,axis=1))//2).sum(1);assert (abs(s[d==2])**2).sum()>.01
 # no-adjacent-wall projected single-spin flips conserve wall number
 valid=np.all((1-z*np.roll(z,-1,axis=1))*(1-np.roll(z,-1,axis=1)*np.roll(z,-2,axis=1))==0,axis=1)
 for i in range(n):
  flipped=np.arange(1<<n)^(1<<i);mask=valid&valid[flipped];np.testing.assert_array_equal(d[mask],d[flipped[mask]])

def test_wall_density_folding_and_target_channel():
 import pennylane as qml
 n=8;words=['IYIIIIII','IYZIIIII','IIYIZIII'];params=[.31,-.17,.12];gates=gate_table(n,'wall','alternating',words,params);pure=evolve(gates,n)
 for fold in [1,3,5]:np.testing.assert_allclose(evolve(gate_table(n,'wall','alternating',words,params,fold),n),pure,atol=1e-12)
 np.testing.assert_allclose(density(gates,n,0),np.outer(pure,pure.conj()),atol=1e-12)
 dev=qml.device('default.mixed',wires=n,shots=None)
 @qml.qnode(dev)
 def run():
  for g in gates:
   if g[0]=='CNOT':qml.CNOT(g[1:]);qml.DepolarizingChannel(.01,g[2])
   elif g[0]=='H':qml.Hadamard(g[1])
   elif g[0]=='X':qml.PauliX(g[1])
   elif g[0]=='RX':qml.RX(g[2],g[1])
   elif g[0]=='RZ':qml.RZ(g[2],g[1])
  return qml.state()
 rho=density(gates,n,.01);np.testing.assert_allclose(rho,run(),atol=2e-11);assert abs(np.trace(rho)-1)<1e-12;assert np.linalg.eigvalsh(rho).min()>-1e-12

def test_distinguish_data_processing_and_same_state():
 from annni.stage6_distinguish import distances,likelihood_errors
 rng=np.random.default_rng(53);a=rng.normal(size=32)+1j*rng.normal(size=32);b=rng.normal(size=32)+1j*rng.normal(size=32);a/=np.linalg.norm(a);b/=np.linalg.norm(b);rho=.8*np.outer(a,a.conj())+.2*np.eye(32)/32;sigma=.7*np.outer(b,b.conj())+.3*np.eye(32)/32
 r,pa,pb=distances(rho,sigma);assert 0<=r['xz_joint_total_variation']<=r['trace_distance']<=1
 r,_,_=distances(rho,rho);assert abs(r['trace_distance'])<1e-14

def test_friedel_mapping_and_synthetic_recovery():
 from annni.stage6_friedel import SMOOTH,extract,fit_profile
 assert abs(SMOOTH.sum()-1)<1e-14;assert np.max(abs(extract(np.ones(64))[1]))<1e-14
 n=128;j=np.arange(1,n+1);chord=np.maximum(n/np.pi*np.sin(np.pi*j/n),1e-6);x=.5+.08*np.cos(1.2*j+.3)/chord**.37
 assert all(abs(f['K']-.37)<.03 for f in fit_profile(x)['fits'])

def test_oracle_derivative_and_isolation():
 from pathlib import Path
 import ast
 rng=np.random.default_rng(18);target=rng.normal(size=256);target/=np.linalg.norm(target);words=words_pool(8,'wall')[:4];p=np.array([.1,.2,.3,.4]);f,g,s=evaluate(p,words,8,'wall','uniform',.5,.1,target=target)
 for j in range(4):
  d=np.zeros(4);d[j]=1e-6;fd=(evaluate(p+d,words,8,'wall','uniform',.5,.1,target=target)[0]-evaluate(p-d,words,8,'wall','uniform',.5,.1,target=target)[0])/2e-6;assert abs(fd-g[j])<1e-8
 source=Path('annni/stage6_candidates.py').read_text();imports=[n.module for n in ast.walk(ast.parse(source)) if isinstance(n,ast.ImportFrom)];assert not any('reference' in (m or '') or 'assess' in (m or '') for m in imports)

def test_unique_features_no_double_count():
 from annni.stage6_diagnostics import independent_features
 n=8;s=np.ones(1<<n)/np.sqrt(1<<n);v=vector(observations(s,n));changed=v.copy();changed[:n]+=100
 np.testing.assert_array_equal(independent_features(v,n),independent_features(changed,n))

def test_wall_statistics_and_covariance_detectors_controls():
 from annni.stage6_wall_features import features,pure_features,train,predict
 from annni.stage6_detector import train as train_sf,predict as predict_sf
 labels=['ferro-like','antiphase-like','paramagnetic-like'];states=[evolve(reference_gates(8,r),8) for r in ['ghz','antiphase','plus']];values=[pure_features(s,8) for s in states];cfg=train(values,labels,8);sfvalues=[vector(observations(s,8)) for s in states];scfg=train_sf(sfvalues,labels,8)
 for label,s,v,sv in zip(labels,states,values,sfvalues):
  assert predict(v,cfg)['label']==label;assert predict_sf(sv,scfg)['label']==label;assert abs(v[:5].sum()-1)<1e-12
  assert abs(np.arange(0,9,2)@v[:5]-4*(1-sv[1]))<1e-12
 assert predict(features(np.ones(256)/256,0,8),cfg)['label']=='degraded'
 assert predict_sf(np.r_[1,np.zeros(7),np.ones(8)/8,0],scfg)['label']=='degraded'
 assert np.linalg.eigvalsh(cfg['covariance']).min()>0

def test_signed_sv_with_actual_noisy_wall_circuit():
 from annni.stage5_measurement_groups import groups
 from annni.upgrade_mitigation import estimated_vector
 g=gate_table(8,'wall','uniform',['IYZIIIII','IIIYIZII'],[.2,.3]);rho=density(g,8,.05);v,den=estimated_vector(groups(rho),8,True)
 projected=(rho+rho[::-1,:]+rho[:,::-1]+rho[::-1,::-1])/4;weight=np.trace(projected).real;projected/=weight
 np.testing.assert_allclose(v,vector(observations(projected,8)),atol=2e-12);assert abs(den-2*weight)<1e-12
 assert sum(resources(g,8)['target_counts'])==resources(g,8)['cnots']

def test_boundary_denominators_and_missing_intervals():
 from annni.stage6_boundaries import compare,denominator
 from annni.stage6_diagnostics import peaks_and_primary,response_curves
 h=np.arange(5)*.1;v=np.zeros((5,17));v[:,8]=[1,.9,.5,.4,.35];ref=peaks_and_primary(h,response_curves(h,v,8)['minus_dm0_dh']);r=compare(h,v,8,'minus_dm0_dh',ref);assert r['matched'];missing=dict(reference_resolvable=True,algorithm_estimatable=False,matched=False,position_error=None);d=denominator([r,missing]);assert d['requested']==2 and d['matched_fraction_given_reference']==.5
 vv=v.copy();vv[2,:]=np.nan;r=compare(h,vv,8,'minus_dm0_dh',ref);assert not r['matched'];assert np.isnan(r['curve'][1]) and np.isnan(r['curve'][2])

def test_baseline_h_zero_and_hmid_contract_unchanged():
 from annni.diagnostics import validate_dataset
 from pathlib import Path
 with np.load(Path('results/baseline/grid_n8.npz')) as a:assert validate_dataset(a)


def test_stage6_saved_measurement_budgets_and_covariances():
 import json
 from pathlib import Path
 rows=json.loads(Path('results/stage6_v1/end_to_end/pilot_index.json').read_text())
 for row in rows:
  r=row.get('record',row)
  with np.load(r['archive']) as a:
   for budget in [10000,100000]:
    counts=a[f'counts_{budget}'];assert counts.shape[0]==32;np.testing.assert_array_equal(counts.sum(axis=(1,2)),np.full(32,budget));np.testing.assert_allclose(a[f'covariance_{budget}'],np.cov(a[f'samples_{budget}'],rowvar=False),atol=1e-14)

def test_area_weights_do_not_count_refinement_as_extra_area():
 from annni.stage6_area import cell_weights
 for k,h in [(np.linspace(0,1,21),np.linspace(.1,2,20)),(np.array([0,.1,.11,.12,.5,1]),np.array([.1,.11,.3,.9,2]))]:
  w=cell_weights(k,h);assert abs(w.sum()-1.9)<1e-12
  low=cell_weights(k,h,region=[.4,.6,.1,.35]);assert abs(low.sum()-.05)<1e-12


def test_so_wall_pool_exact_small_closure():
 from collections import deque
 m=3;gens=[]
 for word in words_pool(m+1,'wall'):
  w=word[1:];gens.append((sum((p in 'XY')<<j for j,p in enumerate(w)),sum((p in 'ZY')<<j for j,p in enumerate(w))))
 seen=set(gens);queue=deque(gens)
 while queue:
  x,z=queue.popleft()
  for a,b in gens:
   if ((x&b).bit_count()+(z&a).bit_count())%2:
    v=(x^a,z^b)
    if v not in seen:seen.add(v);queue.append(v)
 assert len(seen)==28

def test_frozen_hybrid_is_candidate_union_not_state_projection():
 from annni.stage6_hybrid import components
 assert components('H6',.5,.035,'C3')==['C0','C3']
 assert components('H6',.8,.6,'C3')==['C0']
 assert components('H6',.6000000000000001,.3,'C2')==['C0','C2']
 assert components('C1',.5,.035,None)==['C1']

def test_task_index_names_do_not_mix_n12_resource_or_window_cohorts(tmp_path):
 from annni.stage6_io import candidate_paths
 for name in ['n12_631_0_index.json','n12_631_2_index.json','n12_192_631_0_index.json','n12_window_631_0_index.json']:
  (tmp_path/name).write_text('[]')
 assert [p.name for p in candidate_paths('n12',tmp_path)]==['n12_631_0_index.json','n12_631_2_index.json']
 assert len(candidate_paths('n12_192',tmp_path))==1

def test_common_measurement_streams_are_coordinate_setting_specific():
 from annni.stage6_noise_v2 import stream
 a=stream(8,.501,.035,10000,0,1,'Z'*8).random(20)
 np.testing.assert_array_equal(a,stream(8,.501,.035,10000,0,1,'Z'*8).random(20))
 assert not np.array_equal(a,stream(8,.501,.035,10000,1,1,'Z'*8).random(20))
 assert not np.array_equal(a,stream(8,.502,.035,10000,0,1,'Z'*8).random(20))

def test_confirmation_coordinate_isolation_and_freeze_receipt():
 import json,hashlib,ast
 from pathlib import Path
 from annni.stage6_io import candidate_rows
 root=Path('results/stage6_v1');plan=json.loads((root/'experiment_plan.json').read_text())
 validation={tuple(x) for x in plan['validation']};confirmation={(x['kappa'],x['h']) for x in plan['confirmation']}
 development={(x['kappa'],x['h']) for x in json.loads((root/'failure_mechanisms/benchmark.json').read_text())['points']}
 historical={tuple(x) for x in json.loads((root/'verification/historical_coordinates.json').read_text())}
 assert not (historical & confirmation or historical & validation)
 assert len(validation)==24 and len(confirmation)==96
 assert not (validation & confirmation or development & confirmation or development & validation)
 frozen=root/'confirmation/method_frozen.json'
 if frozen.exists():
  receipt=json.loads(frozen.read_text())
  assert receipt['candidate_code']==hashlib.sha256(Path('annni/stage6_candidates.py').read_bytes()).hexdigest()
  assert receipt['runner_sha']==hashlib.sha256(Path('research_scripts/run_stage6_candidates.py').read_bytes()).hexdigest()
 if (root/'reference_atlas/confirmation_evaluation.json').exists():
  assert len({(r['kappa'],r['h']) for r in candidate_rows('confirmation')})==96
 for file in ['annni/stage6_candidates.py','research_scripts/run_stage6_candidates.py']:
  modules=[node.module or '' for node in ast.walk(ast.parse(Path(file).read_text())) if isinstance(node,ast.ImportFrom)]
  assert not any('reference' in name or 'assess' in name for name in modules)

def test_multisize_pattern_is_not_thermodynamic_truth_and_is_retained():
 from annni.stage6_reference_scopes import scopes
 r=scopes('antiphase-like','Rlarge_ED_interior')
 assert r['physical_label'] is None and r['RN_proxy_label']=='antiphase-like'
 assert r['legacy_reference_level']=='Rlarge_ED_interior'
 assert scopes('ferro-like','R0')['physical_label']=='ferro-like'

def test_ideal_XZ_information_probabilities_need_no_density_allocation():
 from annni.upgrade_gates import evolve
 from annni.upgrade_mitigation import measurement_probs
 rng=np.random.default_rng(74);state=rng.normal(size=16)+1j*rng.normal(size=16);state/=np.linalg.norm(state)
 x=abs(evolve([('H',i) for i in range(4)],4,rho=state))**2
 np.testing.assert_allclose(x,measurement_probs(np.outer(state,state.conj()),'XXXX'),atol=1e-12)

def test_classical_gap_scope_excludes_multiphase_and_moderate_field():
 from annni.stage6_reference_scopes import low_field_support
 assert low_field_support(dict(kappa=.5,h=.01)) is None
 assert low_field_support(dict(kappa=.8,h=.5)) is None
 for n in [8,12]:
  _,z,_=geometry(n)
  for k in [.443,.555,.8]:
   energy=-(z*np.roll(z,-1,axis=1)).sum(1)+k*(z*np.roll(z,-2,axis=1)).sum(1)
   levels=np.unique(np.round(energy,12));assert abs(levels[1]-levels[0]-4*abs(1-2*k))<1e-10

def test_registered_MPS_continuation_preserves_prior_evidence_and_other_fields():
 import json,hashlib,pytest
 from pathlib import Path
 root=Path('results/stage6_v1/floating_boundary_scan')
 if not (root/'evidence_map_v3.json').exists():
  pytest.skip('Registered bounded continuation/evidence v3 not executed yet')
 receipt=json.loads((root/'evidence_v3_derivation.json').read_text())
 for path,expected in receipt['old_files'].items():
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
 old={r['h']:r for r in json.loads((root/'evidence_map_v2.json').read_text())}
 new={r['h']:r for r in json.loads((root/'evidence_map_v3.json').read_text())}
 assert old.keys()==new.keys()
 for h,r in new.items():
  if h!=.425:
   assert r['status']==old[h]['status']
   assert r['all_required_solver_stops']==old[h]['all_required_solver_stops']
 continuation=json.loads((root/'final_continuation_index.json').read_text())
 assert len(continuation)==1 and continuation[0]['h']==.425
 assert continuation[0]['initial']=='antiphase' and continuation[0]['n']==128
 assert continuation[0]['options']['max_E_err']==1e-9
 assert continuation[0]['options']['max_S_err']==1e-6

def test_map_reference_endpoint_roundoff_is_not_cache_rounding():
 from annni.stage6_reference_roundoff import map_reference,endpoint_value
 from annni.stage6_common import uid
 k=float(np.nextafter(.3,np.inf));obs=dict(structure_factor=np.array([.8,0,.1,0,0,0,.1,0]),mx=.1)
 plain,_=map_reference(8,.3,.2,obs,.65)
 rounded,meta=map_reference(8,k,.2,obs,.65)
 assert plain==rounded and rounded[0]=='ferro-like'
 assert meta['original_coordinates'][0]==k
 assert endpoint_value(.30000000001,[.3])==.30000000001
 assert uid(dict(kappa=k))!=uid(dict(kappa=.3))
