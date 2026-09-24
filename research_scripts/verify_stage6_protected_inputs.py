"""Stream-check the pre-existing scientific inputs; never modify them."""
import sys, json, hashlib, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import ROOT, OUT, dump
started=time.perf_counter()
manifest=json.loads((OUT/'verification/protected_inputs.json').read_text())
failures=[];total=0
for rel, expected in manifest.items():
    p=ROOT/rel
    if not p.is_file():
        failures.append(dict(path=rel,reason='missing'));continue
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
    total+=p.stat().st_size
    if h.hexdigest()!=expected:failures.append(dict(path=rel,expected=expected,actual=h.hexdigest()))
result=dict(files=len(manifest),bytes=total,failures=failures,passed=not failures,seconds=time.perf_counter()-started,scope='All entries in the Stage6 protected input manifest, sourced from the immutable Stage5 package manifest; not a claim to audit unlisted files.')
dump(OUT/'verification/protected_inputs_verified.json',result)
print(json.dumps(result,indent=2));assert not failures
