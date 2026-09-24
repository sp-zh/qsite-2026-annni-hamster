import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
O=OUT/'ablation';dev=json.loads((OUT/'development/index.json').read_text());rows=[]
for k,h in [(0,.2),(.3,.4),(.8,.5)]:
 row=next(p['methods']['B3'] for p in dev if p['kappa']==k and p['h']==h);s=row['selected'];directions=[]
 for reverse in [False,True]:
  g=compile_circuit(8,row['ref'],s['words'],s['params'],reverse=reverse);clean=evolve(g,8);e0=float(np.vdot(clean,h_action(clean,8,k,h)).real);dE=[];dO=[];v0=vector(observations(clean,8))
  for j in range(s['cnots']):
   for pauli in range(3):
    state=evolve(g,8,injection=(j,pauli));dE.append(float(np.vdot(state,h_action(state,8,k,h)).real-e0));dO.append(vector(observations(state,8))-v0)
  slope=float(np.sum(dE)/3);obs_slope=np.sum(dO,axis=0)/3;actual=[noise_record(row,p,reverse=reverse) for p in [0,.01,.05]];name=f'error_rank_k{k}_h{h}_reverse{reverse}.npz';np.savez_compressed(O/name,energy_changes=dE,observable_changes=dO,first_derivative=obs_slope)
  directions.append(dict(reverse=reverse,clean_energy=e0,first_derivative_energy=slope,predicted_energy_p001=e0+.01*slope,actual=actual,archive=str((O/name).relative_to(ROOT)),extra_pure_error_configurations=len(dE)))
 winner=min(directions,key=lambda r:r['predicted_energy_p001']);rows.append(dict(kappa=k,h=h,first_order_ranked_reverse=winner['reverse'],candidates=directions,scope='development-only first-order ranking pilot; main B4 separately uses paid exact p=.01 energy; first-order is not exact at p=.05'))
 dump(O/'single_error_ranking.json',rows);print(k,h,flush=True)
