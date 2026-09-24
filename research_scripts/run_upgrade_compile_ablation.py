import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_gates import *
old=json.loads((ROOT/'results/stage3_v1/grid/selection_frozen.json').read_text())['rows'];O=OUT/'ablation';rows=[]
for k,h in [(0,.2),(.3,.4),(.8,.5)]:
 r=next(r for r in old if abs(r['kappa']-k)<1e-12 and abs(r['h']-h)<1e-12);a=np.load(ROOT/r['archive']);theta=a['final_params'];pure=a['state'];ed=a['ed_state'];v0=vector(observations(pure,8));ved=vector(observations(ed,8))
 for variant in ['original','reverse_CNOT_direction','reverse_commuting_ZZ_order']:
  gates=reference_gates(8,'plus')
  for gamma,eta,beta in theta:
   blocks=[(i,(i+d)%8,float(t)) for d,t in [(1,gamma),(2,eta)] for i in range(8)]
   if variant=='reverse_commuting_ZZ_order':blocks=blocks[::-1]
   for control,target,t in blocks:
    if variant=='reverse_CNOT_direction':control,target=target,control
    gates += [('CNOT',control,target),('RZ',target,2*t),('CNOT',control,target)]
   gates += [('RX',i,2*float(beta)) for i in range(8)]
  np.testing.assert_allclose(evolve(gates,8),pure,atol=1e-10)
  for p in [0,.01,.05]:
   t=time.perf_counter();rho=density(gates,8,p);v=vector(observations(rho,8));name=f'compile_k{k}_h{h}_{variant}_p{p}.npz';np.savez_compressed(O/name,observables=v,prep=v0-ved,noise=v-v0,total=v-ved)
   rows.append(dict(kappa=k,h=h,p=p,variant=variant,source_old_parameter_archive=r['archive'],original_B0_unchanged=True,new_experiment=True,cnots=resources(gates,8)['cnots'],gate_table=gates,max_c_error=float(max(abs(v[:8]-ved[:8]))),seconds=time.perf_counter()-t,archive=str((O/name).relative_to(ROOT))))
 dump(O/'compile_only.json',rows)
print(len(rows),'compile-only configs')
