"""Only execute predeclared bond-convergence followups when triggered."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_stage5_floating import run,O,dump
requests=json.loads((O/'chi512_requests.json').read_text());rows=[]
for r in requests:
 rows.append(run(r['n'],r['kappa'],r['h'],512,r['init']));dump(O/'chi512_index.json',rows)
if not requests:dump(O/'chi512_index.json',[])
