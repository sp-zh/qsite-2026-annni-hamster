"""Freeze completed MPS artifacts for later resume and package verification."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'results/stage4_upgrade_v1/floating';file=O/'archive_manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if file.exists():
 a=json.loads(file.read_text());assert all(sha(R/n)==v for n,v in a['files'].items());print('MPS archive hashes verified',len(a['files']))
else:
 files={str(p.relative_to(R)):sha(p) for p in O.glob('n*') if p.suffix in ['.json','.npz','.pkl']}
 file.write_text(json.dumps(dict(files=files,scope='Frozen after completed coarse/refine/validation; checkpoint pickle only from this local trusted run'),indent=2));print('MPS artifacts frozen',len(files))
