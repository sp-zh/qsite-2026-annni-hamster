import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_assess import *
from annni.stage6_io import candidate_paths,candidate_rows
parser=argparse.ArgumentParser();parser.add_argument('--task',default='development');args=parser.parse_args();rows=[]
if args.task in ['confirmation','n12','n12_192','map','low_map','windows']:
 frozen=json.loads((OUT/'confirmation/method_frozen.json').read_text());assert frozen
 # Evaluation can unseal only after all intended candidate rows are complete.
 expected=96 if args.task=='confirmation' else None
 allrows=candidate_rows(args.task)
 if expected is not None:assert len({(r['kappa'],r['h']) for r in allrows})==expected
 dump(OUT/f'confirmation/{args.task}_unsealed.json',dict(timestamp=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),freeze_sha=sha(OUT/'confirmation/method_frozen.json'),candidate_count=len(allrows)))
else:allrows=candidate_rows(args.task)
for r in allrows:
 methods={}
 for name,m in r['methods'].items():
  selected=assess_run(m['selected']);allruns=[json.loads((ROOT/p).read_text()) for p in m['runs']];evaluated=[assess_run(x) for x in allruns];methods[name]=dict(**selected,components=m.get('components',[m.get('component',name)]),candidate_pool_exists=any(x['candidate_exists'] for x in evaluated),reference_results=evaluated,total_seconds=sum(x['seconds'] for x in allruns),total_nfev=sum(x['nfev'] for x in allruns))
 rows.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],region=r.get('region'),methods=methods))
dump(OUT/f'failure_mechanisms/{args.task}_assessment.json',rows)
for name in sorted({name for r in rows for name in r['methods']}):
 v=[r['methods'][name] for r in rows if name in r['methods']];print(name,len(v),sum(x['joint_pass'] for x in v),sum(x['candidate_pool_exists'] for x in v),round(sum(x['total_seconds'] for x in v),1),flush=True)
