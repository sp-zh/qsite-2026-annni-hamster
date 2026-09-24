"""Report the optional extra size without converting a finite-window fit into a phase label."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump,np
O=OUT/'floating_validation';p=O/'size_extension_index.json'
if not p.exists():raise SystemExit('Optional extra size not executed; no result fabricated')
rows=json.loads(p.read_text());summary=[]
for r in rows:
 summary.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],chi=r['chi_max'],c_windows=[x['c'] for x in r['entropy_fits']],q_windows=[x['q'] for x in r['fit_raw'][::2]],max_discarded_weight=r['max_discarded_weight'],last_delta_E=r['sweeps']['Delta_E'][-1],last_delta_S=r['sweeps']['Delta_S'][-1],archive=r['archive'],checkpoint=r['checkpoint']))
history=json.loads((O/'center_size_history.json').read_text());history+=[dict(n=r['n'],kappa=r['kappa'],h=r['h'],c_windows=r['c_windows'],q_windows=r['q_windows'],source=r['archive'],disposition='newly_executed_optional_size') for r in summary if r['chi']==max(x['chi'] for x in summary)]
dump(O/'size_extension_analysis.json',dict(rows=summary,size_history=history,protocol=json.loads((O/'size_extension_plan.json').read_text()),status=json.loads((O/'size_extension_status.json').read_text()),scope='One prior-specified extra OBC size for the old elevated-c point. Same two windows and freely fitted c; one initial path. No thermodynamic extrapolation or automatic upgraded phase grade.'))
print(summary)
