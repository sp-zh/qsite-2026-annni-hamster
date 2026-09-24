"""Package actual code and data, extract, validate SHA256 and data references."""
import json,hashlib,zipfile,tempfile,os,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/stage3_v1';DIST=ROOT/'deliverables';DIST.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
folders=['annni','scripts','tests','configs','upstream','results/baseline','results/calibration_v1','results/diagnostics_v1','results/noise_smoke_v1','results/stage3_v1']
files=[]
for folder in folders:
    files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and not any(t in p.parts for t in ['__pycache__','.pytest_cache','.mplconfig']) and p.suffix not in ['.pyc','.tmp']]
for name in ['README.md','requirements.lock.txt','requirements.txt','pyproject.toml','stage3.ipynb','baseline.ipynb','calibration.ipynb','REPRODUCE_STAGE3.md']:
    if (ROOT/name).exists():files.append(ROOT/name)
excluded={'results/calibration_v1/notebook_execution.log':'Nonessential prior notebook cleanup trace contains local home path; original stays untouched.'}
files=sorted(p for p in set(files) if str(p.relative_to(ROOT)) not in excluded)
exclusion_path=DIST/'PACKAGE_EXCLUSIONS.json';exclusion_path.write_text(json.dumps(excluded,indent=2))
manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
manifest['PACKAGE_EXCLUSIONS.json']=sha(exclusion_path)
manifest_path=DIST/'PACKAGE_MANIFEST.json';manifest_path.write_text(json.dumps(manifest,indent=2))
archive=DIST/'annni_stage3_v1.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,str(p.relative_to(ROOT)))
    z.write(manifest_path,'PACKAGE_MANIFEST.json')
    z.write(exclusion_path,'PACKAGE_EXCLUSIONS.json')
print('ZIP created:',len(files),'files',archive.stat().st_size,flush=True)
with tempfile.TemporaryDirectory(prefix='annni-stage3-verify-') as temp:
    root=Path(temp)
    with zipfile.ZipFile(archive) as z:z.extractall(root)
    for p,digest in manifest.items():assert sha(root/p)==digest,p
    references=set()
    def walk(obj):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in ['archive','reference_source','main_archive','alternate_archive','opposite_direction_archive','source'] and isinstance(v,str) and v.startswith('results/'):
                    assert (root/v).is_file(),v;references.add(v)
                walk(v)
        elif isinstance(obj,list):
            for v in obj:walk(v)
    for p in (root/'results/stage3_v1').rglob('*.json'):walk(json.loads(p.read_text()))
    env=os.environ|{'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MPLCONFIGDIR':str(root/'.mplconfig'),'PYTHONPATH':str(root)}
    result=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=root,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    audit_run=subprocess.run([sys.executable,'scripts/verify_stage3_results.py'],cwd=root,env=env,capture_output=True,text=True)
    assert audit_run.returncode==0,audit_run.stdout+audit_run.stderr
    verification=dict(extracted_result_audit=audit_run.stdout.strip(),zip_name=archive.name,zip_sha256=sha(archive),zip_bytes=archive.stat().st_size,files_verified=len(manifest),relative_data_references_verified=len(references),extracted_tests=result.stdout.strip(),passed=True,excluded=['virtual environments','font caches','credentials','unrelated personal files'],note='Manifest hashes refer to delivered files before any reproduction rebuild. Verification sidecar is external to avoid circular archive hashes.')
(DIST/'ZIP_VERIFICATION.json').write_text(json.dumps(verification,indent=2))
print(json.dumps(verification,indent=2))
