"""Supplementary exact Ising-limit sanity check, separate from frozen RN scoring."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'reference_atlas';source=O/'boundary_reference.json';features=json.loads(source.read_text());rows=[]
for r in features:
 if r['kappa']!=0:continue
 rows.append(dict(n=r['n'],feature=r['feature'],resolvable=r['resolvable'],RN_position=r['position'],RN_grid_interval=[r['low'],r['high']],difference_from_bulk_Ising_h1=r['position']-1 if r['position'] is not None else None,scope='Finite-size response feature offset from a separately known thermodynamic point; not an error in the exact finite-N ED solution.'))
result=dict(timestamp=datetime.now(timezone.utc).isoformat(),level='R0_exact_analytic',kappa=0,bulk_critical_h=1,units='Pauli Hamiltonian with J1=1; project ZZ/X related by global Hadamard to conventional XX/Z',derivation='For kappa=0, Jordan-Wigner bulk quasiparticle dispersion epsilon(q)=2 sqrt(1+h²-2h cos(q)); bulk gap=2 abs(1-h), closing at h=1 for h>=0. This bulk gap is not the exponentially small ordered-cat splitting or the finite-N P+/T0 sector gap.',analytic_regions=dict(ferromagnetic='0<=h<1 in the thermodynamic Ising limit',paramagnetic='h>1 in the thermodynamic Ising limit',critical='h=1; not an interior label'),numerical_limit_unit_test=['tests/test_stage6.py::test_sector_ed_and_reference_limit','tests/test_physics.py::test_exact_transverse_ising_energy'],primary_source_context='Cached primary ANNNI2024 text, Eq7 rationalized kappa->0 limit; exact Ising dispersion stated here independently, not a fitted reference curve.',source_sha=sha(source),finite_N_features=rows,freeze_scope='Supplementary physical sanity comparison after method freeze. Does not change the frozen same-N RN targets, detectors, candidate selection, thresholds or confirmation labels. No extension to a full kappa-dependent true boundary is inferred.')
dump(O/'analytic_Ising_reference.json',result)
print([(r['n'],r['feature'],r['RN_position']) for r in rows])
