"""Portable, bounded raw-source reproduction from a clean extracted project.
Run using the locked Python executable; never starts full optimization queues.
"""
import sys,hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from annni.upgrade_gates import evolve,h_action,observations,vector
from annni.stage6_candidates import gate_table
start=time.perf_counter();out=ROOT/'results/stage6_v1';rows=json.loads((out/'domain_wall_candidates/development_101_0_index.json').read_text());checks=[]
for row in rows[:2]:
 for method in ['C0','C3']:
  r=row['methods'][method]['selected'];a=ROOT/r['archive'];assert hashlib.sha256(a.read_bytes()).hexdigest()==r['sha256'];c=r['selected'];g=gate_table(r['n'],r['basis'],r['ref'],c['words'],c['params']);state=evolve(g,r['n']);saved=np.load(a)['state'];np.testing.assert_allclose(state,saved,atol=1e-10);assert abs(np.vdot(state,state)-1)<1e-10;e=float(np.vdot(state,h_action(state,r['n'],r['kappa'],r['h'])).real);checks.append(dict(method=method,kappa=r['kappa'],h=r['h'],energy=e,state_max_error=float(np.max(abs(state-saved))),CNOTs=sum(x[0]=='CNOT' for x in g)))
# Reload real whole-bitstring counts and reconstruct one saved raw estimate.
from annni.upgrade_mitigation import estimated_vector
records=json.loads((out/'end_to_end/pilot_index.json').read_text());item=next(x.get('record',x) for x in records if x.get('record',x)['method']=='raw');data=np.load(ROOT/item['archive']);b=10000;counts=data[f'counts_{b}'][0];settings=item['sampling'][str(b)][0];prob={basis:c/amount for basis,c,amount in zip(settings['bases'],counts,settings['allocations'])};v,_=estimated_vector(prob,8,False);np.testing.assert_allclose(v,data[f'samples_{b}'][0],atol=1e-12);assert int(counts.sum())==b
print(json.dumps(dict(status='passed',seconds=time.perf_counter()-start,circuits=checks,raw_measurement_counts_reconstructed=True,scope='Four actual saved circuits and one whole-bitstring raw measurement. No full scientific rerun; MPS convergence and phase claims require the full evidence tables.'),indent=2))
