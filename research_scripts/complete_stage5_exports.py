"""Record completed export gates; archive verification is a separate final step."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';S=O/'submission'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
pdf=read(S/'pdf_visual_qa.json');slides=read(S/'presentation_visual_qa.json');notebook=read(S/'notebook_execution.json')
assert pdf['status']=='PASS' and pdf['sha256']==sha(S/'report.pdf')
assert slides['schema']=='PASS' and slides['officecli_layout_issues']==0
assert notebook['errors']==0
assert '80 passed' in (O/'verification/final_queue_2.log').read_text()
status=dict(status='EXPORTS_COMPLETE_WITH_PRESENTATION_VISUAL_LIMIT',timestamp=datetime.now(timezone.utc).isoformat(),files={name:sha(S/name) for name in ['report.pdf','presentation.pptx','submission.ipynb']},pdf_pages=3,pdf_visual_check='PASS',pptx_slides=8,pptx_visual_check=slides['visual_status'],pptx_schema='PASS',notebook_errors=0,archive_verification='Performed separately by scripts/package_stage5.py after immutable archive creation; see the delivered ZIP_VERIFICATION_STAGE5.json')
(S/'export_status.json').write_text(json.dumps(status,indent=2))
decision=read(O/'decision.json');decision['submission_readiness']=dict(status='READY_WITH_PRESENTATION_VISUAL_LIMIT',evidence='submission/export_status.json',limitation='Editable8-slide PPTX passes schema, text and HTML checks; actual slide playback was not visually verified because renderer unavailable, local-file browser preview blocked and native UI unavailable while the Mac was locked. PDF3pages visually checked; notebook executed.',archive_integrity='The final ZIP has its own external SHA256 and fresh-extraction verification record; no circular self-hash is embedded in this decision.')
(O/'decision.json').write_text(json.dumps(decision,indent=2))
print(status['status'])
