"""Exact signed bias identity and empirical sampling variance, never sums of norms."""
import sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=argparse.ArgumentParser();p.add_argument('--task',default='core');task=p.parse_args().task
source=OUT/f'end_to_end/{task}_analysis.json';data=json.loads(source.read_text());rows=[]
for point in data:
 target=np.load(ROOT/point['ed_archive'])['exact']
 for e in point['entries']:
  a=np.load(ROOT/e['archive']);clean=a['own_clean'];exact=a['exact'];prep=clean-target;shift=exact-clean;bias=exact-target
  prep2=float(np.mean(prep**2));shift2=float(np.mean(shift**2));cross=float(2*np.mean(prep*shift));bias2=float(np.mean(bias**2));assert abs(bias2-prep2-shift2-cross)<1e-12
  for budget in PLAN['measurement']['budgets']:
   samples=a[f'samples_{budget}'];measurement=samples-exact;measurement2=float(np.mean(measurement**2));cross_sampling=float(2*np.mean(measurement*bias));total=float(np.mean((samples-target)**2));assert abs(total-bias2-measurement2-cross_sampling)<1e-12
   rows.append(dict(kappa=point['kappa'],h=point['h'],method=e['method'],estimator=e['estimator'],p=e['p'],budget=budget,repeats=len(samples),epsilon_prep=prep,delta_noise=shift if e['estimator']=='raw' else None,exact_estimator_shift=shift,prep_MSE=prep2,noise_or_estimator_shift_MSE=shift2,prep_shift_cross_term=cross,exact_bias_MSE_ED=bias2,measurement_MSE_around_exact=measurement2,empirical_measurement_mean=np.mean(measurement,axis=0),measurement_bias_cross_term=cross_sampling,total_MSE_ED=total,source=e['archive']))
groups={}
for r in rows:groups.setdefault((r['method'],r['estimator'],r['p'],r['budget']),[]).append(r)
summary=[]
for key,rr in groups.items():
 fields=['prep_MSE','noise_or_estimator_shift_MSE','prep_shift_cross_term','exact_bias_MSE_ED','measurement_MSE_around_exact','measurement_bias_cross_term','total_MSE_ED'];summary.append(dict(method=key[0],estimator=key[1],p=key[2],budget=key[3],coordinates=len(rr),**{f:float(np.mean([r[f] for r in rr])) for f in fields}))
dump(OUT/f'end_to_end/{task}_error_decomposition.json',dict(rows=rows,summary=summary,source=str(source.relative_to(ROOT)),sha256=sha(source),scope='MSE uses the fixed full vector [C(0..N-1), SF(all q), Mx]; its Fourier-related components are not independent evidence. Exact vector identity: MSE_ED = preparation_MSE + noise/estimator_shift_MSE + signed cross term. Empirical total additionally equals exact_bias_MSE + measurement_MSE + signed sampling cross term. Sampling terms use32 simulated repetitions, not exact statistical expectations. Raw delta_noise refers to physical circuit(p)-circuit(0); mitigated shifts are estimator bias and are not a physical noise channel. These continuous errors do not by themselves establish a physical phase label or information-theoretic impossibility.'))
print(task,len(rows),'signed decompositions')
