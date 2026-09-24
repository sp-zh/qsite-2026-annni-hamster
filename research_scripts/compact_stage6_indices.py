"""Lossless index normalization: complete optimizer traces remain in hashed raw records."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import candidate_paths
parser=argparse.ArgumentParser();parser.add_argument('--task',default='development');task=parser.parse_args().task
paths=candidate_paths(task)+list((OUT/'legacy_b3').glob(task+'_index.json'));changes=[]
def compact(r):
 if 'steps' not in r:return r
 p=Path(r['archive']).with_suffix('.json');return dict({k:v for k,v in r.items() if k!='steps'},raw_record=str(p),raw_record_sha=sha(ROOT/p))
for p in paths:
 rows=json.loads(p.read_text());changed=any('steps' in r.get('selected',{}) or any('steps' in m['selected'] for m in r.get('methods',{}).values()) for r in rows)
 if not changed:continue
 before=sha(p);backup=OUT/'verification/original_full_indices'/(before+'.json');backup.parent.mkdir(exist_ok=True)
 if not backup.exists():backup.write_bytes(p.read_bytes())
 for r in rows:
  if 'methods' in r:
   for m in r['methods'].values():m['selected']=compact(m['selected'])
  else:r['selected']=compact(r['selected']);r['runs']=[compact(x) for x in r['runs']]
 dump(p,rows);changes.append(dict(index=str(p.relative_to(ROOT)),original_backup=str(backup.relative_to(ROOT)),before=before,after=sha(p),reason='Remove duplicate steps from index only; original full index and raw parameter/gate/optimizer records preserved. No numerical result or configuration change.'))
dump(OUT/f'verification/index_normalization_{task}.json',changes);print(task,'normalized',len(changes))
