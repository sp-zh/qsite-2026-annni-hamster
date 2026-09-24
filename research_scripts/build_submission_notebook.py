import os,json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUB=ROOT/'submission'
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'));os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/annni-submission-kernel');os.environ.setdefault('IPYTHONDIR','/tmp/annni-submission-ipython')
import nbformat
from nbclient import NotebookClient
stats=json.loads((SUB/'statistics.json').read_text());nb=nbformat.v4.new_notebook();md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
nb.cells=[md(f'''# Preparation-Protocol Dependence of Noisy ANNNI Phase Diagnostics
Authors: [AUTHOR NAMES] · Team: [TEAM NAME]

## tl;dr
A fixed L6, N8 positive-field grid has **{stats['grid_pass']}/420** calibrated selected preparations. We corrected the comparison objects for all **{stats['switch_intervals']}** actual switching intervals, repaired 13 failed grid points with 78 bounded attempts, and ran **{stats['local_noise_configs']}** local noise configurations. No complementary-indicator evidence establishes a nonzero boundary displacement robust to preparation protocol.

## Context & Methods
The challenge asks for clean and noisy ANNNI maps and a quantitative noise analysis. This submission presents continuous finite-size diagnostics with explicit quality masks, not a validated four-phase classifier.

H = -Σ ZZ_NN + κΣ ZZ_NNN - hΣX, periodic N=8. Initial |+〉^8; each layer NN ZZ(2γ), NNN ZZ(2η), RX(2β). L6 has 192 CNOTs with unchanged CNOT-RZ-CNOT compilation. Each CNOT is followed by the prescribed target-only D_p, p=0/.01/.05. Full 256×256 density matrices, shots=None.

### Key Assumptions
ED validates energy-only VQE; it is not StatePrep. No output symmetry projection, zero-angle gate removal or noisy reoptimization. Structure factors include 1/N self correlation. The prototype classifier uses **three features** [m0²,2m(π/2)²,Mx], although all eight q values are archived. Noisy grid excludes h=0.

## Data — verified archived computations
The next cells read existing results; they do not rerun full scans.'''),code('''from pathlib import Path
import sys,json,numpy as np
from IPython.display import display,Markdown,Image
ROOT=Path.cwd()
if ROOT.name=='submission': ROOT=ROOT.parent
sys.path.insert(0,str(ROOT))
SUB=ROOT/'submission';OUT=ROOT/'results/stage4_v1'
stats=json.loads((SUB/'statistics.json').read_text())
print('Archived grid:',stats['grid_pass'],'/420 preparations pass')
print('Archived local:',stats['local_optimizations'],'states;',stats['local_noise_configs'],'noise configurations')
print('This cell reads archives; fresh computation is explicitly marked below.')'''),md('''## Results — ED validation and VQE calibration
Acceptance: δe≤.001, εC/εSF/εMx≤.02, squared fidelity≥.99. Energy-only candidate selection is preserved. The full baseline and earlier calibration are supplied; below, the Stage4 repair table explicitly retains all failure modes.'''),code('''repairs=json.loads((OUT/'grid_v2/replacement_map.json').read_text())
t='|κ|h|old pass|new pass|new failed metrics|other candidate passed|\\n|---|---|---|---|---|---|\\n'
for r in repairs:t+=f"|{r['kappa']}|{r['h']}|{r['old']['joint_pass']}|{r['new']['joint_pass']}|{r['failed_metrics']}|{r['other_candidate_pass']}|\\n"
display(Markdown(t))'''),md('### Fixed-depth positive-field maps and quality'),code("display(Image(filename=str(SUB/'figures/grid_main.png'),width=1100))\ndisplay(Image(filename=str(SUB/'figures/grid_quality.png'),width=650))"),md('''All three noise strengths are shown directly with shared physical scales. These are observable maps, not exact thermodynamic phase boundaries. Unchanged points reuse validated Stage3 physics; changed parameters replace all three p outputs together.'''),md('### Same-point depth-noise tradeoff — historical matched cohort'),code("display(Image(filename=str(SUB/'figures/depth_noise.png'),width=1100))"),md('''This verified Stage3 cohort uses the same cold-start seeds and budget for each depth. Improved ideal precision need not reduce noisy total error; effective noise also depends on angles and intermediate states.'''),md('### Actual switches versus opposite-direction comparisons'),code('''pairs=json.loads((OUT/'branch_audit/comparisons.json').read_text())
print('Actual intervals:',len(pairs)//3,'; interval-p comparisons:',len(pairs))
print('Changed old sensitivity flags:',stats['old_flags_changed'])
case=json.loads((OUT/'branch_audit/regression_cases.json').read_text())
for r in case:print(r['case'],'p=',r['p'],'same-h Mx difference=',round(r['comparison_metrics']['epsilon_mx'],8))
display(Image(filename=str(SUB/'figures/branch_cases.png'),width=950))'''),md('''The comparison is A and B at the same h, separately at both interval endpoints. Unknown is not insensitive; no switch is not_applicable. The correction concerns comparison identity and full stencil support, not a claimed new numerical noise model. Case2 provides all parameters and density matrices for two high-fidelity ideal preparations with identical CNOT counts.'''),md('### Fixed-branch local refinement'),code("display(Image(filename=str(SUB/'figures/local_curves.png'),width=1100))\ndisplay(Image(filename=str(SUB/'figures/local_branch_difference.png'),width=1100))\ndisplay(Image(filename=str(SUB/'figures/local_all_q.png'),width=950))"),code('''shifts=json.loads((OUT/'local_refinement/shifts.json').read_text())
resolved=[r for r in shifts if r['delta_h'] is not None]
t='|branch|feature|p|Δh_app|grid support|complementary agreement|\\n|---|---|---|---|---|---|\\n'
for r in resolved:t+=f"|{r['chain']}|{r['feature']}|{r['p']}|{r['delta_h']:.4f}|[{r['range_low']:.4f}, {r['range_high']:.4f}]|{r['complementary_agreement']}|\\n"
display(Markdown(t))
print('Unresolved branch/feature/p combinations:',sum(r['delta_h'] is None for r in shifts))'''),md('''Nested .05/.025/.0125 grids use the same preparations; they are not independent repetitions. Each branch is analyzed separately. The full peak list includes endpoint, prominence, width, amplitude, grid position differences and complete computation supports. Coarse-grid association tolerance is not a fine-resolution accuracy certificate. Unresolved shifts are missing, not zero.'''),md('## Fresh computation — ideal state and noisy comparison in this kernel'),code('''from annni.stage4 import dense_literal
from annni.circuits import HVAEngine,observe
from annni.noise import noisy_density,density_checks
r=next(r for r in case if r['case']=='case2' and r['p']==.01)
fresh=[]
for candidate in r['candidates']:
    theta=np.load(ROOT/candidate['archive'])['final_params']
    psi=HVAEngine().state(theta)
    rho0=dense_literal(theta,0)
    np.testing.assert_allclose(rho0,np.outer(psi,psi.conj()),atol=1e-10)
    rho=dense_literal(theta,.01);density_checks(rho)
    fresh.append(observe(rho)['mx'])
qml_rho=noisy_density(theta,.01)
np.testing.assert_allclose(rho,qml_rho,atol=2e-11)
np.testing.assert_allclose(abs(fresh[1]-fresh[0]),r['comparison_metrics']['epsilon_mx'],atol=1e-11)
print('FRESH same-h Mx difference at p=.01:',abs(fresh[1]-fresh[0]))
print('FRESH ideal/p0 and PennyLane full-density checks passed.')'''),md('''## Takeaways
The matched calculations support preparation-protocol dependence at fixed gate count. Bounded repair improves coverage but does not remove every failure. The local data do not support a common nonzero displacement corroborated by both diagnostics. No floating phase, universal critical field or quantum advantage is established.

Methods such as ED, VQE and Pauli depolarization are established. Our contribution is the controlled experiment and its traceable limitations. Author/team placeholders and a timed 5–7 minute rehearsal remain.

## Reproduction and references
Run `bash scripts/reproduce_submission.sh` from the project root. Full continuation requires explicit `--compute`; opening this notebook does not rerun the entire campaign.

See `requirements_checklist.csv`, `evidence_table.csv`, `REPRODUCE.md`, and `report.md`. The supplied Scientific Track handout and PROVENANCE identify upstream commit 57f9a537d24c69328dedf915ad58d1d2bf505135. PennyLane's ANNNI Phase Detection and Noisy Heisenberg resources are linked there as background, not used to generate labels.''')]
nb.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
NotebookClient(nb,timeout=180,resources={'metadata':{'path':str(ROOT)}}).execute();nbformat.validate(nb);nbformat.write(nb,SUB/'submission.ipynb')
parts=['<!doctype html><meta charset="utf-8"><title>ANNNI submission notebook</title><style>body{max-width:1150px;margin:35px auto;font:16px/1.6 system-ui}pre{white-space:pre-wrap;background:#f4f6f8;padding:16px}img{max-width:100%}</style>']
for c in nb.cells:
 if c.cell_type=='markdown':parts.append('<pre>'+html.escape(c.source)+'</pre>')
 else:
  parts.append('<details><summary>Executed cell '+str(c.execution_count)+'</summary><pre>'+html.escape(c.source)+'</pre></details>')
  for o in c.get('outputs',[]):
   if o.output_type=='stream':parts.append('<pre>'+html.escape(o.text)+'</pre>')
   elif 'image/png' in o.get('data',{}):parts.append('<img alt="Executed figure" src="data:image/png;base64,'+o.data['image/png']+'">')
   elif 'text/markdown' in o.get('data',{}):parts.append('<pre>'+html.escape(o.data['text/markdown'])+'</pre>')
(SUB/'notebook_preview.html').write_text('\n'.join(parts))
print('submission.ipynb executed in fresh kernel:',len([c for c in nb.cells if c.cell_type=='code']),'code cells')
