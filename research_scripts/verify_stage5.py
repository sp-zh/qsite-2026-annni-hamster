"""Check real archives, provenance, parameter reloads and finite-shot budgets."""
import sys,json,time,hashlib,platform,importlib.metadata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_selection import symmetry
from annni.upgrade_mitigation import estimated_vector,LINEAR
assert platform.python_version()==PLAN['python'].split()[0], 'Python differs from frozen run; use the locked environment or a separately configured run'
for package,version in PLAN['versions'].items():assert importlib.metadata.version(package)==version, ('Frozen environment differs',package,version,importlib.metadata.version(package))
start=time.perf_counter();protected=json.loads((OUT/'verification/protected_inputs.json').read_text());excluded=set(json.loads((ROOT/'PACKAGE_MANIFEST_STAGE5.json').read_text()).get('excluded_downloaded_sources',[])) if (ROOT/'PACKAGE_MANIFEST_STAGE5.json').exists() else set();assert all('/sources/' in name for name in excluded);nondata_metadata_changes=[name for name,d in protected.items() if Path(name).name=='.DS_Store' and (not (ROOT/name).exists() or sha(ROOT/name)!=d)];changed=[name for name,d in protected.items() if Path(name).name!='.DS_Store' and ((not (ROOT/name).exists() and name not in excluded) or ((ROOT/name).exists() and sha(ROOT/name)!=d))];assert not changed,changed[:10]
if (OUT/'metadata.json').exists():
 for name,d in json.loads((OUT/'metadata.json').read_text())['code_hashes'].items():assert sha(ROOT/name)==d,('Changed Stage5 fingerprint',name)
mps_manifest=OUT/'floating_validation/archive_manifest.json'
if mps_manifest.exists():
 for name,d in json.loads(mps_manifest.read_text())['files'].items():assert sha(ROOT/name)==d,('MPS artifact changed',name)
counts=dict(protected=len(protected),selected=0,noise=0,measurements=0,probabilities=0)
for p in (OUT/'selected').glob('*.json'):
 r=json.loads(p.read_text());assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);s=r['selected'];state=state_and_grad(s['params'],s['words'],r['n'],r['ref'],r['kappa'],r['h'])[2];np.testing.assert_allclose(state,a['state'],atol=1e-11);assert abs(np.vdot(state,state)-1)<1e-10;np.testing.assert_allclose(state,state[::-1],atol=1e-10);g=compile_circuit(r['n'],r['ref'],s['words'],s['params']);assert resources(g,r['n'])['cnots']==s['cnots'];assert all(min(abs(a-b),r['n']-abs(a-b))<=2 for a,b in resources(g,r['n'])['cnot_order']);counts['selected']+=1
for p in (OUT/'noise/cache').glob('*.json'):
 r=json.loads(p.read_text());assert p.stem==hashlib.sha256(json.dumps(r['key'],sort_keys=True).encode()).hexdigest();assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);np.testing.assert_allclose(a['prep']+a['noise'],a['total'],atol=1e-12);np.testing.assert_allclose(a['structure_factor'],np.fft.fft(a['correlations']).real/r['n'],atol=1e-11);assert r['cnots']==r['noise_channels']==sum(r['target_counts']);counts['noise']+=1
for p in (OUT/'end_to_end/measurements').glob('*.json'):
 r=json.loads(p.read_text());assert p.stem==hashlib.sha256(json.dumps(r['key'],sort_keys=True).encode()).hexdigest();assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);n=r['n'];assert all(min(abs(g[1]-g[2]),n-abs(g[1]-g[2]))<=2 for g in r['key']['gates'] if g[0]=='CNOT')
 for budget in ['10000','100000']:
  counts_array=a['counts_'+budget];assert counts_array.shape[0]==32;np.testing.assert_array_equal(counts_array.sum((1,2)),int(budget));assert sum(sum(g['allocations']) for g in r['sampling'][budget])==int(budget);vs=[];offset=0
  for group in r['sampling'][budget]:
   bases=group['bases'];alloc=group['allocations'];dist={b:counts_array[0,offset+i]/alloc[i] for i,b in enumerate(bases)};vs.append(estimated_vector(dist,n,r['method']=='sv')[0]);offset+=len(bases)
  v=LINEAR@np.array(vs) if r['method']=='zne' else vs[0];np.testing.assert_allclose(v,a['samples_'+budget][0],atol=1e-12,equal_nan=True);np.testing.assert_allclose(np.cov(a['samples_'+budget],rowvar=False),r['statistics'][budget]['covariance'],atol=1e-12,equal_nan=True)
 counts['measurements']+=1
for p in (OUT/'end_to_end/probabilities').glob('*.json'):
 r=json.loads(p.read_text());assert p.stem==hashlib.sha256(json.dumps(r['key'],sort_keys=True).encode()).hexdigest();assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive'])
 expected=2+r['key']['n']*(r['key']['n']-1)//2 if r['key']['sv'] else 2
 assert len(r['bases'])==expected and len(set(r['bases']))==expected
 for i in range(len(r['bases'])):v=a[f'p{i}'];assert abs(sum(v)-1)<1e-10 and min(v)>=0
 counts['probabilities']+=1
from annni.stage5_hva_baseline import key_for
from annni.stage5_e2e import hva_gates
from annni.circuits import HVAEngine
hva_engine=HVAEngine(8);counts['corrected_auxiliary_HVA']=0
for p in (OUT/'end_to_end/hva_v2').glob('*.json'):
 r=json.loads(p.read_text());assert r['key']==key_for(r['kappa'],r['h']);assert sha(ROOT/r['archive'])==r['sha256'];a=np.load(ROOT/r['archive']);chosen=int(np.argmin([t['energy'] for t in r['trials']]));np.testing.assert_allclose(a['theta'],a['finals'][chosen],atol=0)
 for final,trial in zip(a['finals'],r['trials']):assert abs(hva_engine.value_grad(final.ravel(),r['kappa'],r['h'])[0]-trial['energy'])<1e-8
 np.testing.assert_allclose(evolve(hva_gates(a['theta'],8),8),a['state'],atol=1e-11);counts['corrected_auxiliary_HVA']+=1
for name in ['core','refined']:
 for point in json.loads((OUT/'end_to_end'/f'{name}_index.json').read_text()):
  source=point['B0_source'];a=np.load(ROOT/source['archive']);theta=a['theta'] if 'theta' in a else a['final_params'];g=json.loads(json.dumps(hva_gates(theta,8)))
  if 'metadata' in source:
   r=json.loads((ROOT/source['metadata']).read_text());assert abs(r['kappa']-point['kappa'])<1e-12 and abs(r['h']-point['h'])<1e-12
  for e in point['entries']:
   if e['arm']=='B0_raw':assert e['record']['key']['gates']==g
from annni.stage5_baseline_selectors import choose as baseline_choose
for index in (OUT/'selector_benchmark').glob('*/index.json'):
 for point in json.loads(index.read_text()):
  if point.get('reoptimization',{}).get('triggered'):
   c=point['reoptimization']['candidate'];assert c['n']==point['n'] and abs(c['kappa']-point['kappa'])<1e-12 and abs(c['h']-point['h'])<1e-12
  for rule in ['S0','S1']:assert baseline_choose(point['candidates'],rule)['candidate']['uid']==point['selectors'][rule]['candidate']['uid'],('Baseline compatibility',index,rule,point['kappa'],point['h'])
sets=[set(map(tuple,PLAN[k])) for k in ['validation_v2','test_v2','n12_test_v2']];assert all(not a&b for i,a in enumerate(sets) for b in sets[i+1:]);freeze=json.loads((OUT/'selector_frozen.json').read_text())
for task in ['test','n12test']:
 r=json.loads((OUT/f'selector_benchmark/{task}/unsealed.json').read_text());assert r['freeze_sha']==sha(OUT/'selector_frozen.json') and r['timestamp']>freeze['timestamp']
for p in (OUT/'reopt').glob('*.json'):
 r=json.loads(p.read_text());assert r['nit']<=2000
from annni.diagnostics import validate_dataset
for name in ['grid_n8','slices_n8','slices_n12','slices_n16']:validate_dataset(np.load(ROOT/f'results/baseline/{name}.npz'))
result=dict(passed=True,nondata_metadata_changes=nondata_metadata_changes,counts=counts,seconds=time.perf_counter()-start,scope='All available completed archives; partial counts are not completion assertions',limits='N12 positivity follows validated CPTP execution, trace/Hermiticity checked at runtime; no full 4096-eigenvalue PSD calculation');dump(OUT/'verification/result_audit.json',result);print(json.dumps(result,indent=2))
