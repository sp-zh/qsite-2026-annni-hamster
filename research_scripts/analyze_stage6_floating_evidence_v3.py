"""Evidence v3: same v2 criteria, adding one registered actual-chain continuation.
Prior maps remain immutable. No confirmation labels or detector training change.
"""
import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';protocol=json.loads((O/'evidence_protocol_v1.json').read_text());allrows=[];friedel={}
for task in ['coarse','bounded','followup','controls','final_continuation']:
 p=O/f'{task}_analysis.json'
 if p.exists():allrows+=json.loads(p.read_text())
 p=O/f'{task}_friedel.json'
 if p.exists():friedel.update({r['source_archive']:r for r in json.loads(p.read_text())})
latest={}
for r in allrows:latest[(r['n'],r['h'],r['chi'],r['initial'])]=r

def metrics(r):
 a=r['analysis'];fits=a['raw'];q=[x['q'] for x in fits if x['kind']=='power'];c=[x['c'] for x in a['entropy'] if not x['oscillation_correction']];cc=[x['c'] for x in a['entropy'] if x['oscillation_correction']];ratios={name:[] for name in ['ordered','power','exponential']}
 for window in sorted(set(tuple(x['window']) for x in fits)):
  block=[x for x in fits if tuple(x['window'])==window]
  for x in block:ratios[x['kind']].append(x['heldout_mse']/max(min(y['heldout_mse'] for y in block if y['kind']!=x['kind']),1e-300))
 xi=[x['parameters'][3] for x in fits if x['kind']=='exponential'];kf=friedel.get(r['archive'],{}).get('fits',[]);valid=len(kf)==2 and all(x.get('status')=='finite_size_fit_only' and not x.get('parameters_at_bound') and x.get('relative_rmse',1) <= .03 for x in kf);ks=[x['K'] for x in kf if 'K' in x];stable=valid and max(ks)-min(ks)<=.08
 anti=max(abs(x-np.pi/2) for x in q)<=.015 and r['tail_rms']>.15 and max(c)<.25
 floating=all(x<=.9 for x in ratios['power']) and stable and all(.25<x<.5 for x in ks) and all(.7<=x<=1.3 for x in c) and min(abs(x-np.pi/2) for x in q)>.015
 para=all(x<=.9 for x in ratios['exponential']) and max(xi)/r['n']<1/6 and max(c)<.4 and r['mx']>.5
 return dict(q=q,c_uncorrected=c,c_with_oscillation_correction=cc,heldout_ratios=ratios,xi=xi,xi_over_N=[x/r['n'] for x in xi],Friedel_fits=kf,K_fit_valid=bool(valid),K_window_stable=bool(stable),K_values=ks,antiphase_signature=bool(anti),floating_signature=bool(floating),paramagnetic_signature=bool(para),source=r['archive'],n=r['n'],chi=r['chi'],actual_chi=r['actual_chi'],initial=r['initial'],solver_stopping_pass=r['solver_stopping_pass'],energy_per_site=r['energy_per_site'],tail_rms=r['tail_rms'])
def agreement(a,b):
 if a is None or b is None:return dict(available=False)
 aa=np.load(ROOT/a['archive']);bb=np.load(ROOT/b['archive']);dc=float(max(abs(aa['central_raw']-bb['central_raw'])));de=float(max(abs(aa['entropy']-bb['entropy'])));offset=float(np.mean(aa['entropy']-bb['entropy']));centered=float(max(abs(aa['entropy']-bb['entropy']-offset)));return dict(available=True,correlation_max_difference=dc,entropy_max_difference=de,entropy_constant_offset=offset,entropy_shape_difference=centered,energy_per_site_difference=abs(a['energy_per_site']-b['energy_per_site']),strict_pass=dc<=.01 and de<=.03,correlation_agreement=dc<=.01,note='Entropy offset may reflect ordered near-degenerate cat/broken branches; raw strict flag is retained, never silently relaxed.')
rows=[]
for h in sorted(set(r['h'] for r in allrows)):
 group=[r for key,r in latest.items() if r['h']==h];detail=[metrics(r) for r in group];plus=latest.get((128,h,256,'plus'));anti=latest.get((128,h,256,'antiphase'));small=latest.get((96,h,128,'plus'));bond=latest.get((128,h,128,'plus'));ia=agreement(plus,anti);ba=agreement(plus,bond);required=[plus,anti,small,bond];complete=all(x is not None for x in required);solver=complete and all(r['solver_stopping_pass'] for r in required);pm=metrics(plus) if plus else None;am=metrics(anti) if anti else None;sm=metrics(small) if small else None
 strict=solver and ia.get('strict_pass',False) and ba.get('strict_pass',False)
 size_compatible=bool(sm and pm and all(x<=1 for x in sm['heldout_ratios']['power']) and min(abs(x-np.pi/2) for x in sm['q'])>.015 and abs(np.median(sm['q'])-np.median(pm['q']))<=2*np.pi/96)
 larger_contradiction=any(x['solver_stopping_pass'] and (x['antiphase_signature'] or x['paramagnetic_signature'] or (x['K_fit_valid'] and x['K_window_stable'] and not all(.25<q<.5 for q in x['K_values']))) for x in detail if x['n']>128)
 if strict and size_compatible and not larger_contradiction and pm['floating_signature'] and am['floating_signature']:status='supported_floating_sample'
 elif solver and ia.get('correlation_agreement',False) and ba.get('correlation_agreement',False) and pm['antiphase_signature'] and am['antiphase_signature'] and sm['antiphase_signature']:status='supported_antiphase_sample'
 elif strict and pm['paramagnetic_signature'] and am['paramagnetic_signature'] and sm['paramagnetic_signature']:status='supported_paramagnetic_side_sample'
 elif any(x['floating_signature'] for x in detail):status='candidate_floating_missing_convergence_or_size_controls'
 elif any(x['antiphase_signature'] for x in detail):status='antiphase_compatible_incomplete_controls'
 elif any(x['paramagnetic_signature'] for x in detail):status='paramagnetic_compatible_incomplete_controls'
 else:status='finite_size_crossover_unresolved'
 conflicts=[dict(n=x['n'],chi=x['chi'],initial=x['initial'],K_values=x['K_values'],source=x['source']) for x in detail if x['n']>=96 and x['solver_stopping_pass'] and x['K_fit_valid'] and x['K_window_stable'] and not all(.25<q<.5 for q in x['K_values'])]
 if status=='supported_floating_sample' and conflicts:status='finite_size_crossover_unresolved'
 rows.append(dict(cross_size_K_conflicts=conflicts,kappa=.8,h=h,status=status,all_required_controls_present=complete,all_required_solver_stops=bool(solver),strict_bond_and_initial_agreement=bool(strict),N96_power_q_consistency=size_compatible,larger_size_contradiction=bool(larger_contradiction),initial_agreement=ia,bond_agreement=ba,metrics=detail,largeN_extra=[x for x in detail if x['n']>=160],interpretation='Discrete tested evidence, OBC only; no transfer of labels to N8 PBC. Fit comparisons are finite-window predictive checks, not rigorous statistical p-values.'))
 dump(O/'evidence_map_v3.json',rows)
supported={name:[r['h'] for r in rows if r['status']==name] for name in ['supported_antiphase_sample','supported_floating_sample','supported_paramagnetic_side_sample']};a=supported['supported_antiphase_sample'];f=supported['supported_floating_sample'];p=supported['supported_paramagnetic_side_sample'];lower=[max(x for x in a if x<min(f)),min(f)] if f and any(x<min(f) for x in a) else None;upper=[max(f),min(x for x in p if x>max(f))] if f and any(x>max(f) for x in p) else None
summary=dict(version=3,timestamp=datetime.now(timezone.utc).isoformat(),prior_evidence_sha=sha(O/'evidence_map_v2.json'),continuation_registration_sha=sha(O/'final_continuation_registration.json'),protocol_sha=sha(O/'evidence_protocol_v1.json'),analysis_sha=sha(__file__),supported_samples=supported,lower_transition_bracket=lower,upper_transition_bracket=upper,candidate_floating_samples=[r['h'] for r in rows if r['status'].startswith('candidate_floating')],unresolved_samples=[r['h'] for r in rows if r['status']=='finite_size_crossover_unresolved'],scope='Brackets span supported sampled sides and may contain unresolved points; not exact thermodynamic phase boundaries or confidence intervals.',raw_observable_antiphase_check='Ordered phase can show entropy constant offsets from near-degenerate branches; full strict entropy agreement is reported separately even when order/q/c across both initial states support antiphase physics.');dump(O/'interval_evidence_v3.json',summary)
flat=[dict(kappa=.8,h=r['h'],status=r['status'],all_controls=r['all_required_controls_present'],solver_stops=r['all_required_solver_stops'],strict_bond_initial=r['strict_bond_and_initial_agreement'],Ns=';'.join(map(str,sorted({x['n'] for x in r['metrics']})))) for r in rows]
with (O/'evidence_map_v3.csv').open('w') as file:w=csv.DictWriter(file,fieldnames=flat[0]);w.writeheader();w.writerows(flat)
print(summary)
