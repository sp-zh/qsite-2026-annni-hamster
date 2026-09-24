import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.sparse.linalg import expm_multiply
from annni.stage5_adapt import *
from annni.upgrade_dynamics import *
from annni.model import Chain
O=OUT/'dynamics_validation';O.mkdir(exist_ok=True);cfg=dict(PLAN['dynamics']);cfg['h']=[.3,.7,1.6];cfg['dt']=PLAN['quench_dt'];rows=[];started=time.perf_counter()
for k in cfg['kappa']:
 for h in cfg['h']:
  H=Chain(8).full_matrix(k,h)
  for ref in cfg['initial']:
   init=evolve(reference_gates(8,ref),8);exact=expm_multiply(-1j*H,init,start=0,stop=2,num=11,endpoint=True);exact_v=np.array([vector(observations(s,8)) for s in exact]);exact_ret=np.array([abs(np.vdot(init,s))**2 for s in exact])
   for dt in cfg['dt']:
    gates=trotter_gates(8,k,h,dt);stride=round(.2/dt);ideal=None
    for p in cfg['p']:
     guard();name=f'k{k:.2f}_h{h:.2f}_{ref}_dt{dt:.2f}_p{p:.2f}';meta=O/(name+'.json');archive=O/(name+'.npz');key=dict(kappa=k,h=h,initial=ref,dt=dt,p=p,backend=sha(ROOT/'annni/upgrade_gates.py'),dynamics=sha(ROOT/'annni/upgrade_dynamics.py'))
     if meta.exists():
      row=json.loads(meta.read_text());assert row['key']==key and row['sha256']==sha(archive);rows.append(row)
      if p==0:ideal=np.load(archive)['observables']
      continue
     t=time.perf_counter();s=init.copy() if p==0 else np.outer(init,init.conj());vals=[vector(observations(s,8))];ret=[1.]
     for step in range(1,round(2/dt)+1):
      s=evolve(gates,8,p,rho=s)
      if step%stride==0:
       vals.append(vector(observations(s,8)));ret.append(float(abs(np.vdot(init,s))**2 if p==0 else np.vdot(init,s@init).real))
     vals=np.array(vals)
     if p==0:ideal=vals.copy()
     np.savez_compressed(archive,times=cfg['times'],observables=vals,return_probability=ret,exact_observables=exact_v,exact_return=exact_ret,trotter_error=ideal-exact_v,noise_increment=vals-ideal,total_error=vals-exact_v)
     row=dict(key=key,n=8,bc='PBC',kappa=k,h=h,initial=ref,dt=dt,p=p,seconds=time.perf_counter()-t,cnots=round(2/dt)*resources(gates,8)['cnots'],cnot_per_step=resources(gates,8)['cnots'],gate_schedule=gates,noise_channels=round(2/dt)*resources(gates,8)['cnots'],max_total_error=float(np.max(abs(vals-exact_v))),max_trotter_error=float(np.max(abs(ideal-exact_v))),max_noise_increment=float(np.max(abs(vals-ideal))),features=dict(mean_c1=float(vals[:,1].mean()),mean_sf0=float(vals[:,8].mean()),mean_sfpi2=float(vals[:,10].mean()),mean_mx=float(vals[:,-1].mean()),mean_return=float(np.mean(ret)),early_return=float(ret[1])),heldout_h=True,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),disposition='newly_executed');dump(meta,row);rows.append(row)
    dump(O/'index.json',rows);print(name,len(rows),round(time.perf_counter()-started,2),flush=True)
