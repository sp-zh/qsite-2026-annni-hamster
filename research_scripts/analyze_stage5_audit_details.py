import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_baseline_selectors import choose
rows=json.loads((OUT/'selector_benchmark/audit/index.json').read_text());out=[];cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector']
for r in rows:
 c=r['selectors']['S0']['candidate'];best=min(r['candidates'],key=lambda c:c['energy']);new=choose(r['candidates'],'S2',cfg)['candidate'];tags=[]
 if not c['joint_pass']:
  if c['w0']<.99:tags.append('translation_leakage_observed_not_sole_causal_proof')
  if c['delta_e']<=.001 and not c['state_pass']:tags.append('energy_accurate_low_pure_fidelity; near-degeneracy not proved without spectrum')
  if not tags:tags.append('insufficient_evidence_for_sector_or_degeneracy_cause')
 out.append(dict(group=r['group'],n=r['n'],kappa=r['kappa'],h=r['h'],S0_pass=c['joint_pass'],S2_pass=new['joint_pass'],candidate_qualified=r['oracle'] is not None,primary_category=r['failure_category'],posterior_tags=tags,S0_w0=c['w0'],S2_w0=new['w0'],S2_energy_penalty_per_site=(new['energy']-best['energy'])/r['n'],no_coordinate_exception_used=True))
counter=json.loads((OUT/'selection_audit/counterexample.json').read_text());cc=counter['candidates'];summary=[{k:c[k] for k in ['ref','cnots','energy','delta_e','fidelity','epsilon_c','epsilon_sf','epsilon_mx','w_plus','w0','eta_T','variance']} for c in cc if (c['ref']=='ghz' and c['cnots']==31) or (c['ref']=='antiphase' and c['cnots']==32)]
actual_counter_selectors={rule:{key:choose(cc,rule,cfg)['candidate'][key] for key in ['ref','cnots','energy','delta_e','fidelity','epsilon_c','epsilon_sf','epsilon_mx','w0']} for rule in ['S0','S1','S2']}
dump(OUT/'selection_audit/failure_details.json',dict(counterexample_actual_selectors=actual_counter_selectors,rows=out,counterexample_31_32=summary,all_counterexample_resources=sorted(set(c['cnots'] for c in cc)),note='Saved candidates span several budgets, not only a pair one CNOT apart. Low pure fidelity alone does not establish wrong physical label. Exact observable errors are reported.'))
print(summary)
