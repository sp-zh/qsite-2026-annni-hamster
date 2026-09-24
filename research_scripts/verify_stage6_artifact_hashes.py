"""Verify archived scientific payloads against their originating execution records."""
import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import ROOT,OUT,dump
started=time.perf_counter();references={};conflicts=[]
def add(path,expected,source):
 key=str(path)
 if key in references and references[key]['sha256']!=expected:conflicts.append(dict(path=key,source=source,previous=references[key]))
 references[key]=dict(sha256=expected,source=source)
def walk(value,source):
 if isinstance(value,dict):
  for path_key,hash_key in [('archive','sha256'),('checkpoint','checkpoint_sha'),('counts_archive','counts_sha256'),('raw_record','raw_record_sha'),('metadata_record','metadata_sha256')]:
   if isinstance(value.get(path_key),str) and isinstance(value.get(hash_key),str):add(value[path_key],value[hash_key],source)
  for x in value.values():
   if isinstance(x,(dict,list)):walk(x,source)
 elif isinstance(value,list):
  for x in value:
   if isinstance(x,(dict,list)):walk(x,source)
for p in OUT.rglob('*.json'):
 if p.name=='artifact_hash_verification.json':continue
 try:walk(json.loads(p.read_text()),str(p.relative_to(ROOT)))
 except json.JSONDecodeError:raise AssertionError(('Incomplete JSON',str(p)))
failures=[];size=0
for rel,reference in references.items():
 p=Path(rel);p=p if p.is_absolute() else ROOT/p
 if not p.exists():failures.append(dict(path=rel,reason='missing',source=reference['source']));continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
 size+=p.stat().st_size
 if h.hexdigest()!=reference['sha256']:failures.append(dict(path=rel,expected=reference['sha256'],actual=h.hexdigest(),source=reference['source']))
result=dict(payloads=len(references),bytes=size,failures=failures,conflicting_references=conflicts,seconds=time.perf_counter()-started,passed=not failures and not conflicts,scope='Payload hashes referenced by actual Stage6 records, including reused historical archives. Execute only after numerical writers stop for final verification.')
dump(OUT/'verification/artifact_hash_verification.json',result);print(json.dumps(result,indent=2));assert result['passed']
