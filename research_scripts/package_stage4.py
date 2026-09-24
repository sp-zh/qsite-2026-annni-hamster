"""Package actual evidence; verify the extracted default reproduction entry."""
import os,sys,json,hashlib,zipfile,tempfile,subprocess,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage4_v1';DIST=ROOT/'deliverables';DIST.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
folders=['annni','scripts','tests','configs','upstream','results/baseline','results/calibration_v1','results/diagnostics_v1','results/noise_smoke_v1','results/stage3_v1','results/stage4_v1','submission']
files=[]
for folder in folders:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and not any(v in p.parts for v in ['__pycache__','.pytest_cache','.mplconfig']) and p.suffix not in ['.pyc','.tmp']:files.append(p)
for name in ['README.md','requirements.lock.txt','requirements.txt','pyproject.toml','baseline.ipynb','calibration.ipynb','stage3.ipynb','REPRODUCE_STAGE3.md','deliverables/PACKAGE_MANIFEST.json','deliverables/ZIP_VERIFICATION.json','deliverables/PACKAGE_EXCLUSIONS.json']:
 if (ROOT/name).exists():files.append(ROOT/name)
excluded={'results/calibration_v1/notebook_execution.log':'Nonessential historical cleanup trace contains a local home path; protected original remains unchanged.'}
files=sorted(p for p in set(files) if str(p.relative_to(ROOT)) not in excluded)
historical=json.loads((DIST/'PACKAGE_MANIFEST.json').read_text());entries={}
for p in files:
 name=str(p.relative_to(ROOT));digest=sha(p)
 category='unchanged_stage3_history' if historical.get(name)==digest else ('versioned_modified_source_or_entry' if name in historical else 'new_stage4_or_submission_file')
 entries[name]={'sha256':digest,'category':category,'bytes':p.stat().st_size}
exclusion=DIST/'PACKAGE_EXCLUSIONS_STAGE4.json';exclusion.write_text(json.dumps(excluded,indent=2));entries['PACKAGE_EXCLUSIONS.json']={'sha256':sha(exclusion),'category':'package_privacy_exclusions','bytes':exclusion.stat().st_size}
manifest=DIST/'PACKAGE_MANIFEST_STAGE4.json';manifest.write_text(json.dumps({'files':entries,'note':'Manifest excludes itself and external ZIP hash sidecar. Regeneration changes generated artifacts; verify before rebuilding.'},indent=2))
archive=DIST/'annni_submission_stage4_v1.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(ROOT)))
 z.write(manifest,'PACKAGE_MANIFEST_STAGE4.json');z.write(exclusion,'PACKAGE_EXCLUSIONS.json')
print('ZIP created',len(entries),'files',archive.stat().st_size,'bytes',flush=True)
with tempfile.TemporaryDirectory(prefix='annni-stage4-extracted-') as tmp:
 root=Path(tmp)
 with zipfile.ZipFile(archive) as z:z.extractall(root)
 for name,r in entries.items():assert sha(root/name)==r['sha256'],name
 refs=set()
 def walk(o):
  if isinstance(o,dict):
   for k,v in o.items():
    if k in ['archive','selection_archive','reference_source','source'] and isinstance(v,str) and v.startswith('results/'):
     assert (root/v).is_file(),v;refs.add(v)
    walk(v)
  elif isinstance(o,list):
   for v in o:walk(v)
 for p in (root/'results/stage4_v1').rglob('*.json'):
  if 'source_before' not in p.parts:walk(json.loads(p.read_text()))
 assets=0
 for name in ['submission/report.md','submission/presentation.html']:
  for pair in re.findall(r'\]\((figures/[^)]+)\)|src="(figures/[^"]+)"',(root/name).read_text()):
   for v in pair:
    if v:assert (root/'submission'/v).is_file();assets+=1
 export_python=Path.home()/'.cache/scientific-runtimes/python-runtime/dependencies/python/bin/python3'
 env=os.environ|{'ANNI_PYTHON':sys.executable,'ANNI_EXPORT_PYTHON':str(export_python),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MPLCONFIGDIR':str(root/'.mplconfig'),'PYTHONPATH':str(root)}
 result=subprocess.run(['bash','scripts/reproduce_submission.sh'],cwd=root,env=env,capture_output=True,text=True)
 log=(result.stdout+'\n'+result.stderr).replace(str(root),'<EXTRACTED_PROJECT>').replace(str(ROOT),'<PROJECT_ROOT>').replace(str(Path.home()),'<USER_HOME>')
 (DIST/'EXTRACTED_REPRODUCTION_STAGE4.log').write_text(log)
 assert result.returncode==0,log[-5000:]
 nb=json.loads((root/'submission/submission.ipynb').read_text());cells=[c for c in nb['cells'] if c['cell_type']=='code'];assert len(cells)==8 and all(c['execution_count'] for c in cells)
 verification=dict(passed=True,zip_name=archive.name,zip_sha256=sha(archive),zip_bytes=archive.stat().st_size,manifest_files_verified=len(entries),data_references_verified=len(refs),figure_references_verified=assets,extracted_default_reproduction_exit=result.returncode,extracted_fresh_kernel_cells=len(cells),full_test_summary=next(line for line in result.stdout.splitlines() if '46 passed' in line),log='EXTRACTED_REPRODUCTION_STAGE4.log',stages_reexecuted=['46 tests','archive/hash/physical consistency audit including all new p0 densities','derived analysis and figures','fresh-kernel notebook lightweight checks','HTML slides and editable notes','3-page PDF export'],full_optimization_reexecuted=False,note='Manifest verified before regenerating outputs. External sidecar avoids circular ZIP hash. Original delivered PDF was visually inspected; extracted regenerated PDF is structurally checked, not a second manual visual review.')
(DIST/'ZIP_VERIFICATION_STAGE4.json').write_text(json.dumps(verification,indent=2));print(json.dumps(verification,indent=2),flush=True)
