"""Merge disjoint/resumed index batches without counting cached repeats as new data."""
from .stage6_common import *
def measurement_rows(paths):
 result={}
 for p in sorted(paths):
  for r in json.loads(Path(p).read_text()):
   key=(r['n'],r['kappa'],r['h'])
   if key in result:
    def signature(a):return sorted((e['method'],e['estimator'],e['record']['p'],e['record']['archive'],e['record']['sha256']) for e in a['entries'])
    assert signature(result[key])==signature(r),('Inconsistent overlapping batches',key,p)
   result[key]=r
 return [result[k] for k in sorted(result)]

def candidate_paths(task, directory=None):
 """Exact task with numeric seed/start suffix; n12 must not include n12_192/window."""
 import re
 directory=Path(directory) if directory is not None else OUT/'domain_wall_candidates'
 pattern=re.compile(re.escape(task)+r'_\d+_\d+_index\.json$')
 return sorted(p for p in directory.glob(task+'_*_index.json') if pattern.fullmatch(p.name))

def candidate_rows(task):
 result={}
 for path in candidate_paths(task):
  for row in json.loads(path.read_text()):
   seeds=tuple(sorted({m['selected']['seed'] for m in row['methods'].values()}))
   key=(row['n'],row['kappa'],row['h'],seeds)
   if key in result:
    signature=lambda r: sorted((name,m['selected']['archive'],m['selected']['sha256']) for name,m in r['methods'].items())
    assert signature(result[key])==signature(row),('Inconsistent candidate batch overlap',key,path)
   result[key]=row
 return [result[key] for key in sorted(result)]
