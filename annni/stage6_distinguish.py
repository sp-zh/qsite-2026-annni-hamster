"""Offline binary-hypothesis diagnostics, not phase-classifier accuracy."""
import numpy as np
from .upgrade_mitigation import measurement_probs
def distances(a,b):
 quantum=float(.5*np.abs(np.linalg.eigvalsh((a-b+a.conj().T-b.conj().T)/2)).sum());n=int(np.log2(len(a)));pa=[measurement_probs(a,x*n) for x in ['Z','X']];pb=[measurement_probs(b,x*n) for x in ['Z','X']];tv=float(.25*sum(np.abs(x-y).sum() for x,y in zip(pa,pb)))
 if quantum>1+1e-9:raise ArithmeticError(('Invalid trace distance',quantum))
 if tv>quantum+1e-9:raise ArithmeticError(('Classical data-processing violation',tv,quantum))
 return dict(trace_distance=quantum,xz_joint_total_variation=tv,optimal_known_binary_single_copy_error=(1-quantum)/2,quantum_access='Full simulated density matrix, not local100k-shot protocol',measurement='Equal allocation to complete Z/X bitstrings'),pa,pb
def likelihood_errors(pa,pb,budget,seed,repeats=32):
 rng=np.random.default_rng(seed);alloc=[budget//2,budget-budget//2];wrong=[0,0];logs=[];counts=[]
 ratios=[np.log(np.maximum(a,1e-300))-np.log(np.maximum(b,1e-300)) for a,b in zip(pa,pb)]
 for label,ps in enumerate([pa,pb]):
  for _ in range(repeats):
   cc=np.array([rng.multinomial(int(n),p) for n,p in zip(alloc,ps)],dtype=np.int32);counts.append(cc);ll=float(sum(c@l for c,l in zip(cc,ratios)));guess=0 if ll>0 else 1;wrong[label]+=guess!=label;logs.append(ll)
 return dict(counts=np.array(counts),shots_per_query=budget,repeats_per_hypothesis=repeats,error_rate=sum(wrong)/(2*repeats),errors=wrong,log_likelihoods=logs,scope='Oracle known binary templates from full distributions, not given to deployment detector;32rep zeroerrors does not prove zero risk')
