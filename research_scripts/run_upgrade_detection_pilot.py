import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_detection import *
O=OUT/'detection';rows=json.loads((OUT/'development/noise_index.json').read_text());cfg=json.loads((O/'frozen.json').read_text());out=[]
for p in [0,.01,.05]:
 chosen=[next(r for r in rows if r['kappa']==0 and r['h']==h) for h in [.9,1.,1.1]];rho=[];labels=[]
 for point in chosen:
  r=next(r for r in point['methods']['B3'] if r['p']==p);a=np.load(ROOT/r['archive']);rho.append(a['rho']);labels.append(predict(vector(observations(a['rho'],8)),cfg))
 f=[uhlmann_squared(a,b) for a,b in zip(rho[:-1],rho[1:])];wide=uhlmann_squared(rho[0],rho[-1]);out.append(dict(kappa=0,p=p,h=[.9,1,1.1],h_mid=[.95,1.05],chi_f=(-np.log(f)/.01).tolist(),coarse_h_mid=1.,coarse_chi_f=-np.log(wide)/.04,labels=labels,structure_control='pointwise selected, not fixed branch',scope='minimal same-data D1/D2/D3 pilot; no critical-point inference'))
dump(O/'pilot.json',out)
from annni.model import Chain
if not (O/'binder.json').exists():
 binder=[]
 for n in [8,12,16]:
  chain=Chain(n);mz=chain.z.mean(1)
  for h in [.8,.9,1.,1.1,1.2]:
   s=chain.ground_state(0,h);m2=float(s.probabilities@(mz**2));m4=float(s.probabilities@(mz**4));binder.append(dict(n=n,kappa=0,h=h,mz2=m2,mz4=m4,binder=1-m4/(3*m2*m2),bc='PBC',definition='scalar ferro 1-<Mz^4>/(3<Mz^2>^2)',disposition='newly_executed'))
 dump(O/'binder.json',binder)
print('Noisy D1/D2/D3 pilot and independent finite-size Binder controls executed')
