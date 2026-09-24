"""Four literal reference-circuit controls; no variational fit or projected output."""
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_candidates import gate_table
from annni.stage6_assess import assess
from annni.upgrade_gates import evolve
started=time.perf_counter();rows=[];states={}
for n in [8,12]:
    point=[]
    for basis,reference in [('physical','antiphase'),('wall','alternating')]:
        gates=gate_table(n,basis,reference,[],[]);state=evolve(gates,n);metric=assess(state,n,.55,.01)
        ids=np.arange(1<<n);shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1));rot=state.copy();component=np.zeros_like(state)
        for _ in range(n):component+=rot/n;rot=rot[shift]
        key=f'n{n}_{basis}';states[key]=state
        row=dict(n=n,kappa=.55,h=.01,p=0,basis=basis,reference=reference,gates=gates,cnots=sum(g[0]=='CNOT' for g in gates),
            T0_weight=float(np.vdot(component,component).real),**metric)
        rows.append(row);point.append(row)
    np.testing.assert_allclose(point[0]['observables'],point[1]['observables'],atol=1e-12)
    assert abs(point[0]['energy']-point[1]['energy'])<1e-12
    assert abs(point[0]['T0_weight']-1)<1e-12 and abs(point[1]['T0_weight']-.5)<1e-12
O=OUT/'failure_mechanisms';archive=O/'reference_translation_controls.npz';np.savez_compressed(archive,**states)
dump(O/'reference_translation_controls.json',dict(rows=rows,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),seconds=time.perf_counter()-started,
    scope='Post-evaluation explanatory control at positiveh, four actual parameter-free reference circuits and their literal charged gates. No additional optimization, selection change, free StatePrep or projection used for circuit output. T0 projection is only a mathematical diagnostic; saved states are unprojected circuit outputs. Physical AP reference includes the translation orbit; alternating wall reference decoded with a global spin bit gives a spin-flip pair, so it need not be translation invariant. Equal translation-averaged observables/energy at these reference states do not imply equal ground-state fidelity. This does not prove the adaptive wall pool cannot reach T0 states at greater depth.'))
print([(r['n'],r['basis'],r['cnots'],r['T0_weight'],r['fidelity'],r['observable_pass']) for r in rows])
