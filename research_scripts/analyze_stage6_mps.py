import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_mps_analysis import *
parser=argparse.ArgumentParser();parser.add_argument('--task',default='coarse');args=parser.parse_args();O=OUT/'floating_boundary_scan';rows=[]
for r in json.loads((O/f'{args.task}_index.json').read_text()):
 key=dict(archive_sha=r['sha256'],analysis_sha=sha(ROOT/'annni/stage6_mps_analysis.py'));p=O/'analysis_cache'/ (uid(key)+'.json')
 if p.exists():analysis=json.loads(p.read_text())
 else:
  a=np.load(ROOT/r['archive']);raw=fit_models(a['central_raw'],r['n']);conn=fit_models(a['central_connected'],r['n']);q=np.median([f['q'] for f in raw if f['kind']=='power']);ent=entropy_fits(a['entropy'],r['n'],q);analysis=dict(key=key,raw=raw,connected=conn,entropy=ent);dump(p,analysis)
 raw_flag=r['solver_stopping_pass'];stats=r['sweeps'];corrected=bool(abs(stats['Delta_E'][-1]/max(stats['E'][-1],1.0))<1e-9 and abs(stats['Delta_S'][-1])<1e-6);row=dict(r,analysis=analysis,original_reported_stopping_flag=raw_flag,solver_stopping_pass=corrected,stopping_recomputed_from_raw_sweeps=True);rows.append(row);dump(O/f'{args.task}_analysis.json',rows)
 print(r['n'],r['h'],r['chi'],'c',round(analysis['entropy'][0]['c'],3),'winners',[(lo,min([f for f in analysis['raw'] if f['window'][0]==lo],key=lambda f:f['heldout_mse'])['kind']) for lo in [2,4]],flush=True)
