"""Verify manifests and run light reproduction from a clean extraction.
The caller specifies an already-created empty directory; no destructive cleanup.
"""
import sys,argparse,zipfile,json,hashlib,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();dest=Path(a.directory).resolve();dest.mkdir(parents=True,exist_ok=True);assert not any(dest.iterdir()),'Destination must be empty';bundle=json.loads((ROOT/'deliverables/STAGE6_BUNDLE.json').read_text());start=time.perf_counter()
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
for part in [bundle['base'],*bundle['parts']]:
 archive=ROOT/part['archive'];assert digest(archive)==part['sha256']
 with zipfile.ZipFile(archive) as z:
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(dest)
checks=[]
for part in bundle['parts']:
 manifest=json.loads((dest/part['manifest']).read_text())['files']
 for rel,meta in manifest.items():
  path=dest/rel;assert path.exists() and digest(path)==meta['sha256'],rel
 checks.append(dict(manifest=part['manifest'],verified_files=len(manifest)))
result=subprocess.run([sys.executable,'scripts/reproduce_stage6_light.py'],cwd=dest,text=True,capture_output=True);assert result.returncode==0,result.stdout+result.stderr
# The interpreter is external but all research code and data resolve in the clean directory.
out=dict(status='passed',directory=str(dest),python=sys.executable,manifest_checks=checks,light_reproduction=json.loads(result.stdout),stderr=result.stderr,seconds=time.perf_counter()-start,scope='Full code/data archive hashes and entries, then four literal circuits and one count reconstruction from the clean extraction. Does not rerun all optimization/DMRG experiments.')
(ROOT/'deliverables/STAGE6_CLEAN_EXTRACTION_CHECK.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
