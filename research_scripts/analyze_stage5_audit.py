import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
a=json.loads((OUT/'selector_benchmark/audit/index.json').read_text());cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector'];table=[]
for r in a:
 s2=next(x['selection'] for x in r['S2_grid'] if x['config']==cfg);s0=r['selectors']['S0']['candidate'];s1=r['selectors']['S1']['candidate'];c=s2['candidate'];table.append(dict(n=r['n'],group=r['group'],kappa=r['kappa'],h=r['h'],candidates=len(r['candidates']),historical_pass=r['historical_selected']['joint_pass'],S0_pass=s0['joint_pass'],S1_pass=s1['joint_pass'],S2_pass=c['joint_pass'],oracle_available=r['oracle'] is not None,S0_cnots=s0['cnots'],S1_cnots=s1['cnots'],S2_cnots=c['cnots'],S2_unresolved=s2['selection_unresolved'],category=r['failure_category'],S2_fidelity=c['fidelity'],S2_energy_error=c['delta_e'],S2_w0=c['w0']))
with open(OUT/'selection_audit/fixed_candidates.csv','w') as f:w=csv.DictWriter(f,table[0]);w.writeheader();w.writerows(table)
summary={}
for g in ['map','heldout','n12']:
 rows=[r for r in table if r['group']==g];summary[g]=dict(points=len(rows),**{key:sum(r[key] for r in rows) for key in ['historical_pass','S0_pass','S1_pass','S2_pass','oracle_available','S2_unresolved']},failures=[r for r in rows if not r['historical_pass']],passing_controls=[r for r in rows if r['historical_pass']][:20])
dump(OUT/'selection_audit/summary.json',summary);print(json.dumps({k:{x:y for x,y in v.items() if x not in ['failures','passing_controls']} for k,v in summary.items()},indent=2))
