"""Descriptive N12 noise scope; preserve the frozen boundary matching rule."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'n12_transfer'
summary_path=OUT/'end_to_end/n12_summary.json'
boundary_path=O/'window_boundary_comparison.json'
summary=json.loads(summary_path.read_text())
boundary=json.loads(boundary_path.read_text())
noise=[]
for method in ['B3','H6']:
    for p in [0,.01,.05]:
        r=summary[f'{method}_raw_p{p}_100000']
        noise.append(dict(method=method,p=p,coordinates=r['physical_coordinates'],
            MSE_ED=r['MSE_ED_mean'],MSE_own_p0=r['MSE_own_p0_mean'],
            total_shots=r['total_shots'],total_gate_shots=r['total_gate_shots']))
features=[]
for r in boundary['rows']:
    if r['budget'] is not None or r['estimator']!='raw_sparse_window':continue
    target=r['reference']['primary'];found=r['result']['primary']
    features.append(dict(method=r['method'],p=r['p'],coordinates=r['coordinates'],
        frozen_rule_match=r['matched'],position_error=r['position_error'],
        reference_peak=target,selected_peak=found,
        amplitude_ratio_to_same_sparse_ED=found['value']/target['value'] if found else None,
        interval_width=r['interval_width']))
decomposition_path=OUT/'end_to_end/n12_error_decomposition.json'
decomposition=json.loads(decomposition_path.read_text()) if decomposition_path.exists() else None
largest_preparation_errors={}
if decomposition:
    for method in ['B3','H6']:
        rr=sorted([r for r in decomposition['rows'] if r['method']==method and r['p']==0 and r['budget']==100000],key=lambda r:r['prep_MSE'],reverse=True)
        largest_preparation_errors[method]=[dict(kappa=r['kappa'],h=r['h'],preparation_MSE=r['prep_MSE']) for r in rr[:3]]
dump(O/'noise_scope_interpretation.json',dict(noise=noise,sparse_response=features,
    largest_preparation_errors=largest_preparation_errors,
    sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [summary_path,boundary_path,*([decomposition_path] if decomposition else [])]],
    scope='Twelve preselected coordinates comprise six main-cohort points and six window points. The registered stride selects low-field interior controls and includes no high-field paramagnetic control; no claim of all-phase N12 noise coverage is made. They are not the full36-point transfer cohort or an area-weighted map.100k totalshots per coordinate/p/preparation per repetition;32repetitions. MSE uses the full[C,SF,Mx]vector with acknowledged Fourier redundancy. The sparse6-point ED response differs from the full16-point reference. Frozen matching and failures are unchanged; amplitude retention is a secondary descriptive audit, not a newly tuned acceptance criterion.',
    interpretation='On this fixed subset H6 reduces ED-target MSE at p0/.01 but increases it at p.05. B3 p0 mean is dominated by the retained failure at(.507,.013), which H6 improves substantially in observable MSE. This is not universal N12 improvement. A same-coordinate sparse peak at p.05 survives with only about9% of the ED response amplitude; position agreement alone does not demonstrate boundary recovery.'))
print('N12 noise scope:',len(noise),'comparisons;',len(features),'exact sparse responses')
