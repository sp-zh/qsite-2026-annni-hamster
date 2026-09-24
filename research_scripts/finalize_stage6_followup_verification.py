"""Verify historical immutability, source provenance and actual inventory."""
import sys,csv,collections,importlib.metadata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_followup import *
start=time.perf_counter();protected=read(OUT/'verification/protected_inputs.json');failures=[]
for rel,expected in protected.items():
 if sha(ROOT/rel)!=expected:failures.append(rel)
stat=read(OUT/'verification/old_file_stat_inventory.json');statbad=[]
for rel,old in stat.items():
 p=ROOT/rel
 if not p.exists() or [p.stat().st_size,p.stat().st_mtime_ns]!=old:statbad.append(rel)
assert not failures and not statbad,(failures,statbad)
inputs=read(OUT/'inputs.json');refs=read(OUT/'window_reference.json');idx=read(OUT/'A_index.json');byid={x['point_id']:x for x in idx};rows=[]
for w in refs:
 for h in w['h']:
  pt=point(w['kappa'],float(h));rs=[read(ROOT/p) for p in byid[pt['id']]['records']];assert len(rs)==18
  rows.append(dict(kappa=w['kappa'],h=h,reference_resolvable=w['frozen_reference']['resolvable'],parameter_source=pt['source'],parameter_source_sha=pt['source_sha'],gate_hash=uid(pt['gates']),complete=True,historical_reused=sum(r['disposition']=='historical_reused' for r in rs),newly_executed=sum(r['disposition']=='newly_executed' for r in rs),combination_count=len(rs),methods=['raw','zne_quadratic','sv'],p=[0,.01,.05],budgets=[10000,100000]))
def csvout(p,rows):
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows])
csvout(OUT/'window_inventory_completed.csv',rows)
resource=[]
for x in read(OUT/'B_index.json'):
 for p in x['records']:
  r=read(ROOT/p);resource.append(dict(kappa=r['kappa'],h=r['h'],p=r['p'],estimator=r['method'],comparison=r['mode'],budget=r['budget'],equal_CNOT_shots_completed=r['equal_CNOT_verified'],zero_CNOT_control=r['zero_CNOT_control'],actual_G=r['CNOT_shots_per_repeat'],actual_shots=r['shots_per_repeat'],archive=r['archive'],sha256=r['sha256'],scientific_fingerprint=uid(r['key']),disposition=r['disposition']))
csvout(OUT/'resource_experiment_inventory_completed.csv',resource)
old_boundaries=read(OLD/'end_to_end/boundary_comparison.json')
changes=[]
for new in read(OUT/'window_completion/coverage.json'):
 if new['mode']!='equal_shots':continue
 rr=[r for r in old_boundaries if r['method']=='B3' and r['p']==new['p'] and r['estimator']==new['method'] and r['budget']==new['budget'] and r['repeat'] is not None]
 changes.append(dict(p=new['p'],method=new['method'],budget=new['budget'],requested_windows=6,reference_resolvable=5,old_complete_windows=len({r['kappa'] for r in rr}),new_complete_windows=new['executed_complete_windows'],old_matched_window_equivalents=sum(r['matched'] for r in rr)/32,new_matched_window_equivalents=new['frozen_matching_window_equivalents'],reason='New execution for three missing windows; frozen matching protocol unchanged. The new secondary audit is not a retroactive historical rule.'))
csvout(OUT/'window_completion/old_vs_followup_coverage.csv',changes)
dump(OUT/'window_completion/old_vs_followup_coverage.json',changes)
current={str(p.relative_to(ROOT)):sha(p) for p in [*ROOT.glob('scripts/*stage6_followup*'),ROOT/'annni/stage6_followup.py',ROOT/'tests/test_stage6_followup.py',ROOT/'requirements.lock.txt'] if p.is_file()}
dump(OUT/'verification/historical_integrity.json',dict(protected_hashed_files=len(protected),old_stat_checked_files=len(stat),hash_failures=failures,old_file_changes=statbad,seconds=time.perf_counter()-start))
dump(OUT/'metadata.json',dict(config=cfg(),current_code=current,environment=read(OUT/'verification/environment.json'),elapsed_wall_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(cfg()['started_utc'])).total_seconds(),historical_integrity=read(OUT/'verification/historical_integrity.json'),execution=read(OUT/'verification/execution_statistics.json'),sampler_fix=dict(initial_failure_log='verification/A_attempt1_failure.log',reason='Same literal coordinate can refer to distinct frozen B3 selections in core versus window cohorts; gate fingerprint rejection now skips incompatible cache rather than stopping.',old_counts_retained=True,postfix_resampling='New code fingerprint gives explicitly new random streams; old valid draws remain archived and charged, excluded from final cohort statistics.'),cohort_amendment=read(OUT/'verification/control_cohort_amendment.json'),final_provenance='Original Stage6 files remain unchanged; this is a separately dated directed supplement.'))
print('Historical integrity and final inventories passed')
meta=read(OUT/'metadata.json')
meta['actual_versions']={name:importlib.metadata.version(name) for name in ['numpy','scipy','pennylane','matplotlib','nbformat','nbclient','pytest']}
meta['cache_catalog_enrichment']=read(OUT/'verification/cache_catalog_enrichment.json')
dump(OUT/'metadata.json',meta)
