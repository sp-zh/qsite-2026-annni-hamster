"""Versioned layered reference: physical labels and RN proxies remain separate."""
import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_reference_scopes import scopes
O=OUT/'reference_atlas';rows=[]
for task in ['development','validation','confirmation']:
 p=O/f'{task}_evaluation.json'
 if not p.exists():continue
 for r in json.loads(p.read_text()):rows.append(dict(cohort=task,n='8;12;16',bc='PBC',kappa=r['kappa'],h=r['h'],**scopes(r['label'],r['level'],r),sources=';'.join(r['sources']),evidence=r['evidence']))
p=OUT/'floating_boundary_scan/evidence_map.json'
if p.exists():
 mapping={'supported_antiphase_sample':'antiphase_supported_OBC_sample','supported_floating_sample':'floating_supported_OBC_sample','supported_paramagnetic_side_sample':'paramagnetic_supported_OBC_sample'}
 for r in json.loads(p.read_text()):
  rows.append(dict(cohort='MPS_main_slice',n=';'.join(map(str,sorted({x['n'] for x in r['metrics']}))),bc='OBC',kappa=.8,h=r['h'],physical_label=mapping.get(r['status']),physical_level='Rlarge_OBC_sample' if r['status'] in mapping else 'Rlarge_unresolved',RN_proxy_label=None,legacy_reference_level=None,reason='Multi-N, chi, initial-state, stopping and signed-correlation/Friedel/entropy evidence; discrete finite-size support, not rigorous exclusion of arbitrarily large gapped correlation lengths.',sources=';'.join(x['source'] for x in r['metrics']),evidence=r['status']))
dump(O/'reference_regions_v3.json',rows)
with (O/'reference_regions_v3.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=sorted({key for r in rows for key in r}));w.writeheader();w.writerows(rows)
boundaries=json.loads((O/'boundary_reference.json').read_text());p=OUT/'floating_boundary_scan/interval_evidence.json';interval=json.loads(p.read_text()) if p.exists() else {}
extra=[]
for name,key in [('antiphase_to_candidate_floating','lower_transition_bracket'),('candidate_floating_to_paramagnetic_side','upper_transition_bracket')]:
 value=interval.get(key);extra.append(dict(n='multiN',kappa=.8,feature=name,level='Rlarge_OBC_bracket',bc='OBC',resolvable=value is not None,low=value[0] if value else None,high=value[1] if value else None,position=None,all_peaks=None,competing=None,physical_interpretation='Bracket of supported sampled sides, with unresolved points retained; not a midpoint estimate, thermodynamic exact boundary or statistical confidence interval.',reference_numerical_ambiguous_count=None))
dump(O/'boundary_reference_v3.json',boundaries+extra)
with (O/'boundary_reference_v3.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=boundaries[0]);w.writeheader();w.writerows(boundaries+extra)
print('Reference v3 regions',len(rows),'RN features',len(boundaries),'requested OBC transition intervals',len(extra))
