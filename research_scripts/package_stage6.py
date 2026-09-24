"""Package actual Stage6 code/data, layered on the immutable full Stage5 bundle.
No environments, credentials, fonts or unrelated caches are included.
Run only after numerical workers finish and final evidence is written.
"""
import sys,json,hashlib,zipfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/stage6_v1';D=ROOT/'deliverables';D.mkdir(exist_ok=True)
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
 return h.hexdigest()
def pack(name,paths):
 manifest={}
 for p in sorted(set(paths)):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.pyc','.tmp','.lock']:continue
  rel=str(p.relative_to(ROOT));manifest[rel]=dict(sha256=digest(p),bytes=p.stat().st_size)
 meta=D/f'PACKAGE_MANIFEST_STAGE6_{name.upper()}.json';meta.write_text(json.dumps(dict(files=manifest,scope=name,created_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()),indent=2));archive=D/f'annni_stage6_v1_{name}.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
  for rel in manifest:z.write(ROOT/rel,rel)
  z.write(meta,str(meta.relative_to(ROOT)))
 return dict(archive=str(archive.relative_to(ROOT)),sha256=digest(archive),bytes=archive.stat().st_size,files=len(manifest),manifest=str(meta.relative_to(ROOT)))
start=time.perf_counter();code=[]
for folder in ['annni','scripts','tests','configs']:
 code.extend((ROOT/folder).rglob('*.py'));code.extend((ROOT/folder).rglob('*.sh'));code.extend((ROOT/folder).rglob('*.json'))
for pattern in ['README.md','REPRODUCE_STAGE6.md','requirements*.lock.txt']:
 code.extend(ROOT.glob(pattern))
# The data bundle contains every Stage6 saved result, including failed and partial runs.
data=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.tmp','.pyc','.lock']]
parts=[pack('code',code),pack('data',data)];base=D/'annni_stage5_v1.zip';expected='193e4e58a0d4ef1d1122b2afab301f4ad3aa412afaf4cfe1a8aa546c91d2c5d5';actual=digest(base);assert actual==expected,'Immutable Stage5 base archive mismatch'
baseinfo=dict(archive=str(base.relative_to(ROOT)),sha256=actual,bytes=base.stat().st_size,disposition='historical_reused_complete_base')
result=dict(base=baseinfo,parts=parts,combination='Extract Stage5 base, then Stage6 code, then Stage6 data into the same fresh directory; all archive entries are relative to project root.',excludes=['virtual environments','font files','credentials','.git','unrelated caches'],seconds=time.perf_counter()-start)
(D/'STAGE6_BUNDLE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
