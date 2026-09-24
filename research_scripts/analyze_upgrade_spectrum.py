import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.sparse.linalg import eigsh
from annni.upgrade_adapt import *
rows=[]
for task in ['heldout','n12']:
 data=json.loads((OUT/task/'index.json').read_text());failures=sorted([p['methods']['B3'] for p in data if not p['methods']['B3']['joint_pass']],key=lambda r:r['delta_e'])[:4]
 for r in failures:
  n=r['n'];k,h=r['kappa'],r['h'];a=np.load(ROOT/r['archive']);s=a['state'];ids=np.arange(1<<n);permutation=((ids<<1)&((1<<n)-1))|(ids>>(n-1));hs=h_action(s,n,k,h);eig=eigsh(Chain(n).full_matrix(k,h),k=6,which='SA',return_eigenvectors=False,tol=1e-10,maxiter=20000);eig=np.sort(eig)
  rows.append(dict(task=task,n=n,kappa=k,h=h,delta_e=r['delta_e'],fidelity=r['fidelity'],translation_overlap_real=float(np.vdot(s,s[permutation]).real),global_X_overlap=float(np.vdot(s,s[::-1]).real),variance=float(np.vdot(hs,hs).real-r['energy']**2),six_low_energies=eig.tolist(),gap=float(eig[1]-eig[0]),source=r['archive'],interpretation='diagnostic only; no subspace expansion or pass-threshold change'))
dump(OUT/'spectrum_failures.json',rows);print(len(rows))
