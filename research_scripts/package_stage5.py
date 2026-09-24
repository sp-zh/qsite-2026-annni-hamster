"""Self-contained actual code/data ZIP and fresh extraction checks."""
import json,hashlib,zipfile,time,subprocess,os,tempfile,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];O=R/'results/stage5_v1';D=R/'deliverables';D.mkdir(exist_ok=True);archive=D/'annni_stage5_v1.zip';started=time.perf_counter()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
files=[];excluded=[]
for directory in ['annni','configs','scripts','tests','upstream','results','submission']:
 for p in (R/directory).rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(R)
  if '__pycache__' in rel.parts or p.suffix in ['.pyc','.tmp'] or p.name=='.DS_Store':continue
  if 'sources' in rel.parts and p.suffix in ['.pdf','.txt','.html']:
   excluded.append(str(rel));continue
  files.append(p)
for name in ['README.md','requirements.lock.txt','requirements-tn.lock.txt','pyproject.toml','baseline.ipynb','calibration.ipynb','stage3.ipynb','REPRODUCE_STAGE3.md']:
 if (R/name).exists():files.append(R/name)
entries={str(p.relative_to(R)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(files))};manifest=dict(files=entries,excluded_downloaded_sources=excluded,format='Actual code/data, relative paths; no environments, credentials, fonts, Git internals or downloaded full-text papers');mf=D/'PACKAGE_MANIFEST_STAGE5.json';mf.write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for name in entries:z.write(R/name,name)
 z.writestr('PACKAGE_MANIFEST_STAGE5.json',mf.read_text())
extract=Path(tempfile.mkdtemp(prefix='annni_stage5_extract_'))
with zipfile.ZipFile(archive) as z:
 for i in z.infolist():assert not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts
 z.extractall(extract)
for name,r in entries.items():assert sha(extract/name)==r['sha256'],name
log=D/'EXTRACTED_STAGE5_VERIFY.log';env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(R/'.mplconfig'),PYTHONPATH=str(extract));python=R/'.venv/bin/python'
with log.open('w') as f:
 for command in [[str(python),'-m','pytest','-q'],[str(python),'scripts/verify_stage5.py'],[str(python),'scripts/verify_stage5_sampling.py']]:
  p=subprocess.run(command,cwd=extract,env=env,stdout=f,stderr=subprocess.STDOUT);assert p.returncode==0,log
references=0
for p in (extract/'results/stage5_v1').rglob('*.json'):
 def visit(a):
  global references
  if isinstance(a,dict):
   for k,v in a.items():
    if isinstance(v,str) and (k in ['archive','checkpoint','source','run_record'] or k.endswith('_archive')) and v.startswith('results/') and not any(x in v for x in ['historical_reused ', 'newly_executed ']):
     assert (extract/v).exists(),(p,k,v);references+=1
    else:visit(v)
  elif isinstance(a,list):
   for v in a:visit(v)
 visit(json.loads(p.read_text()))
markdown_references=0
for doc in [extract/'README.md',extract/'results/stage5_v1/EVIDENCE_LEDGER.md',extract/'results/stage5_v1/REPORT.md',extract/'results/stage5_v1/submission/failure_cases.md']:
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text()):
  if re.match(r'[a-zA-Z]+:',target) or target.startswith('#'):continue
  resolved=doc.parent/target.split('#')[0]
  assert resolved.exists(),('Missing Markdown reference',str(doc.relative_to(extract)),target)
  markdown_references+=1
result=dict(passed=True,completed_utc=datetime.now(timezone.utc).isoformat(),run_wall_elapsed_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(json.loads((O/'experiment_plan.json').read_text())['started_utc'])).total_seconds(),archive=str(archive.relative_to(R)),sha256=sha(archive),bytes=archive.stat().st_size,files_hashed=len(entries),references_checked=references,markdown_references_checked=markdown_references,extracted_tests=True,extracted_verify=True,extraction_directory=str(extract),seconds=time.perf_counter()-started);(D/'ZIP_VERIFICATION_STAGE5.json').write_text(json.dumps(result,indent=2));(D/'annni_stage5_v1.zip.sha256').write_text(result['sha256']+'  annni_stage5_v1.zip\n');print(json.dumps(result,indent=2))
