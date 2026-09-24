"""Controlled paired ablations; improvements and regressions retained together."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
rows=[];summaries=[]
for task in ['development','validation','confirmation','n12','n12_192']:
 folder='failure_mechanisms' if task in ['development','validation'] else 'confirmation' if task=='confirmation' else 'n12_transfer';p=OUT/f'{folder}/{task}_paired_summary.json'
 if not p.exists():continue
 data=json.loads(p.read_text())['rows'];points={}
 for r in data:points.setdefault((r['n'],r['kappa'],r['h'],r['seed']),{})[r['method']]=r
 pairs=[('C0','C1','search_change_fixed_physical_pool'),('C0','C2','basis_reference_change_greedy'),('C2','C3','search_change_fixed_wall_pool'),('C1','C3','basis_reference_change_forward_search'),('B3','H6','frozen_full_pipeline_change')]
 for a,b,scope in pairs:
  for key,methods in points.items():
   if a not in methods or b not in methods:continue
   x,y=methods[a],methods[b];outcome='both_pass' if x['joint_pass'] and y['joint_pass'] else 'improved' if y['joint_pass'] else 'regressed' if x['joint_pass'] else 'both_fail'
   rows.append(dict(task=task,n=key[0],kappa=key[1],h=key[2],seed=key[3],region=x['region'],baseline=a,candidate=b,scope=scope,outcome=outcome,baseline_joint=x['joint_pass'],candidate_joint=y['joint_pass'],baseline_observable=x['observable_pass'],candidate_observable=y['observable_pass'],baseline_cnots=x['cnots'],candidate_cnots=y['cnots'],baseline_seconds=x['search_seconds_standalone'],candidate_seconds=y['search_seconds_standalone'],baseline_fidelity=x['fidelity'],candidate_fidelity=y['fidelity'],baseline_delta_e=x['delta_e'],candidate_delta_e=y['delta_e']))
groups={}
for r in rows:
 for region in ['all',r['region']]:groups.setdefault((r['task'],r['baseline'],r['candidate'],region),[]).append(r)
for key,rr in groups.items():
 summaries.append(dict(task=key[0],baseline=key[1],candidate=key[2],region=key[3],coordinates=len(rr),outcomes=dict(collections.Counter(r['outcome'] for r in rr)),baseline_median_cnots=float(np.median([r['baseline_cnots'] for r in rr])),candidate_median_cnots=float(np.median([r['candidate_cnots'] for r in rr])),baseline_total_search_seconds=sum(r['baseline_seconds'] for r in rr),candidate_total_search_seconds=sum(r['candidate_seconds'] for r in rr)))
dump(OUT/'failure_mechanisms/paired_ablations.json',dict(rows=rows,summary=summaries,scope='Same prescribed budget caps, not necessarily equal executed CNOTs or classical calls. Full pipeline comparison is not a one-factor causal attribution. Wall-basis change also changes reference and pool parameterization. No ED-based circuit selection. Sleep-overlapping elapsed seconds remain raw and are not clean CPU-efficiency measurements.'))
print('Paired comparisons',len(rows))
