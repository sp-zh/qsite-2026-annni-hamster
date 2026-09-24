"""Descriptive strata and failure accounting; no model/selector fitting."""
import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
S=OUT/'submission';stats=json.loads((S/'statistics.json').read_text());a=list(csv.DictReader(open(OUT/'matched_grid.csv')));table=[]
strata={'all':lambda k,h:True,'low_field_h<=0.5':lambda k,h:h<=.5,'high_field_h>=1.2':lambda k,h:h>=1.2,'competition_0.4<=k<=0.6':lambda k,h:.4<=k<=.6,'frustrated_k>=0.7':lambda k,h:k>=.7}
for name,predicate in strata.items():
 for method in ['B3','B4']:
  for p in [0,.01,.05]:
   for mask in ['all','common_pass']:
    rows=[r for r in a if r['method']==method and float(r['p'])==p and predicate(float(r['kappa']),float(r['h'])) and (mask=='all' or r['common_pass']=='True')]
    table.append(dict(stratum=name,method=method,p=p,mask=mask,points=len(rows),mean_c_new=float(np.mean([float(r['epsilon_c_new']) for r in rows])),mean_c_old=float(np.mean([float(r['epsilon_c_old']) for r in rows])),new_wins=sum(float(r['epsilon_c_new'])<float(r['epsilon_c_old']) for r in rows)))
dump(S/'descriptive_regions.json',dict(protocol='Post-computation descriptive coordinate strata, overlapping and not used for selection or training; no significance claim.',rows=table))
branch=[]
for name,path in [('B3','branches/index.json'),('B4','branches/b4_index.json')]:
 file=OUT/path
 if not file.exists():continue
 rows=json.loads(file.read_text())
 for p in [0,.01,.05]:
  entries=[c for r in rows for e in r['endpoints'] if e['both_prep_pass'] for c in e['comparisons'] if c['p']==p]
  branch.append(dict(method=name,p=p,intervals=len(rows),qualified_endpoint_comparisons=len(entries),sensitive=sum(c['sensitive'] for c in entries),meaning='Same-coordinate counterpart comparison after fixed-structure energy refit; threshold full-feature max difference >.02'))
dump(S/'branch_summary.json',branch)
mechanisms=[dict(method='D1',mechanism='Full C(r), SF, Mx reference distances and changes',input='2N+1 real observables',measurement_settings=2,training='Analytic reference prototypes; frozen limits',reference_consistency='Control tests and cross-method agreement only',error_rate=None),dict(method='D2',mechanism='Squared pure/Uhlmann overlap sensitivity',input='State vector or full density matrix',measurement_settings=None,training='No classifier training',reference_consistency='Pure limit, self-fidelity, nested step and fixed-structure peak tests',error_rate=None,cost='Full simulator state access; no hardware measurement implementation'),dict(method='D3',mechanism='Development-scaled PCA3 + kmeans3, analytic control mapping, anomaly cutoff',input='Same 2N+1 observables as D1',measurement_settings=2,training='Clean development only; shared D1 degraded veto',reference_consistency='Frozen control, held-out and noise outputs',error_rate=None)]
dump(OUT/'detection/mechanism_comparison.json',mechanisms)
print('Region and branch accounting written')
