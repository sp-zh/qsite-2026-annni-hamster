import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.optimize import least_squares
from annni.stage5_adapt import ROOT,OUT,PLAN,sha,dump
O=OUT/'floating_validation';rows=json.loads((O/'index.json').read_text());fits=[]
for row in rows:
 a=np.load(ROOT/row['archive']);n=row['n'];entries=[]
 for key in ['central_raw','central_connected']:
  for lo,hi in [(2,n//3),(4,n//2-2)]:
   x=np.arange(lo,hi+1);y=a[key][x];split=int(.75*len(x));train=x[:split];test=x[split:]
   for kind in ['power','exponential']:
    def pred(v,r):return v[0]*np.cos(v[1]*r+v[2])*(r**(-v[3]) if kind=='power' else np.exp(-r/v[3]))
    best=None
    for q in np.linspace(.6,1.8,7):
     f=least_squares(lambda v:pred(v,train)-y[:split],[.5,q,0,1 if kind=='power' else 10],bounds=([-2,0,-np.pi,.001],[2,np.pi,np.pi,5 if kind=='power' else 10*n]),max_nfev=1000)
     if best is None or sum(f.fun**2)<sum(best.fun**2):best=f
    entries.append(dict(channel=key,window=[lo,hi],kind=kind,params=best.x.tolist(),optimizer_success=bool(best.success),optimizer_message=str(best.message),optimizer_nfev=int(best.nfev),train_mse=float(np.mean(best.fun**2)),heldout_mse=float(np.mean((pred(best.x,test)-y[split:])**2)),heldout_block=[int(test[0]),int(test[-1])],interpretation='Contiguous-distance extrapolation sensitivity, not independent statistical significance'))
  # Alternative entropy regression is sensitivity only, never used to tune main grade.
 l=np.arange(1,n);d=2*n/np.pi*np.sin(np.pi*l/n);q=row['fit_raw'][0]['q'];aux=[]
 for edge in [.15,.25]:
  m=(l>=edge*n)&(l<=(1-edge)*n);X=np.column_stack([np.ones(len(l)),np.log(d)/6,np.cos(2*q*l)/np.sqrt(d),np.sin(2*q*l)/np.sqrt(d),1/d]);coef=np.linalg.lstsq(X[m],a['entropy'][m],rcond=None)[0];aux.append(dict(edge=edge,c=float(coef[1]),coefficients=coef.tolist(),design_condition_number=float(np.linalg.cond(X[m])),rms=float(np.sqrt(np.mean((X[m]@coef-a['entropy'][m])**2))),scope='exploratory finite-size/oscillation sensitivity, not a theoretical correction or grading input'))
 fits.append(dict(n=n,kappa=row['kappa'],h=row['h'],chi=row['chi_max'],init=row['init'],archive=row['archive'],sha256=sha(ROOT/row['archive']),block_fits=entries,entropy_sensitivity=aux))
dump(O/'block_validation.json',fits)
old=json.loads((ROOT/'results/stage4_upgrade_v1/floating/evidence_grading.json').read_text())['rows'];graded=[]
for k,h in PLAN['floating_validation']['centers']:
 group=[r for r in rows if r['kappa']==k and r['h']==h];low=next(r for r in group if r['chi_max']==128 and r['init']=='plus');high=next(r for r in group if r['chi_max']==256 and r['init']=='plus');alt=next(r for r in group if r['chi_max']==256 and r['init']=='antiphase');a=np.load(ROOT/low['archive']);b=np.load(ROOT/high['archive']);c=np.load(ROOT/alt['archive']);de=abs(high['energy']-low['energy'])/128;dc=float(max(abs(a['central_raw']-b['central_raw'])));ds=float(max(abs(a['entropy']-b['entropy'])));initdc=float(max(abs(c['central_raw']-b['central_raw'])));prev=next(r for r in old if r['kappa']==k and r['h']==h);cs=[r['c'] for r in high['entropy_fits']];qs=[r['q'] for r in high['fit_raw'][::2]];fit=next(r for r in fits if r['n']==128 and r['kappa']==k and r['h']==h and r['chi']==256 and r['init']=='plus');blocks=fit['block_fits'];wins=[blocks[i]['heldout_mse']<=blocks[i+1]['heldout_mse'] for i in range(0,len(blocks),2)];conv=de<1e-5 and dc<.01 and ds<.03;stable=all(.75<x<1.25 for x in cs) and abs(qs[0]-prev['q'][-1])<.1
 graded.append(dict(kappa=k,h=h,old_grade=prev['evidence_grade'],new_grade='support_strengthened' if conv and stable and all(wins) and initdc<.01 else 'candidate' if conv else 'not_resolved',bond_converged=conv,delta_e_per_site=de,delta_c=dc,delta_entropy=ds,initialization_delta_c=initdc,entropy_c=cs,old_n96_c=prev['entropy_c'][-2:],q=qs,power_wins_heldout_blocks=wins,scope='Discrete tested center and separate neighboring points only; no inferred continuous interval',needs_chi512=not conv))
dump(O/'evidence_update.json',dict(rows=graded,main_protocol=PLAN['floating_validation'],auxiliary_entropy='Exploratory sensitivity introduced after jobs started; never used to choose or claim main-grade support',continuous_interval_claim=False));print(json.dumps(graded,indent=2))
# Neighbors are checked independently, never filled from center labels.
neighbor_checks=[];chi512_requests=[]
for k,h in PLAN['floating_validation']['centers']:
 for delta in [-.025,.025]:
  hh=round(h+delta,3)
  for n in [96,128]:
   group=[r for r in rows if r['n']==n and r['kappa']==k and r['h']==hh and r['init']=='plus'];low=next(r for r in group if r['chi_max']==128);high=next(r for r in group if r['chi_max']==256);a=np.load(ROOT/low['archive']);b=np.load(ROOT/high['archive']);de=abs(high['energy']-low['energy'])/n;dc=float(max(abs(a['central_raw']-b['central_raw'])));ds=float(max(abs(a['entropy']-b['entropy'])));conv=de<1e-5 and dc<.01 and ds<.03;f=next(r for r in fits if r['n']==n and r['kappa']==k and r['h']==hh and r['chi']==256 and r['init']=='plus');blocks=f['block_fits'];wins=[blocks[i]['heldout_mse']<=blocks[i+1]['heldout_mse'] for i in range(0,len(blocks),2)];neighbor_checks.append(dict(n=n,kappa=k,h=hh,bond_converged=conv,delta_e_per_site=de,delta_c=dc,delta_s=ds,c=[v['c'] for v in high['entropy_fits']],power_wins_blocks=wins,q=[v['q'] for v in high['fit_raw'][::2]],interpretation='Constituent diagnostics at this actual discrete neighboring point, no inferred continuous phase label'))
   if not conv:chi512_requests.append(dict(n=n,kappa=k,h=hh,init='plus'))
for r in graded:
 if r['needs_chi512']:chi512_requests.append(dict(n=128,kappa=r['kappa'],h=r['h'],init='plus'))
controls=[r for r in rows if r['kappa']==0];dump(O/'neighbor_checks.json',neighbor_checks);dump(O/'control_checks.json',[dict(n=r['n'],kappa=r['kappa'],h=r['h'],entropy_c=[v['c'] for v in r['entropy_fits']],fit_raw=r['fit_raw'],sweeps=r['sweeps'],expected='Ising critical c=.5' if r['h']==1 else 'gapped control; no c1 expectation',scope='Same fitting pipeline; expectation is a control, never fixed during regression') for r in controls]);dump(O/'chi512_requests.json',chi512_requests)
# Match the installed TeNPy 1.1.1 stopping implementation, not just bond differences.
sweep_checks=[]
for r in rows:
 sw=r['sweeps'];lastE=float(sw['E'][-1]);dE=float(sw['Delta_E'][-1]);dS=float(sw['Delta_S'][-1]);stop_ok=abs(dE/max(lastE,1.0))<1e-9 and abs(dS)<1e-6;sweep_checks.append(dict(n=r['n'],kappa=r['kappa'],h=r['h'],chi=r['chi_max'],init=r['init'],sweep_entries=len(sw['E']),last_delta_E=dE,last_delta_S=dS,configured_stopping_tolerances_met=stop_ok,bond_stability_is_separate=True,source='TeNPy1.1.1 algorithms/dmrg.py DMRGEngine.is_converged: absolute DeltaS and DeltaE/max(E,1); do not substitute a guessed relative entropy test'))
dump(O/'sweep_stopping_checks.json',sweep_checks)

# Preserve both entropy windows at each size; no fitted thermodynamic extrapolation.
history=[];oldraw=json.loads((ROOT/'results/stage4_upgrade_v1/floating/refine_index.json').read_text())
for k,h in PLAN['floating_validation']['centers']:
 for n,pool in [(64,oldraw),(96,oldraw),(128,rows)]:
  r=next(r for r in pool if r['n']==n and r['kappa']==k and r['h']==h and r['chi_max']==256 and r['init']=='plus');history.append(dict(n=n,kappa=k,h=h,c_windows=[v['c'] for v in r['entropy_fits']],q_windows=[v['q'] for v in r['fit_raw'][::2]],source=r['archive'],disposition='historical_reused' if n<128 else 'newly_executed'))
dump(O/'center_size_history.json',history)
