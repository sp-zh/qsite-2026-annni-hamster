"""Exploratory same-coordinate saved-checkpoint controls for noise response spikes.
No optimizer, deployed selector, reference threshold or confirmation circuit changes.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.upgrade_gates import compile_circuit,evolve,observations,vector,resources
from annni.stage6_noise import physical
from annni.stage6_assess import assess
protocol=OUT/'failure_mechanisms/gate_jump_control_protocol.json'
settings=[(.45,.025,7,31),(.45,.0875,31,63),(.55,.025,6,32),(.55,.1,32,64)]
if not protocol.exists():
    dump(protocol,dict(timestamp=datetime.now(timezone.utc).isoformat(),settings=settings,p=[0,.01,.05],
        selection='Exploratory post-window inspection: two initial gate-count jumps and two spurious low-field interior-response intervals. Not blind confirmation.',
        comparison='At the SAME Hamiltonian coordinate, compare actual saved checkpoints from the SAME original seed/reference growth run. This is not a directional-chain or opposite-reference surrogate.',
        resources='Eight literal N8 circuits,24 exact-density evaluations maximum; shots=None, no optimization, no added deployment samples.',
        limits='Changing growth checkpoint changes both parameters and gates; this is not an isolated one-CNOT causal effect. Full parameters/gates and p0 differences are retained.'))
else:assert json.loads(protocol.read_text())['settings']==[list(x) for x in settings]
data=json.loads((OUT/'legacy_b3/windows_index.json').read_text());rows=[]
for k,h,small,large in settings:
    raw=next(r for r in data if (r['kappa'],r['h'])==(k,h))['selected'];controls=[]
    for count in [small,large]:
        saved=next(c for c in raw['checkpoints'] if c['cnots']==count)
        g=compile_circuit(8,raw['ref'],saved['words'],saved['params']);s=evolve(g,8);assert resources(g,8)['cnots']==count
        arm=dict(n=8,kappa=k,h=h,gates=g,state=s);clean=assess(s,8,k,h);noisy=[]
        for p in [0,.01,.05]:
            _,r=physical(arm,p);noisy.append(dict(p=p,record=r,observables=r['observables']))
        controls.append(dict(cnots=count,reference=raw['ref'],seed=raw['seed'],params=saved['params'],words=saved['words'],gates=g,source_record=raw['raw_record'],source_sha=raw['raw_record_sha'],clean=clean,noise=noisy))
    order_index=8 if k<.5 else 10
    diff=[]
    for j,p in enumerate([0,.01,.05]):
        a,b=[np.asarray(x['noise'][j]['observables']) for x in controls]
        clean_delta=np.asarray(controls[1]['clean']['observables'])-np.asarray(controls[0]['clean']['observables'])
        diff.append(dict(p=p,large_minus_small=b-a,noise_induced_increment=(b-a)-clean_delta,order_component_large_minus_small=float((b-a)[order_index]),order_component_noise_increment=float(((b-a)-clean_delta)[order_index])))
    rows.append(dict(kappa=k,h=h,small=small,large=large,controls=controls,differences=diff))
    dump(OUT/'failure_mechanisms/gate_jump_controls.json',dict(protocol_sha=sha(protocol),rows=rows,
        interpretation='Same-coordinate checkpoint differences isolate the combined gate/parameter choice from changing the Hamiltonian. Noise-induced increments subtract each circuit own p0. They support a preparation-resource contribution to response artifacts, not a physical phase transition or a universal improvement rule.'))
    print(k,h,[(r['p'],r['order_component_large_minus_small'],r['order_component_noise_increment']) for r in diff],flush=True)
