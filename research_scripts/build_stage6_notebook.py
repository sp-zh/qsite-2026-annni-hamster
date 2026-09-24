"""Build a portable research companion; execute separately with the locked Python."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nbformat as nb
from annni.stage6_common import ROOT,OUT,sha
cells=[]
def md(text):cells.append(nb.v4.new_markdown_cell(text))
def code(text):cells.append(nb.v4.new_code_cell(text))
md('# ANNNI Stage 6 — phase-diagram research evidence\n\nThis executed companion reads saved experiments and reruns a lightweight literal-circuit check. It does **not** rerun the full optimization, ED atlas or DMRG queues. State accuracy, finite-size physical features and physical phase interpretation are separate outcomes.')
md('## Scope and conventions\n\nPBC circuit model: H = −ΣZZ + κΣZZ(next-nearest) − hΣX. Wire 0 is the most significant bit. Structure factors include self-correlation 1/N. All positive-field pure references use the same Hamiltonian; h=0 is excluded. MPS evidence is OBC and is not transplanted into N8 labels. Noise acts only on the target after every actual CNOT, including preparation, decoding and folding.\n\nIndependent coordinate confirmation follows development/validation freezing; it tests new-coordinate interpolation, not completely unseen regions of parameter space. Detector ED outputs are not independent phase truth.')
code("""from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path.cwd().resolve()
while not (ROOT/'annni/stage6_common.py').exists():
    if ROOT==ROOT.parent: raise RuntimeError('Run inside the extracted ANNNI project')
    ROOT=ROOT.parent
sys.path.insert(0,str(ROOT))
OUT=ROOT/'results/stage6_v1'
read=lambda path: json.loads((OUT/path).read_text())
plt.rcParams.update({'figure.figsize':(9,4),'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
print('Notebook execution UTC:',datetime.datetime.now(datetime.timezone.utc).isoformat())
print('Saved experiment:',read('experiment_plan.json')['run_id'])
print('This execution recomputes only the explicitly labelled check below.')""")
md('## Saved candidate experiments\n\nThe following counts are read from complete saved candidate evaluations. Development improvements are not confirmation results. Shared cached searches do not constitute new independent executions.')
code("""for relative in ['failure_mechanisms/development_paired_summary.json','confirmation/confirmation_paired_summary.json','confirmation/stability_paired_summary.json','n12_transfer/n12_paired_summary.json']:
    path=OUT/relative
    if not path.exists():
        print(relative,': not yet executed/summarized'); continue
    data=json.loads(path.read_text())
    print('\\n',relative)
    for row in data['summary']:
        if row['region']=='all':
            print(row['method'],'joint',str(row['joint_pass'])+'/'+str(row['runs']),
                  'coordinates',row['coordinates'],'median CNOT',row['median_cnots'])""")
md('## Recomputed now: reload the literal circuit\n\nThis check loads one saved energy-optimized candidate, executes its actual gate list again and verifies its state, normalization and energy. No ED state is loaded into the preparation circuit.')
code("""from annni.upgrade_gates import evolve,h_action,observations
from annni.stage6_candidates import gate_table
point=json.loads((OUT/'domain_wall_candidates/development_101_0_index.json').read_text())[0]
record=point['methods']['C3']['selected']; chosen=record['selected']
gates=gate_table(record['n'],record['basis'],record['ref'],chosen['words'],chosen['params'])
state=evolve(gates,record['n']); saved=np.load(ROOT/record['archive'])['state']
np.testing.assert_allclose(state,saved,atol=1e-10)
assert abs(np.vdot(state,state)-1)<1e-10
energy=float(np.vdot(state,h_action(state,record['n'],record['kappa'],record['h'])).real)
assert abs(energy-chosen['energy'])<1e-8
print({'state_max_difference':float(np.max(abs(state-saved))),
       'norm':float(np.vdot(state,state).real),'recomputed_energy':energy,
       'actual_CNOTs':sum(g[0]=='CNOT' for g in gates)})""")
md('## Independent reference diagnostics\n\nThe N8 PBC curves below are finite-size physical quantities. Multiple wavevectors and Binder/spectral evidence are retained separately. Their response peaks are not automatically thermodynamic critical points. Reference reporting v3/v4 separates physical-interior support from RN multi-size pattern proxies. Frozen D4/D5 training included some v1 pattern-proxy labels; the training-scope audit preserves that limitation rather than calling all training labels independent phase truth.')
code("""curves=read('reference_atlas/curves.json'); fig,axs=plt.subplots(1,3,figsize=(12,3.5))
colors=['#276FBF','#CC6B32','#4C8265']
for key,color in zip(['n8_k0.45','n8_k0.5','n8_k0.8'],colors):
    d=curves[key]; h=np.array(d['h']); values=np.array(d['values'])
    for ax,col,label in zip(axs,[8,10,16],['m0 squared','m(pi/2) squared','Mx']):
        ax.plot(h,values[:,col],label=key,color=color);ax.set(xlabel='h',ylabel=label)
axs[0].legend();fig.tight_layout();plt.show()""")
md('## Noise and finite measurements\n\nAll-shots totals are shared across settings and ZNE scales. Linear and quadratic ZNE reuse the same counts, so they are not independent quantum data. ED finite-shot distributions are ideal information references, not free physical state preparation. Full-state binary trace-distance diagnostics are distinct from deployed phase detection.')
code("""path=OUT/'end_to_end/core_summary.json'
if path.exists():
    summary=json.loads(path.read_text()); keys=[k for k in summary if k.endswith('_100000')]
    for key in keys:
        if '_p0.01_' in key: print(key,'ED MSE',summary[key]['MSE_ED_mean'],'coordinates',summary[key]['physical_coordinates'])
else: print('Core noise comparison not yet completed at this notebook execution.')
path=OUT/'noise_diagnosability/identifiability.json'
if path.exists():
    rows=json.loads(path.read_text()); excess=max(r['xz_joint_total_variation']-r['trace_distance'] for r in rows)
    assert excess<1e-9
    print('Executed pair/method/p rows:',len(rows),'max(TV-DQ):',excess)
else: print('Pair distinguishability analysis not yet executed.')""")
md('## Response reconstruction and circuit-specific noise\n\nThe frozen rule selects an interior peak; a matched coordinate can coexist with a larger endpoint response or a distorted curve. The secondary endpoint audit preserves the original score and reports this limitation. All six requested slices remain in the denominator, although only three noisy windows were executed. Same-coordinate B3/H6 controls test whether the measured difference can reflect circuit noise rather than a change of physical phase.')
code("""path=OUT/'end_to_end/boundary_coordinate_coverage.json'
if path.exists():
    for r in json.loads(path.read_text())['rows']:
        if r['estimator']=='pure_circuit' or (r['p']==.05 and r['budget']==100000 and r['estimator']=='raw'):
            print(r['method'],r['p'],r['estimator'],'requested slices',r['requested_physical_slices'],
                  'reference-resolvable',r['reference_resolvable_physical_slices'],
                  'mean match fraction given reference',r['mean_match_fraction_given_reference'])
path=OUT/'noise_diagnosability/cross_structure_summary.json'
if path.exists():
    for r in json.loads(path.read_text())['summary']: print('Same-coordinate control:',r)
from IPython.display import display,Image
path=OUT/'end_to_end/figures/RN_noisy_response_curves.png'
if path.exists(): display(Image(filename=str(path),width=1000))""")
md('## Complete confirmation and descriptive maps\n\nThese tables read the complete archived cohorts. The96-coordinate confirmation is distinct from the420-point descriptive map and108-point refined grid. State acceptance is not phase-label accuracy. The cached-prefix race and its discarded15-point intermediate analysis are preserved in verification; the canonical confirmation denominator below must be96.')
code("""data=read('end_to_end/confirmation_summary.json')
assert all(row['physical_coordinates']==96 for row in data.values())
for key,row in data.items():
    if key.endswith('_p0.05_100000'):
        correct={d:row['label_repeat_counts'][d]['physical_label'].get('correct',0)/32 for d in ['D1','D3','D4','D5']}
        print(key,'ED-target MSE',row['MSE_ED_mean'],'correct coordinate-equivalents /24',correct)
for task in ['map','low_map']:
    for row in read(f'n8_maps/{task}_selected_preparation_summary.json')['summary']:
        if row['region']=='all':print(task,row)
path=OUT/'end_to_end/figures/confirmation_all_detector_comparison.png'
if path.exists():display(Image(filename=str(path),width=1000))""")
md('## N12 difficult-region noise and translation diagnostics\n\nThese are saved executed data, not new notebook optimizations. The 12 noisy coordinates include six main-cohort points and six local-window points; the registered stride omitted high-field paramagnetic controls. D4/D5 use separately pre-frozen N12 clean-feature calibrations, not zero-shot N8 detector transfer. Mathematical momentum projections below are offline full-state diagnostics and are never substituted for actual circuit outputs or original acceptance.')
code("""path=OUT/'n12_transfer/noise_scope_interpretation.json'
if path.exists():
    data=json.loads(path.read_text())
    for row in data['noise']:
        print(row['method'],row['p'],'12-coordinate ED MSE',row['MSE_ED'])
    print(data['interpretation'])
path=OUT/'failure_mechanisms/translation_sector_diagnostic.json'
if path.exists():
    rows=json.loads(path.read_text())['rows']
    print('Offline translation diagnostics:',len(rows),'cases')
    print('Minimum conditional T0 fidelity:',min(r['conditional_T0_fidelity_diagnostic'] for r in rows))
    assert all(not r['original_joint_pass'] for r in rows)
    assert max(r['observable_weighted_identity_error'] for r in rows)<1e-9
    print('Original state failures unchanged; projected components are not prepared circuits.')
path=OUT/'n12_transfer/figures/n12_all_q_noise.png'
if path.exists(): display(Image(filename=str(path),width=1100))""")
code("""for row in read('n12_transfer/paired_budget_128_192.json')['summary']:
    if row['method'] in ['B3','H6']:
        print('Same-coordinate128/192 comparison:',row)
print('The12-point extension is a subset of36, not an equal-denominator comparison with the entire initial cohort.')""")
md('## OBC floating-region evidence\n\nStopping tolerance, bond dimension, independent initial chains and system size are separate checks. Signed correlations are fitted without dropping oscillation nodes. The K convention follows the transverse-profile Friedel formula, not a renamed ZZ decay exponent. A central charge near one alone does not establish a floating phase. Evidence v2 also retains valid conflicting Friedel exponents at N96, preventing v1 from labelling h=.475 supported solely from N128 fits. A registered single h=.425 chain continuation, if completed, is reported in evidence v3 with the same criteria; registered independent N160 starts, if executed, enter v4. Prior evidence remains archived. The interrupted chi512 run overlaps a recorded host-sleep period and is not a physical exclusion result.')
code("""mps_version=next(v for v in [4,3,2] if (OUT/f'floating_boundary_scan/interval_evidence_v{v}.json').exists())
path=OUT/f'floating_boundary_scan/interval_evidence_v{mps_version}.json'
if path.exists():
    d=json.loads(path.read_text())
    for key in ['supported_samples','lower_transition_bracket','upper_transition_bracket','candidate_floating_samples','scope']: print(key,':',d[key])
else: print('Refined interval evidence not yet complete.')
path=OUT/f'floating_boundary_scan/evidence_map_v{mps_version}.json'
if path.exists():
    rows=json.loads(path.read_text()); status=sorted({r['status'] for r in rows}); fig,ax=plt.subplots(figsize=(12,5))
    for j,name in enumerate(status):
        h=[r['h'] for r in rows if r['status']==name];ax.scatter(h,[j]*len(h),label=name,marker='o')
    import textwrap
    labels=[chr(10).join(textwrap.wrap(x.replace('_',' '),42)) for x in status]
    ax.set(yticks=range(len(status)),yticklabels=labels,xlabel='h at kappa=.8, OBC')
    fig.tight_layout();plt.show()""")
md('## Limits and source records\n\nThe authoritative raw records remain in `results/stage6_v1/`, with source hashes, parameter arrays, literal gates, whole-bitstring counts and MPS checkpoints. Read `report/REPORT.md`, `decision.json` and `EVIDENCE_LEDGER.json` for completed versus unexecuted scope. Grid intervals are not statistical confidence intervals. Repeated shots are not independent physical coordinates. No quantum advantage or complete strong-noise restoration is claimed.')
notebook=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'ANNNI locked Python','language':'python','name':'python3'}});nb.validate(notebook);path=OUT/'report/stage6_research.ipynb';path.parent.mkdir(exist_ok=True);nb.write(notebook,path);print(path)
