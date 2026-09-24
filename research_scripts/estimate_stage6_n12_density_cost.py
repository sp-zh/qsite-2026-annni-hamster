"""Engineering extrapolation from the executed pilot; never a batch timing claim."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_index_records import expand_measurement_record
from scipy.optimize import nnls
O=OUT/'n12_transfer';pilot=json.loads((O/'density_pilot_cost.json').read_text())
records=[expand_measurement_record(r) for r in pilot['records']]
def design(gates,p):
    cn=sum(g[0]=='CNOT' for g in gates)
    return [len(gates)-cn,cn,cn*(p>0)]
x=np.array([design(r['key']['gates'],r['p']) for r in records]);y=np.array([r['seconds'] for r in records])
coef,residual=nnls(x,y);rows=[]
for point in json.loads((O/'noise_coordinates.json').read_text()):
    for method in ['B3','H6']:
        arm=load(point['kappa'],point['h'],method,12,task=point['source_task'])
        for p in [0,.01,.05]:
            features=design(arm['gates'],p)
            rows.append(dict(kappa=point['kappa'],h=point['h'],method=method,p=p,gate_counts=features,estimated_density_seconds=float(np.dot(features,coef))))
dump(O/'density_batch_cost_estimate.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),code_sha=sha(__file__),pilot_sha=sha(O/'density_pilot_cost.json'),design=['one_qubit_gates','CNOTs','noisy_CNOTs'],nonnegative_seconds_per_gate=coef,fit_residual_L2=residual,pilot_actual_seconds=y,pilot_fitted_seconds=x@coef,rows=rows,total_estimated_seconds=sum(r['estimated_density_seconds'] for r in rows),scope='Estimate only from six actual probability calculations at one coordinate; not observed batch duration. Includes all12coordinates andbothmethods/all3p before cache reuse, excludes sampling and analysis. Gate timing model is an engineering extrapolation, not a guaranteed completion time or a new experiment allocation. Original deadline and scientific configuration unchanged.'))
print('Estimated full batch minutes',sum(r['estimated_density_seconds'] for r in rows)/60,'pilot residual',residual)
