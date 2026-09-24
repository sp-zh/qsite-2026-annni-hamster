"""Three-page research summary, using saved measurements rather than invented runs.

Run with the bundled document Python (ReportLab); numerical environments unchanged.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/stage6_v1'
DEST=OUT/'report/STAGE6_RESEARCH_SUMMARY.pdf'
read=lambda p:json.loads((OUT/p).read_text())
plan=read('experiment_plan.json')
decision=read('decision.json')
navy=HexColor('#183B50');teal=HexColor('#247C83');grey=HexColor('#52636D')
style=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor=navy)
small=ParagraphStyle('small',parent=style,fontSize=8.3,leading=11)
c=canvas.Canvas(str(DEST),pagesize=(612,792))
c.setTitle('ANNNI Stage 6: low-field preparation and phase-diagnostic limits')
c.setAuthor('ANNNI Scientific Track research project')
y=0
def page(number,subtitle):
    global y
    c.setFillColor(navy);c.rect(0,742,612,50,fill=1,stroke=0)
    c.setFillColor(white);c.setFont('Helvetica-Bold',13)
    c.drawString(42,766,'ANNNI  /  STAGE 6 RESEARCH SUMMARY')
    c.setFont('Helvetica',9);c.drawString(42,750,subtitle)
    c.setFillColor(grey);c.setFont('Helvetica',7.5)
    c.drawString(42,26,plan['run_id']+'  |  PBC circuits; OBC MPS reported separately')
    c.drawRightString(570,26,f'{number} / 3')
    y=718
def paragraph(text,kind=style,gap=9):
    global y
    p=Paragraph(text,kind);w,h=p.wrap(528,y-43)
    assert y-h>=43,('Page content exceeds available space',text[:60],y,h)
    p.drawOn(c,42,y-h);y-=h+gap
def heading(text):
    global y
    y-=4;c.setFillColor(teal);c.setFont('Helvetica-Bold',12)
    c.drawString(42,y,text);y-=20
def table(headers,rows,widths):
    global y
    data=[[Paragraph(escape(str(x)),small) for x in r] for r in [headers,*rows]]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#E4EFF1')),
                          ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,teal),
                          ('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
    _,h=t.wrap(528,y-43);assert y-h>=43;t.drawOn(c,42,y-h);y-=h+12
def summary(task):
    folder='n12_transfer' if task.startswith('n12') else 'confirmation'
    p=OUT/f'{folder}/{task}_paired_summary.json'
    return json.loads(p.read_text())['summary'] if p.exists() else []
def select(task,method,region):
    return next((r for r in summary(task) if r['method']==method and r['region']==region),None)

page(1,'Candidate generation: a real N8 gain, with explicit cost and transfer limits')
paragraph('<b>Finding.</b> A reversible domain-wall variational construction improves low-field N8 candidate availability on new confirmation coordinates. It does not establish a universal replacement for B3: validation, noise resilience and N12 transfer give different rankings.')
heading('Model, method and independent evaluation')
paragraph('We simulate H = -sum ZZ + kappa sum Z_i Z_(i+2) - h sum X, with periodic boundaries for N8/N12. The wall register keeps the global spin bit and periodic parity constraint; all preparation and decoding CNOTs are charged. Energy-only optimization uses the full Hamiltonian. H6 is a frozen regional union of physical and wall candidates, not the historical six-layer HVA.')
paragraph('Development, validation and 96 new confirmation coordinates are separate. The low-field confirmation subset contains 48 coordinates. State acceptance retains F >= .99, energy error <= .001/site and each observable error <= .02. Qualified-candidate existence and the deployed energy/resource selection are reported separately.')
table(['N8 low-field confirmation','B3','H6'],[
    ['Qualified candidate exists','27 / 48','45 / 48'],['Selected joint pass','27 / 48','37 / 48'],
    ['Selected observable pass','28 / 48','45 / 48'],['Median executed CNOTs','32','127'],
    ['Energy objective calls','678,228','5,050,938']], [292,118,118])
paragraph('H6 gains 18 and loses 8 passing coordinates relative to B3. At saved 64/96/128-CNOT checkpoints, H6 joint passes are 15/18/37 versus B3 26/26/27. This is not a same-executed-cost breakthrough. Eight H6 failures have a qualified saved candidate but the frozen rule selects an observable-accurate, near-half-fidelity branch.')
heading('Stability and N12 transfer')
paragraph('Validation joint acceptance is H6 20/24 versus B3 22/24. Across 12 coordinates and three independent seeds, both methods pass at least two seeds on 10/12 coordinates; all-three success is H6 9/12 versus B3 10/12. Improved initialization stability is not established.')
rows=[]
for task in ['n12','n12_192']:
    a,b=select(task,'B3','all'),select(task,'H6','all')
    if a and b:rows.append([task.replace('n12_192','N12, 192 cap').replace('n12','N12, 128 cap'),str(a['joint_pass'])+'/'+str(a['coordinates']),str(b['joint_pass'])+'/'+str(b['coordinates'])])
table(['N12 fixed-cohort comparison','B3 joint','H6 joint'],rows,[292,118,118])
paragraph('The128 cap covers36points; the192 cap covers a registered12-point subset. On those same12points, B3 rises10 to11 passes and H6 rises8 to10; gains are in the antiphase band, not low field. The separate kappa=.55 window has H6 joint0/16 versus B3 7/16, yet both retain seven observable passes and shift the RN response peak +.0125. No N12 low-field advantage is established.',small)
c.showPage()

page(2,'Reference, response reconstruction and the source of strong-noise failures')
heading('Independent physical scope is narrower than the state grid')
paragraph('R0/qualified interior evidence, same-size ED finite-size features (RN), and larger OBC evidence (Rlarge) are separate. Only 24/96 confirmation coordinates have independently supported physical-interior labels, including 4/48 low-field points. The 64/96 RN pattern proxies are not independent phase truth. No literature curve paints a full truth map.')
paragraph('The principal ED order-response feature is resolvable on 14/15 N8 slices and 5/6 at each of N12/N16. On six fine circuit windows, ED resolves five: p0 B3 matches 4/5 and H6 5/5, with worst matched displacement .0125. These are finite-size feature coordinates, not precise thermodynamic phase boundaries.')
paragraph('<b>Failure exposed by full curves:</b> all 17 B3 kappa=0 window states pass preparation tests, but competing derivative peaks prevent a unique frozen-rule match. Under p=.05, 64 raw B3 repeated matches in two low-field windows coexist with a stronger endpoint response. A close interior peak alone is not reliable boundary recovery.')
heading('Same-budget noise and mitigation')
paragraph('After every literal CNOT, only its target receives D_p(rho)=(1-p)rho+(p/3)(XrhoX+YrhoY+ZrhoZ). Tests use p=0,.01,.05, fixed p0 parameters, complete bitstrings and 32 repeats at total 10k/100k shots. ZNE folds each CNOT 1/3/5 times; signed SV uses (O+OP)/(1+P). All settings share the stated total budget.')
table(['48-coordinate core, p=.05, 100k','B3','H6'],[
    ['Mean ED-target MSE, raw','.070341','.138866'],['Mean ED-target MSE, quadratic ZNE','.039536','.109008'],
    ['D4 correct / physically labelled, raw','2 / 13','0 / 13'],['D4 correct / physically labelled, ZNE','11 / 13','0 / 13']], [292,118,118])
paragraph('Quadratic ZNE was selected on validation and costs about three times the raw CNOT-shots at equal shots. The other35 core coordinates lack independent labels. Old D3 raw already gives10/13 correct for B3; new D4/D5 do not show a general advantage over that simpler baseline. Sampling-about-exact MSE is about 1.4-1.6e-6, far below exact bias MSE: more shots alone cannot remove the dominant error.')
paragraph('The complete108-point low-field grid shows the same tradeoff: area-weighted raw MSE improves from .00185 to .00075 at p0, but worsens from .08265 to .11963 at p=.05 (B3 to H6). These are observable errors, not phase-label accuracy.',small)
heading('Retained information does not imply correct phase detection')
paragraph('Four same-H saved-growth controls directly expose circuit artifacts. At (.45,.0875), 31 versus 63 CNOTs changes m0 squared by -.00150 at p0 but -.23196 at p=.05. Parameters and structure both change; this is not an isolated one-gate causal effect. These controls were exploratory, after inspecting the curves.')
paragraph('Fourteen fixed binary pairs satisfy classical X/Z distance <= quantum trace distance. Known-template 100k/1M queries show no observed errors in 64 trials per pair/method/p, but are oracle binary tests, not a phase classifier. Twelve pairs straddle RN features without independently established opposite phase labels. Same-coordinate cross-structure controls also reveal noise fingerprints.',small)
c.showPage()

page(3,'Large-size evidence, completion scope and reproducibility')
heading('A controlled kappa=.8 OBC slice, with unresolved intervals')
paragraph('The scan spans h=.10-.80: N64 coarse data; N96/N128 independent initial chains and chi128/256 controls; targeted N160/N192; and a retained failed chi512 continuation. Signed central-pair correlations, ordered-platform/power/exponential fits, free OBC central-charge fits and mapped Friedel-profile K are compared. No single c, q or fit score establishes a floating phase.')
mps_version=next(v for v in [4,3,2] if (OUT/f'floating_boundary_scan/interval_evidence_v{v}.json').exists())
floating=read(f'floating_boundary_scan/interval_evidence_v{mps_version}.json')
table(['Evidence category','Executed support / limitation'],[
    ['Supported antiphase samples',str(floating['supported_samples']['supported_antiphase_sample'])],['Supported paramagnetic-side samples',str(floating['supported_samples']['supported_paramagnetic_side_sample'])],
    ['Supported floating samples',str(floating['supported_samples']['supported_floating_sample'])],['Candidate floating samples',str(floating['candidate_floating_samples'])],
    ['Controlled continuous floating interval','Not established'],['Two transition brackets',str(floating['lower_transition_bracket'])+' / '+str(floating['upper_transition_bracket'])]], [225,303])
paragraph('At h=.4, N128 Friedel K about .36 conflicts with N160 values about .54/.56; h=.475 also has size conflicts. Historical (.8,.5) and (1,.7) center interpretations need crossover qualification, not a claim of a gap. At h=.425 the N128 continuation and both N160 starts now pass stopping, but the N160 Friedel fits hit their upper bound and free c fits vary about1.29-1.35. These invalid profile fits are not physical K measurements. No controlled continuous floating interval is established; all earlier failures remain archived.')
paragraph('The h=.35 chi512 hard timeout overlaps a recorded host-sleep interval; it is a computational outcome, not evidence excluding a floating phase. Solver stopping, chi agreement, initial-chain agreement and size trends remain distinct. OBC evidence is not copied into N8 PBC labels.')
heading('Executed scope and scientific decision')
rows=[]
for key in ['candidate_confirmation','noise_core','noise_windows','noise_low_map','noise_map','noise_n12']:
    r=decision['execution_counts'][key];rows.append([key.replace('_',' '),str(r['actual'])+' / '+str(r['requested'])])
table(['Saved coordinate groups (not independent solver calls)','Actual / requested'],rows,[390,138])
paragraph('Retain B3 and H6 as measured accuracy/resource tradeoffs. The N8 low-field gain is real; strong-noise response recovery, N12 difficult-region advantage and a controlled continuous floating interval remain unresolved. Quality masks report these failures and do not solve them.',small)
paragraph('Combine the code/data archives with the protected Stage5 base as specified in REPRODUCE_STAGE6.md. Run: <font name="Courier">ANNNI_PYTHON=/path/to/locked/python bash scripts/reproduce_stage6.sh --verify</font>. The full report, executed notebook, EVIDENCE_LEDGER, decision.json and raw archives distinguish historical reuse, new execution and missing work.',small)
paragraph('Primary sources: qubit-ADAPT, arXiv:1911.10205; ANNNI tensor-network study, arXiv:2402.11022; floating-phase DMRG, cond-mat/0702676; symmetry verification, arXiv:1807.10050. XX/Z conventions are mapped by a global Hadamard to this ZZ/X model. Actual cached-text access and installed-library checks are recorded in sources/.',small)
c.save()
print(DEST)
