"""Run in separate reportlab environment; does not touch scientific dependencies."""
import json,re
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1];S=R/'results/stage4_upgrade_v1/submission';stats=json.loads((S/'statistics.json').read_text());text=(S/'report.md').read_text();sections={};title=''
for part in text.split('\n## '):
 if part.startswith('# '):title=part.splitlines()[0][2:]
 else:
  key,body=part.split('\n',1);sections[key]=body.strip()
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='TitleSmall',fontName='Helvetica-Bold',fontSize=18,leading=22,spaceAfter=10));styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9.5,leading=12.5,spaceAfter=7));styles.add(ParagraphStyle(name='HeadingSmall',fontName='Helvetica-Bold',fontSize=11,leading=14,spaceBefore=6,spaceAfter=5));styles.add(ParagraphStyle(name='CaptionSmall',fontName='Helvetica',fontSize=8,leading=10,spaceAfter=6));story=[]
def p(s,sty='BodySmall'):story.append(Paragraph(s.replace('&','&amp;'),styles[sty]))
def section(name):p(name,'HeadingSmall');p(sections[name])
def image(name,w,h):
 path=S/'figures'/name;im=ImageReader(str(path));iw,ih=im.getSize();scale=min(w/iw,h/ih);story.append(Image(str(path),width=iw*scale,height=ih*scale))
def footer(canvas,doc):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.grey);canvas.drawString(40,24,'ANNNI Scientific Track | reproducible numerical study | September 2026');canvas.drawRightString(572,24,str(doc.page))
p(title,'TitleSmall');p('N=8/12 periodic circuits; large-N open-chain MPS evidence','CaptionSmall');section('Abstract');section('Model and controlled comparison');section('Results and interpretation');image('pareto_noise.png',520,210);p('Matched grid includes failed preparations. Reduced inference gates incur adaptive search overhead; full-domain and jointly qualified statistics are separate.','CaptionSmall');story.append(PageBreak())
p('Phase-feature maps and quality masks','TitleSmall');image('matched_phase_maps.png',520,530);p('Same full-observable diagnostic and color mapping at every p. Rows: historical HVA B0, adaptive B3, noise-aware equivalent compilation B4. Red crosses mark failed noiseless preparation. White lines show the N8 ED response maximum; black dashed/dotted lines are approximate external literature references, not fitted labels or exact phase boundaries. Degraded and uncertain are diagnostic outcomes.','CaptionSmall');section('Detection, mitigation and scale');story.append(PageBreak())
p('Mitigation, scaling and independent dynamics','TitleSmall');image('mitigation_equal_shots.png',520,205);section('Error mitigation and dynamics');image('floating_convergence.png',520,185);p('Open-boundary entropy and oscillation fits across N and bond dimension. A fitted c near one alone is insufficient to establish a floating phase; raw/connected correlation fits, controls and truncation checks are retained in the appendix.','CaptionSmall');section('Limitations and conclusion');p('References','HeadingSmall');p(sections['References'],'CaptionSmall')
SimpleDocTemplate(str(S/'report.pdf'),pagesize=(612,792),leftMargin=40,rightMargin=40,topMargin=32,bottomMargin=38).build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader
n=len(PdfReader(S/'report.pdf').pages);assert n==3,f'Expected 3 pages, got {n}'
print('Rendered',n,'pages')
