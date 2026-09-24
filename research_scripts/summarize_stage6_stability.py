"""Count independent starts within each physical coordinate, never pool them as points."""
import sys,csv,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
data=json.loads((OUT/'confirmation/stability_paired_summary.json').read_text())['rows'];rows=[]
for method,n,k,h in sorted({(r['method'],r['n'],r['kappa'],r['h']) for r in data}):
 selected=[r for r in data if (r['method'],r['n'],r['kappa'],r['h'])==(method,n,k,h)];seeds=sorted(r['seed'] for r in selected)
 assert seeds==[631,743,857],(method,k,h,seeds)
 passed=sum(r['joint_pass'] for r in selected)
 rows.append(dict(method=method,n=n,kappa=k,h=h,region=selected[0]['region'],seeds=seeds,joint_pass_runs=passed,observable_pass_runs=sum(r['observable_pass'] for r in selected),state_pass_runs=sum(r['state_pass'] for r in selected),candidate_pool_exists_runs=sum(r['candidate_pool_exists'] for r in selected),at_least_two_joint=passed>=2,all_three_joint=passed==3,at_least_two_observable=sum(r['observable_pass'] for r in selected)>=2,median_fidelity=float(np.median([r['fidelity'] for r in selected])),worst_fidelity=min(r['fidelity'] for r in selected),median_cnots=float(np.median([r['cnots'] for r in selected])),minimum_energy_delta_per_site=min(r['delta_e'] for r in selected),median_energy_delta_per_site=float(np.median([r['delta_e'] for r in selected])),source_archives=[r['source'] for r in selected]))
summary=[]
for method,region in itertools.product(sorted({r['method'] for r in rows}),['all','low_field','antiphase_band','interior']):
 group=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)]
 summary.append(dict(method=method,region=region,physical_coordinates=len(group),independent_runs=3*len(group),two_of_three_joint=sum(r['at_least_two_joint'] for r in group),three_of_three_joint=sum(r['all_three_joint'] for r in group),two_of_three_observable=sum(r['at_least_two_observable'] for r in group),at_least_one_joint=sum(r['joint_pass_runs']>0 for r in group)))
dump(OUT/'confirmation/stability_by_coordinate.json',dict(rows=rows,summary=summary,scope='12 fixed physical coordinates, three independent seeds631/743/857;631 reuses the main confirmation run and is not counted as new execution. All failures are retained. Warm starts are excluded.'))
with (OUT/'confirmation/stability_by_coordinate.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
print([r for r in summary if r['region']=='all'])
