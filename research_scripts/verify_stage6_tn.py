import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from run_stage6_mps import ANNNI,pairs
from tenpy.algorithms.exact_diag import ExactDiag
from annni.upgrade_gates import geometry
n=8;k=.8;h=.35;m=ANNNI(dict(L=n,lattice='Chain',bc_MPS='finite',bc_x='open',kappa=k,h=h));ed=ExactDiag(m,max_size=20000000);ed.build_full_H_from_mpo();actual=ed.full_H.to_ndarray();ids,z,flips=geometry(n);diag=-sum(z[:,i]*z[:,i+1] for i in range(n-1))+k*sum(z[:,i]*z[:,i+2] for i in range(n-2));expected=np.diag(diag).astype(complex)
for f in flips:expected[ids,f]-=h
np.testing.assert_allclose(actual,expected,atol=1e-12)
for n in [64,96,128]:
 for r in range(n//3+1):
  ps=pairs(n,r);assert ps
  assert all(n//4<=i and j<3*n//4 and abs(i+j-(n-1))<=4 and j-i==r for i,j in ps)
dump(OUT/'verification/tn_model_pairs.json',dict(passed=True,max_matrix_error=float(np.max(abs(actual-expected))),pauli_normalization=True,bc='OBC',pair_checks=[64,96,128],version=__import__('tenpy').__version__))
print('TeNPy model and midpoint-pair tests passed')
