"""Stage6 provenance and deadline. Historical outputs are never write targets."""
import json,hashlib,time,os
from pathlib import Path
from datetime import datetime,timezone
os.environ.setdefault("MPLCONFIGDIR",str(Path(__file__).resolve().parents[1]/".mplconfig"))
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/stage6_v1'
PLAN=json.loads((OUT/'experiment_plan.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uid(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(x,indent=2,default=lambda a:a.item() if isinstance(a,np.generic) else a.tolist() if isinstance(a,np.ndarray) else str(a)));tmp.replace(p)
def guard():
 if datetime.now(timezone.utc)>=datetime.fromisoformat(PLAN['deadline']):raise TimeoutError('Stage6 deadline reached; saved records retained')
def progress(task,completed,next_command,**extra):
 dump(OUT/f'verification/progress_{task}.json',dict(time=datetime.now(timezone.utc).isoformat(),completed=completed,next_command=next_command,**extra))
