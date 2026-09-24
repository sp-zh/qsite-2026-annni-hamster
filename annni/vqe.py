"""Energy-only optimization and post-hoc calibration against frozen ED."""
import time
import numpy as np
from scipy.optimize import minimize
from .circuits import HVAEngine,observe

def optimize(theta,kappa,h,options,n=8):
    engine=HVAEngine(n)
    started=time.perf_counter()
    trace=[]
    def fun(flat):
        value,grad=engine.value_grad(flat,kappa,h)
        trace.append([value,float(np.linalg.norm(grad,np.inf))])
        return value,grad
    fit=minimize(fun,np.asarray(theta).ravel(),jac=True,method='L-BFGS-B',options=options)
    final=fit.x.reshape((-1,3)); state=engine.state(final)
    record=dict(energy=float(fit.fun),nit=int(fit.nit),nfev=int(fit.nfev),njev=int(fit.njev),
                optimization_success=bool(fit.success),status=int(fit.status),message=str(fit.message),
                gradient_inf=float(np.linalg.norm(fit.jac,np.inf)),seconds=time.perf_counter()-started)
    return record,final,state,np.array(trace)

def metrics(state,ed_state,ed_energy,kappa,h,thresholds,n=8):
    obs=observe(state,n); ref=observe(ed_state,n)
    energy=n*(-obs['correlations'][1]+kappa*obs['correlations'][2]-h*obs['mx'])
    de=(energy-ed_energy)/n
    if de < -1e-9: raise RuntimeError(f"Negative variational energy error {de}")
    f=float(abs(np.vdot(ed_state,state))**2)
    result=dict(energy=float(energy),ed_energy=float(ed_energy),delta_e=float(de),fidelity=f,
                epsilon_c=float(np.max(abs(obs['correlations']-ref['correlations']))),
                epsilon_sf=float(np.max(abs(obs['structure_factor']-ref['structure_factor']))),
                epsilon_mx=abs(obs['mx']-ref['mx']),mx=obs['mx'])
    result['observable_pass']=bool(de<=thresholds['delta_e'] and result['epsilon_c']<=thresholds['epsilon_c']
            and result['epsilon_sf']<=thresholds['epsilon_sf'] and result['epsilon_mx']<=thresholds['epsilon_mx'])
    result['state_pass']=bool(f>=thresholds['fidelity'])
    result['joint_pass']=result['observable_pass'] and result['state_pass']
    return result,obs,ref
