import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.upgrade_dynamics import trotter_gates
old=json.loads((ROOT/'results/stage4_upgrade_v1/dynamics/index.json').read_text());checks=[]
for r in [next(x for x in old if x['p']==0 and x['initial']==ref) for ref in ['zero','0011']]:
 a=np.load(ROOT/r['archive']);s=evolve(reference_gates(8,r['initial']),8);g=trotter_gates(8,r['kappa'],r['h'],r['dt']);vals=[vector(observations(s,8))]
 for i in range(1,round(2/r['dt'])+1):
  s=evolve(g,8,rho=s)
  if i%round(.2/r['dt'])==0:vals.append(vector(observations(s,8)))
 error=float(np.max(abs(np.array(vals)-a['observables'])));assert error<1e-11;checks.append(dict(archive=r['archive'],sha256=sha(ROOT/r['archive']),max_error=error,disposition='newly_executed regression of historical sequence'))
rows=json.loads((OUT/'dynamics_validation/index.json').read_text());summary=[]
for p in [0,.01,.05]:
 for dt in [.1,.05]:
  a=[r for r in rows if r['p']==p and r['dt']==dt];summary.append(dict(p=p,dt=dt,configs=len(a),error_quantiles=np.quantile([r['max_total_error'] for r in a],[0,.25,.5,.75,1]).tolist(),cnots=a[0]['cnots']))
static=[]
for k,h in PLAN['quench_coordinates'] if 'quench_coordinates' in PLAN else [(k,h) for k in [.3,.8] for h in [.3,.7,1.6]]:
 s,e,src=reference(8,float(k),float(h));v=vector(observations(s,8));static.append(dict(kappa=k,h=h,static_ED=v.tolist(),dynamics=[r['features']|dict(initial=r['initial'],dt=r['dt'],p=r['p']) for r in rows if r['kappa']==k and r['h']==h]))
dump(OUT/'dynamics_validation/analysis.json',dict(regression=checks,new_summary=summary,static_comparison=static,feature_protocol='Unchanged whole-window arithmetic means and early return; old Stage4 definition, no new fit',claim='Six new quench coordinates; static ground and nonequilibrium means are different observables, not a classifier accuracy test'));print(summary)
