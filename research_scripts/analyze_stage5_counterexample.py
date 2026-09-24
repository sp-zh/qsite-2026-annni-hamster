import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.sparse.linalg import eigsh
from annni.stage5_adapt import *
from annni.stage5_selection import *
old=json.loads((ROOT/'results/stage4_upgrade_v1/heldout/index.json').read_text());p=next(x for x in old if x['kappa']==.975 and x['h']==.15);a=load_candidates(p['candidates']);E,V=eigsh(Chain(8).full_matrix(.975,.15),k=8,which='SA',tol=1e-12);order=np.argsort(E);E=E[order];V=V[:,order]
rows=[]
for c in a:
 s=state_and_grad(np.array(c['params']),c['words'],8,c['ref'],.975,.15)[2];rows.append(c|dict(observables={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in observations(s,8).items()},fixed_lowest8_subspace_weight=float(sum(abs(V.conj().T@s)**2))))
dump(OUT/'selection_audit/counterexample.json',dict(candidates=rows,spectrum=[dict(eigensolver_energy=float(e),**symmetry(s,8,.975,.15)) for e,s in zip(E,V.T)],note='Entire saved cost-ADAPT candidate set spans multiple resources; the 31/32-CNOT comparison is one pair, not a description of every candidate. Low fidelity alone does not establish a wrong phase label. Fixed lowest8 overlap auxiliary only, never acceptance.'))
