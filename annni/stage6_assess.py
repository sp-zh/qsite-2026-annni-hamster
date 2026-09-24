"""Post-generation ED evaluation, never imported by candidate generation."""
from .stage6_common import *
from .stage6_reference import record
from .stage6_candidates import evaluate
from .upgrade_gates import observations,vector,h_action
def assess(state,n,k,h):
 ed=record(n,k,h);target=np.load(ROOT/ed['archive'])['state'];a=observations(state,n);b=observations(target,n);hs=h_action(state,n,k,h);e=float(np.vdot(state,hs).real);residual=float(np.linalg.norm(hs-e*state));ids=np.arange(1<<n);shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1));translation=np.vdot(state,state[shift]);parity=np.vdot(state,state[::-1]);de=(e-ed['energy'])/n
 if de < -1e-9:raise ArithmeticError(('Negative variational energy error',n,k,h,de))
 ec=float(max(abs(a['correlations']-b['correlations'])));es=float(max(abs(a['structure_factor']-b['structure_factor'])));em=abs(a['mx']-b['mx']);f=float(abs(np.vdot(target,state))**2);op=de<=.001 and ec<=.02 and es<=.02 and em<=.02;sp=f>=.99
 return dict(state_energy_residual=residual,energy_variance=residual**2,parity_real=float(parity.real),parity_imag=float(parity.imag),translation_real=float(translation.real),translation_imag=float(translation.imag),energy=e,ed_energy=ed['energy'],delta_e=de,epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,fidelity=f,observable_pass=bool(op),state_pass=bool(sp),joint_pass=bool(op and sp),reference_numerical_ambiguous=ed['reference_numerical_ambiguous'],ed_source=ed['archive'],observables=vector(a).tolist(),ed_observables=vector(b).tolist())
def assess_run(row):
 selected=assess(np.load(ROOT/row['archive'])['state'],row['n'],row['kappa'],row['h']);candidates=[]
 for c in row['checkpoints']:
  s=evaluate(c['params'],c['words'],row['n'],row.get('basis','physical'),row['ref'],row['kappa'],row['h'])[2];candidates.append(dict(cnots=c['cnots'],reason=c['reason'],**assess(s,row['n'],row['kappa'],row['h'])))
 return dict(**selected,basis=row.get('basis','physical'),reference=row['ref'],seed=row['seed'],source_stop=row.get('stop'),optimizer_success=row['selected']['optimizer_success'] if len(row['selected']['params']) else None,reported_optimizer_success=row['selected']['optimizer_success'],optimization_applicable=bool(len(row['selected']['params'])),candidate_exists=any(c['joint_pass'] for c in candidates),parameter_count=len(row['selected']['params']),gate_count=row['selected']['gate_count'],pool_gradient_evaluations=row.get('pool_gradient_evaluations'),cnots=row['selected']['cnots'],depth=row['selected']['unitary_depth'],nfev=row['nfev'],seconds=row['seconds'],candidates=candidates,source=row['archive'])
