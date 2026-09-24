import numpy as np
from annni.stage6_followup import *
from annni.upgrade_mitigation import algebra_check
from annni.stage6_diagnostics import peaks_and_primary,response_curves
from annni.stage6_boundaries import compare
from annni.upgrade_gates import X,Y,Z,one_axis,h_action

def test_target_only_depolarization_asymmetric_state():
 g=[('RX',0,.47),('RX',1,.23),('CNOT',0,1)];p=.17
 ideal=density(g,2,0)
 def channel(wire):
  return (1-p)*ideal+p/3*sum(one_axis(one_axis(ideal,u,wire,2),u.conj(),wire,2,2) for u in [X,Y,Z])
 np.testing.assert_allclose(density(g,2,p),channel(1),atol=1e-12)
 assert np.max(abs(channel(1)-channel(0)))>1e-4

def test_integer_allocation_exact_resource():
 for target in [10000,100000,300000,100001]:
  total,equiv=equal_gate_shots(target);s=alloc(total,3)
  assert sum(f*x for f,x in zip([1,3,5],s))==equiv<=target
  assert sum(f*x for f,x in zip([1,3,5],alloc(total+1,3)))>target
  assert sum(alloc(equiv,30))==equiv and min(alloc(equiv,30))>0

def test_literal_p0_folds_targets_and_sv():
 row=next(iter(read(OUT/'inputs.json').values()));state=data(row)['state'];g=row['gates'];n=8
 for f in [1,3,5]:
  gg=folded(g,f);r=resources(gg,n);assert r['cnots']==f*row['resources']['cnots'];assert r['target_counts']==[f*x for x in row['resources']['target_counts']]
  np.testing.assert_allclose(evolve(gg,n),state,atol=1e-10)
 rho=density(g,n,0);np.testing.assert_allclose(rho,np.outer(state,state.conj()),atol=1e-10);algebra_check(rho)
 rho=density(g,n,.01);assert abs(np.trace(rho)-1)<1e-10;assert np.max(abs(rho-rho.conj().T))<1e-10;assert np.linalg.eigvalsh(rho).min()>-1e-9;algebra_check(rho)
 v=vector(observations(rho,n));np.testing.assert_allclose(v[n:2*n],np.fft.fft(v[:n]).real/n,atol=1e-12)
 pure=vector(observations(state,n));k,h=row['kappa'],row['h']
 np.testing.assert_allclose(np.vdot(state,h_action(state,n,k,h)).real,-n*pure[1]+k*n*pure[2]-h*n*pure[-1],atol=1e-11)

def test_frozen_weights_and_reference_denominators():
 np.testing.assert_allclose(RICHARDSON@np.array([[1,1,1],[1,3,9],[1,5,25]]),[1,0,0],atol=1e-12)
 refs=read(OUT/'window_reference.json');assert len(refs)==6;assert sum(r['frozen_reference']['resolvable'] for r in refs)==5
 for w in refs:
  assert len(w['h'])==17
  name='minus_dm0_dh' if w['kappa']<.5 else 'minus_dmap_dh'
  r=peaks_and_primary(w['h'],response_curves(w['h'],w['values'],8)[name]);assert r==w['frozen_reference']

def test_counts_and_budget_reconstruction():
 for path in list((OUT/'measurements').glob('*.json'))[:12]:
  r=read(path);a=np.load(ROOT/r['archive']);allocs=[x for s in r['settings'] for x in s['allocations']]
  np.testing.assert_array_equal(a['counts'].sum(-1),np.tile(allocs,(32,1)))
  G=sum(sum(s['allocations'])*p['cnots'] for s,p in zip(r['settings'],r['probabilities']));assert G==r['CNOT_shots_per_repeat']
  cc=a['counts'][0];vs=[];offset=0
  for s in r['settings']:
   ds={b:cc[offset+i]/n for i,(b,n) in enumerate(zip(s['bases'],s['allocations']))};offset+=len(s['bases']);vs.append(estimated_vector(ds,8,r['method']=='sv')[0])
  reconstructed=RICHARDSON@np.array(vs) if r['method']=='zne_quadratic' else vs[0];np.testing.assert_allclose(reconstructed,a['samples'][0],atol=1e-12,equal_nan=True)

def test_full_coordinate_fingerprints():
 assert uid({'h':.15000000000001})!=uid({'h':.15})
 assert uid({'h':.15,'p':0})!=uid({'h':.15,'p':.01})
