import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_friedel import *
parser=argparse.ArgumentParser();parser.add_argument('--task',default='coarse');args=parser.parse_args();rows=[]
for r in json.loads((OUT/f'floating_boundary_scan/{args.task}_index.json').read_text()):
 key=dict(source=r['sha256'],code=sha(ROOT/'annni/stage6_friedel.py'));p=OUT/'floating_boundary_scan/friedel_cache'/(uid(key)+'.json')
 if p.exists():f=json.loads(p.read_text())
 else:f=dict(key=key,**fit_profile(np.load(ROOT/r['archive'])['x']));dump(p,f)
 rows.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],chi=r['chi'],initial=r['initial'],source_archive=r['archive'],**f));dump(OUT/f'floating_boundary_scan/{args.task}_friedel.json',rows);print(r['n'],r['h'],[round(x.get('K',float('nan')),3) for x in f['fits']],flush=True)
