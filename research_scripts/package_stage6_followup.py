"""Small standalone reading/plotting/verification increment, no old ZIPs."""
import sys,zipfile,shutil,subprocess,ast,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
D=ROOT/'deliverables';D.mkdir(exist_ok=True)
# Only transitive local Python dependencies of the actual followup verification/plots.
modules={'model','stage6_followup','stage6_boundaries','stage6_diagnostics','upgrade_detection'};todo=list(modules)
while todo:
 name=todo.pop();p=ROOT/'annni'/f'{name}.py'
 for node in ast.walk(ast.parse(p.read_text())):
  if isinstance(node,ast.ImportFrom) and node.level and node.module:
   dep=node.module.split('.')[0]
   if dep not in modules and (ROOT/'annni'/f'{dep}.py').exists():modules.add(dep);todo.append(dep)
files=[ROOT/'annni'/f'{m}.py' for m in modules]+[ROOT/'annni/__init__.py',ROOT/'requirements.lock.txt',ROOT/'configs/stage6_followup_v1.json',ROOT/'tests/test_stage6_followup.py',ROOT/'REPRODUCE_STAGE6_FOLLOWUP.md']
# Intake/deep branch regeneration depends on historical pipeline: documented, not needed to view/verify.
files += list((ROOT/'scripts').glob('*stage6_followup*'))
files += [p for p in OUT.rglob('*') if p.is_file() and p.suffix not in ['.tmp','.pyc','.lock'] and '__pycache__' not in p.parts]
manifest={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(files)) if p.exists()}
mp=D/'STAGE6_FOLLOWUP_MANIFEST.json';dump(mp,dict(run_id=cfg()['run_id'],generated_utc=datetime.now(timezone.utc).isoformat(),files=manifest,minimal_annni_modules=sorted(modules),scope='Standalone result reading, redraw and light verification. Deep historical intake/resume needs original exact inputs/module snapshots named in provenance. No old ZIP/density matrices/MPS/environment/fonts/credentials.'))
archive=D/'annni_stage6_followup_v1.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for rel in manifest:z.write(ROOT/rel,rel)
 z.write(mp,str(mp.relative_to(ROOT)))
dump(D/'STAGE6_FOLLOWUP_BUNDLE.json',dict(archive=str(archive.relative_to(ROOT)),sha256=sha(archive),bytes=archive.stat().st_size,files=len(manifest),manifest=str(mp.relative_to(ROOT)),instructions='Extract into an empty directory. Set ANNNI_PYTHON to the pinned Python interpreter, then bash scripts/stage6_followup.sh --verify or --redraw. Deep resume requires merging with original Stage6 inputs and modules; no old9GB ZIP needed for reading/verify/redraw.'))
print('Packaged',archive,archive.stat().st_size,'bytes',len(manifest),'files')
