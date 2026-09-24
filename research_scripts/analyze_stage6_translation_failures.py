"""Full-state diagnostic only: never a projected preparation or new acceptance rule."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.upgrade_gates import h_action,observations,vector
rows=[];sources=[]
for task,folder in [('confirmation','confirmation'),('n12','n12_transfer'),('n12_window','n12_transfer'),('n12_192','n12_transfer')]:
    path=OUT/f'{folder}/{task}_paired_summary.json'
    if not path.exists():continue
    source=json.loads(path.read_text());sources.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path)))
    for r in source['rows']:
        if r['method']!='H6' or not r['observable_pass'] or r['state_pass']:continue
        n=r['n'];state=np.load(ROOT/r['source'])['state'];ids=np.arange(1<<n)
        shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1));rotations=[state]
        for _ in range(1,n):rotations.append(rotations[-1][shift])
        components=np.fft.fft(np.asarray(rotations),axis=0)/n
        weights=np.sum(abs(components)**2,axis=1);assert abs(weights.sum()-1)<1e-9
        exact_vector=vector(observations(state,n));sectors=[];reconstructed_observables=np.zeros_like(exact_vector)
        for k,weight in enumerate(weights):
            if weight<1e-12:continue
            component=components[k]/np.sqrt(weight);hs=h_action(component,n,r['kappa'],r['h'])
            energy=float(np.vdot(component,hs).real);obs=vector(observations(component,n))
            reconstructed_observables+=weight*obs
            sectors.append(dict(momentum_index=k,weight=float(weight),energy=energy,
                energy_error_per_site=(energy-r['ed_energy'])/n,
                residual=float(np.linalg.norm(hs-energy*component)),
                max_observable_change_relative_to_unprojected=float(np.max(abs(obs-exact_vector)))))
        observable_identity_error=float(np.max(abs(reconstructed_observables-exact_vector)))
        energy_identity_error=abs(sum(s['weight']*s['energy'] for s in sectors)-r['energy'])
        assert observable_identity_error<1e-9 and energy_identity_error<1e-9
        conditional_fidelity=r['fidelity']/weights[0]
        assert conditional_fidelity<1+1e-8
        rows.append(dict(task=task,n=n,kappa=r['kappa'],h=r['h'],basis=r['basis'],reference=r['reference'],cnots=r['cnots'],original_fidelity=r['fidelity'],
            original_joint_pass=r['joint_pass'],original_observable_pass=r['observable_pass'],
            momentum_weights=weights,conditional_T0_fidelity_diagnostic=float(conditional_fidelity),sectors=sectors,
            observable_weighted_identity_error=observable_identity_error,energy_weighted_identity_error=energy_identity_error,
            state_archive=r['source'],state_sha256=sha(ROOT/r['source'])))
dump(OUT/'failure_mechanisms/translation_sector_diagnostic.json',dict(rows=rows,sources=sources,
    inclusion_rule='All H6 selected observable-pass/state-fail rows in the named completed cohorts, without fidelity-based subset tuning.',
    scope='Offline full-state-access diagnostic. Momentum components are mathematical projections, not physically prepared states, deployable candidates or free symmetry verification. No projected state is saved as circuit output; original fidelity, all state failures and all acceptance thresholds remain unchanged. No oracle selection or enlarged target subspace. Component conditional fidelity is original ED fidelity divided by exact T0 weight, using the verified positive-field ED T0 reference. Energy differences of these components are not an exact low-energy spectrum.'))
print('Translation diagnostic rows',len(rows))
for task in sorted({r['task'] for r in rows}):
    rr=[r for r in rows if r['task']==task]
    print(task,len(rr),'T0 weights',[round(r['momentum_weights'][0],6) for r in rr],
          'conditional fidelity min',min(r['conditional_T0_fidelity_diagnostic'] for r in rr))
