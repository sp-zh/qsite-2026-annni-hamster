"""Three-page editable report layout. Uses optional isolated export environment."""
from pathlib import Path
import json,sys,importlib.metadata
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
ROOT=Path(__file__).resolve().parents[1];SUB=ROOT/'submission';F=SUB/'figures';s=json.loads((SUB/'statistics.json').read_text());case=json.loads((ROOT/'results/stage4_v1/branch_audit/regression_cases.json').read_text());c=next(x for x in case if x['case']=='case2' and x['p']==.01)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='Text',fontName='Helvetica',fontSize=9.3,leading=12,spaceAfter=7));styles.add(ParagraphStyle(name='Cap',fontName='Helvetica',fontSize=8,leading=10,spaceAfter=8,textColor=colors.HexColor('#384556')))
styles['Title'].fontSize=19;styles['Title'].leading=22;styles['Heading2'].fontSize=12;styles['Heading2'].leading=15
story=[]
def p(t,sty='Text'):story.append(Paragraph(t,styles[sty]))
def img(name,width,height):story.append(Image(str(F/name),width=width,height=height,kind='proportional'))
def heading(t):p(t,'Heading2')
p('Preparation-Protocol Dependence of<br/>Noisy ANNNI Phase Diagnostics','Title');p('[AUTHOR NAMES] | [TEAM NAME] | Q-SITE 2026 Scientific Track candidate','Cap')
p(f'<b>Abstract.</b> We map continuous diagnostics of an eight-spin periodic ANNNI chain using an energy-optimized circuit and prescribed gate-local depolarization. Bounded repair improves selected preparation coverage from 407 to {s["grid_pass"]}/420. We audit every actual chain-switch interval and refine three windows on nested grids. Nearly identical ideal states can yield substantially different noisy observables at identical gate count. Our results support preparation-protocol dependence, but not a universal nonzero thermodynamic boundary shift.')
heading('1. Model, circuit and controlled noise')
p('H = -sum ZZ<sub>NN</sub> + kappa sum ZZ<sub>NNN</sub> - h sum X; N=8, periodic boundaries. Starting from |+&gt;<super>8</super>, each layer applies NN IsingZZ(2 gamma), NNN IsingZZ(2 eta), then RX(2 beta). IsingZZ(2a)=exp(-ia ZZ). L=6 has 18 parameters and 192 CNOTs (unitary depth 223). Each ZZ block is CNOT-RZ-CNOT; no gates are canceled or removed at zero angle.')
p('After each CNOT, only its target receives D<sub>p</sub>(rho)=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ), with p=0, 0.01, 0.05. The same parameters are used at all p. Full 256 x 256 density matrices, shots=None and no symmetry projection isolate gate noise. ED validates energy-only VQE; it does not supply StatePrep.')
img('grid_main.png',510,290)
p(f'<b>Figure 1.</b> Fixed L6 continuous maps, kappa=0:0.05:1 and h=0.1:0.1:2. Color scales are shared across p within each observable. h=0 is excluded. {s["grid_pass"]}/420 selected noiseless states pass; the separate quality map preserves {420-s["grid_pass"]} failures. These are finite-size diagnostic maps, not a verified four-phase classification.','Cap')
story.append(PageBreak())
heading('2. Calibration and the depth-noise tradeoff')
p('Noiseless acceptance requires energy error/spin &lt;=0.001; maximum errors in C(r), m<sub>q</sub><super>2</super>, Mx &lt;=0.02; squared fidelity &gt;=0.99. Repair used six attempts per failed point, at most 4000 iterations each: two own-point resumes, two neighboring initializations, two new cold starts. Lowest energy selects the winner, including the old solution. The 78 attempts improved four of thirteen failures; nine remain. This is selected multi-path coverage, not a 97.9% independent-start success rate.')
img('depth_noise.png',510,210)
p('<b>Figure 2.</b> Historical matched five-point cohort (verified this stage), L2/4/6 and p=0/.01/.05. Upper panels: maximum SF error to ED. Lower: normalized purity R<sub>mix</sub>. More accurate ideal preparation does not ensure lower noisy total error. At (0,1.8), p=.01 SF errors are .0297/.0527/.0937. CNOT counts are 64/128/192.','Cap')
heading('3. Correct comparison objects, then physical interpretation')
p(f'The earlier audit compared the best opposite-direction candidate, which need not be the branch actually selected after a switch. We instead compare A(h<sub>left</sub>) with B(h<sub>left</sub>), and A(h<sub>right</sub>) with B(h<sub>right</sub>). All {s["switch_intervals"]} actual intervals are checked at three p; {s["old_flags_changed"]} previously checked right-endpoint/p flags change. This is an analysis reliability correction, not a change to density propagation or a claimed physical discovery.')
img('branch_cases.png',510,168)
p(f'<b>Figure 3.</b> Same-parameter archived candidates. Right: kappa=.3, h=.7, L6. Ideal fidelities are {c["candidates"][0]["fidelity"]:.8f} and {c["candidates"][1]["fidelity"]:.8f}. Their Mx difference changes from 0.0000578 at p=0 to {c["comparison_metrics"]["epsilon_mx"]:.5f} at p=.01. All six density matrices are supplied.','Cap')
p('Different angles and intermediate states change how interleaved noise propagates, despite identical resources. We separate O(0)-O<sub>ED</sub> from O(p)-O(0); vector differences add, maximum error norms generally do not. Accidental cancellation is not mitigation. No intrinsic ranking of phase fragility follows from this case alone.')
story.append(PageBreak())
heading('4. Fixed-branch nested-grid refinement')
p('Windows were frozen from N8 noiseless evidence: kappa=0, h=[.75,1.25]; kappa=.3, h=[.25,.65]; kappa=.8, h=[.35,.85]. Two independently sourced endpoint chains are continued without pointwise winner splicing. Three originally requested endpoints failed calibration, so passing same-direction archived sources were explicitly frozen before any local simulation. Windows and thresholds were unchanged.')
p(f'The finest spacing is .0125. Spacings .025 and .05 are nested subsamples of those same preparations, not independent repeats. All p are simulated at every fine point: {s["local_optimizations"]} optimizations, {s["local_noise_configs"]} configurations; {s["local_prep_pass"]} preparations pass.')
img('local_curves.png',510,245)
p('<b>Figure 4.</b> Raw order-feature (top) and transverse-magnetization (bottom) curves. Colors denote p and line styles distinguish the two fixed-source chains. Vertical scales remain comparable even when the p=.05 signal is small. The full-q supplement retains all eight discrete wavevectors and the 1/N self term.','Cap')
p(f'We require raw signal range &gt;=.02 and derivative prominence &gt;=.02, retain all local/endpoint peaks and mask failed preparation or possible optimizer-jump supports. Every derivative, prominence and coarse-grid support is traceable. There are {s["local_resolved_shift_pairs"]} resolved branch-feature/noise pairings, but no pair has corroborated nonzero displacement supported by both order and Mx diagnostics. Individual-feature shifts depend on the preparation branch; we do not average them into a unique boundary. Unresolved results stay missing, not zero. Grid/protocol ranges are not confidence intervals.')
heading('5. Scope, contribution and submission limitations')
p('This project adds a controlled computational comparison and a reproducible preparation-protocol audit. ED, VQE and the Pauli depolarizing model are established methods. N=8 finite-size diagnostics, remaining preparation failures, branch effects and the fixed circuit limit interpretation. No floating phase, universal critical field or quantum advantage is established. Failure under our fixed thresholds does not prove that all possible measurements lose information. The prototype classifier uses only [m0 squared, 2m(pi/2) squared, Mx].')
p('The supplied notebook directly displays the grid and reruns one ideal/noisy check from a new kernel. The evidence table, official-requirements checklist, all failed attempts and raw fine-grid parameters are included. Author/team details, final editorial review and timed 5-7 minute rehearsal remain for the team.')
heading('References and reproduction')
p('[1] Q-SITE 2026 Quantum Coalition Scientific Track handout, snapshot 57f9a537d24c69328dedf915ad58d1d2bf505135; README and PROVENANCE supplied.<br/>[2] PennyLane, ANNNI Phase Detection: pennylane.ai/qml/demos/tutorial_annni.<br/>[3] PennyLane, A Noisy Heisenberg Model: pennylane.ai/challenges/heisenberg_model.<br/>Run: <font face="Courier">bash scripts/reproduce_submission.sh</font>. Full calculations require explicit <font face="Courier">--compute</font>.','Cap')
def footer(canvas,doc):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526174'));canvas.drawString(42,24,'ANNNI | Submission candidate | deterministic simulation');canvas.drawRightString(570,24,str(doc.page))
SimpleDocTemplate(str(SUB/'report.pdf'),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=37).build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
reader=PdfReader(SUB/'report.pdf');assert len(reader.pages)==3,len(reader.pages)
(SUB/'export_environment.json').write_text(json.dumps({'python':sys.version,'reportlab':importlib.metadata.version('reportlab'),'pypdf':importlib.metadata.version('pypdf'),'pages':len(reader.pages),'science_environment_changed':False},indent=2))
print('Rendered 3-page report.pdf')
