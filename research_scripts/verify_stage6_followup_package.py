import sys,zipfile,subprocess,argparse,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();dest=Path(a.directory).resolve();dest.mkdir(parents=True,exist_ok=True);assert not any(dest.iterdir());start=time.perf_counter();bundle=read(ROOT/'deliverables/STAGE6_FOLLOWUP_BUNDLE.json');archive=ROOT/bundle['archive'];assert sha(archive)==bundle['sha256']
with zipfile.ZipFile(archive) as z:
 assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(dest)
manifest=read(dest/'deliverables/STAGE6_FOLLOWUP_MANIFEST.json')['files']
for rel,m in manifest.items():assert sha(dest/rel)==m['sha256'],rel
# No old Stage6 directory or base archive exists here.
assert not (dest/'results/stage6_v1').exists()
import os
env=dict(os.environ,ANNNI_PYTHON=sys.executable,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');logs={}
for mode in ['--verify','--redraw']:
 r=subprocess.run(['bash','scripts/stage6_followup.sh',mode],cwd=dest,env=env,text=True,capture_output=True);logs[mode]=dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);assert r.returncode==0,logs[mode]
# Compare deterministic redraw dimensions/pixels, separately from archive hashes.
from PIL import Image,ImageChops
figures=[]
for path in (dest/'results/stage6_followup_v1/figures').glob('*.png'):
 old=ROOT/path.relative_to(dest);im=Image.open(path).convert('RGB');orig=Image.open(old).convert('RGB');assert im.size==orig.size;equal=ImageChops.difference(im,orig).getbbox() is None;assert equal,path.name;figures.append(dict(name=path.name,pixels_identical=equal,size=im.size))
dump(ROOT/'deliverables/STAGE6_FOLLOWUP_CLEAN_CHECK.json',dict(status='passed',directory=str(dest),verified_manifest_files=len(manifest),standalone_without_old_stage6=True,logs=logs,redraw_figures=figures,seconds=time.perf_counter()-start));print('Clean increment verify and redraw passed',len(manifest),'files')
