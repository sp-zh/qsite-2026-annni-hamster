"""Package real data with relative paths; fresh safe extraction and hash/entry verification."""
import json,hashlib,zipfile,time,subprocess,os,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'results/stage4_upgrade_v1';D=R/'deliverables';D.mkdir(exist_ok=True);archive=D/'annni_stage4_upgrade_v1.zip';manifest=D/'PACKAGE_MANIFEST_UPGRADE.json';started=time.perf_counter()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[];excluded=[]
for directory in ['annni','configs','scripts','tests','upstream','results','submission']:
 for p in (R/directory).rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(R)
  if '__pycache__' in rel.parts or p.suffix=='.pyc' or p.name=='.DS_Store':continue
  if 'stage4_upgrade_v1' in rel.parts and 'sources' in rel.parts and p.name not in ['references.json','fulltext_access.json','METHOD_NOTES.md']:
   excluded.append(str(rel));continue
  files.append(p)
for name in ['README.md','requirements.lock.txt','requirements-tn.lock.txt','pyproject.toml','baseline.ipynb','calibration.ipynb','stage3.ipynb','REPRODUCE_STAGE3.md']:
 if (R/name).exists():files.append(R/name)
entries={str(p.relative_to(R)):dict(sha256=sha(p),bytes=p.stat().st_size,category='new_campaign' if 'stage4_upgrade_v1' in p.parts or 'upgrade' in p.name else 'historical_or_shared_source') for p in sorted(set(files))}
meta=dict(created_utc=time.time(),files=entries,excluded_downloaded_copyright_sources=excluded,format='relative directory ZIP with actual data, no environments, credentials, fonts or Git internals');manifest.write_text(json.dumps(meta,indent=2))
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for name in entries:z.write(R/name,name)
 z.writestr('PACKAGE_MANIFEST_UPGRADE.json',manifest.read_text())
extract=Path(tempfile.mkdtemp(prefix='annni_upgrade_extract_'))
with zipfile.ZipFile(archive) as z:
 for info in z.infolist():
  rel=Path(info.filename);assert not rel.is_absolute() and '..' not in rel.parts
 z.extractall(extract)
for name,entry in entries.items():assert sha(extract/name)==entry['sha256'],name
# Environment is deliberately outside the archive; use same locked interpreter on extracted source.
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MPLCONFIGDIR=str(R/'.mplconfig'),PYTHONPATH=str(extract));python=R/'.venv/bin/python'
log=D/'EXTRACTED_UPGRADE_VERIFY.log'
with open(log,'w') as f:
 test=subprocess.run([str(python),'-m','pytest','-q'],cwd=extract,env=env,stdout=f,stderr=subprocess.STDOUT)
 if test.returncode:raise RuntimeError('Extracted tests failed; see '+str(log))
 verify=subprocess.run([str(python),'scripts/verify_upgrade.py'],cwd=extract,env=env,stdout=f,stderr=subprocess.STDOUT)
 if verify.returncode:raise RuntimeError('Extracted result verification failed; see '+str(log))
# Cross-reference archives recorded throughout new indices, without evaluating arbitrary code.
references=0
for p in (extract/'results/stage4_upgrade_v1').rglob('*.json'):
 def visit(a):
  global references
  if isinstance(a,dict):
   for k,v in a.items():
    if isinstance(v,str) and k in ['archive','checkpoint','a_archive','b_archive','source_state_archive','a_state_archive','b_state_archive'] and v.startswith('results/'):
     assert (extract/v).exists(),(p,k,v);references+=1
    else:visit(v)
  elif isinstance(a,list):
   for v in a:visit(v)
 visit(json.loads(p.read_text()))
result=dict(passed=True,zip_path=str(archive.relative_to(R)),sha256=sha(archive),bytes=archive.stat().st_size,files_hashed=len(entries),references_checked=references,extracted_tests_exit_code=test.returncode,extracted_verify_exit_code=verify.returncode,extraction_directory=str(extract),seconds=time.perf_counter()-started,manifest=str(manifest.relative_to(R)))
(D/'ZIP_VERIFICATION_UPGRADE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
