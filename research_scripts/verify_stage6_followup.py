"""Portable light verification; no old Stage6 data needed."""
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
from annni.stage6_diagnostics import response_curves,peaks_and_primary
start=time.perf_counter();inputs=read(OUT/'inputs.json');records=[read(p) for p in (OUT/'measurements').glob('*.json')];probabilities=[read(p) for p in (OUT/'probabilities').glob('*.json')]
for r in list(inputs.values())+records+probabilities:assert sha(ROOT/r['archive'])==r['sha256'],r['archive']
for row in list(inputs.values())[::max(1,len(inputs)//4)][:4]:np.testing.assert_allclose(evolve(row['gates'],8),data(row)['state'],atol=1e-10)
for r in records:
 a=np.load(ROOT/r['archive']);counts=a['counts'];allocs=[a for s in r['settings'] for a in s['allocations']];np.testing.assert_array_equal(counts.sum(-1),np.tile(allocs,(32,1)));vs=[];offset=0
 for s in r['settings']:
  ds={b:counts[0,offset+i]/num for i,(b,num) in enumerate(zip(s['bases'],s['allocations']))};offset+=len(s['bases']);vs.append(estimated_vector(ds,8,r['method']=='sv')[0])
 v=RICHARDSON@np.array(vs) if r['method']=='zne_quadratic' else vs[0];np.testing.assert_allclose(v,a['samples'][0],atol=1e-12,equal_nan=True)
 np.testing.assert_allclose(a['samples'][:,8:16],np.fft.fft(a['samples'][:,:8],axis=-1).real/8,atol=1e-12,equal_nan=True)
 assert sum(sum(s['allocations'])*p['cnots'] for s,p in zip(r['settings'],r['probabilities']))==r['CNOT_shots_per_repeat']
 if r['mode']=='equal_gate' and not r['zero_CNOT_control']:
  _,equiv=equal_gate_shots(r['budget']);assert r['CNOT_shots_per_repeat']==equiv*inputs[r['point_id']]['resources']['cnots']
refs=read(OUT/'window_reference.json');assert len(refs)==6 and sum(r['frozen_reference']['resolvable'] for r in refs)==5
coverage=read(OUT/'window_completion/coverage.json');assert all(r['executed_complete_windows']==r['requested_windows'] for r in coverage)
assert read(OUT/'equal_gate_budget/equality_verification.json')['all_equal']
fresh=next(r for r in records if r['disposition']=='newly_executed')
s=fresh['settings'][0];basis=s['bases'][0];num=s['allocations'][0]
pr=fresh['probabilities'][0];distribution=np.load(ROOT/pr['archive'])['p0']
identity=dict(key=fresh['key'],repeat=0,fold=s['fold'],basis=basis)
seed=np.random.SeedSequence([cfg()['seed'],*np.frombuffer(bytes.fromhex(uid(identity)),dtype='<u4').tolist()])
np.testing.assert_array_equal(np.random.default_rng(seed).multinomial(num,distribution),np.load(ROOT/fresh['archive'])['counts'][0,0])
print(json.dumps(dict(status='passed',scientific_payload_hashes=len(inputs)+len(records)+len(probabilities),measurement_records_reconstructed=len(records),circuits_reconstructed=4,seconds=time.perf_counter()-start,scope='All joint-count totals, first repeat per record reconstructed, exact integer CNOT-shots, six/five window denominators, four literal circuits. No new optimization or DMRG.'),indent=2))
