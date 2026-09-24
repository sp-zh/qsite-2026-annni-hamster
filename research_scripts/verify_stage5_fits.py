"""Regression of actual TeNPy-campaign fitting code against known signed data."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_stage5_floating import fits,np,O,dump
n=96;r=np.arange(n//2);l=np.arange(1,n);q=1.31;c_target=.9
entropy=.7+c_target/6*np.log(2*n/np.pi*np.sin(np.pi*l/n))
rows=[]
for kind in ['power','exponential']:
 y=np.ones_like(r,dtype=float);y[1:]=.65*np.cos(q*r[1:]+.17)*(r[1:]**(-.6) if kind=='power' else np.exp(-r[1:]/8))
 assert np.any(y<0) and np.any(y>0)
 f,e=fits(y,entropy,n)
 for start in [0,2]:
  correct=next(x for x in f[start:start+2] if x['kind']==kind);wrong=next(x for x in f[start:start+2] if x['kind']!=kind)
  assert correct['rss']<1e-12 and correct['rss']<wrong['rss']*1e-4,(kind,correct,wrong)
  assert abs(correct['q']-q)<1e-6
 assert max(abs(x['c']-c_target) for x in e)<1e-10
 rows.append(dict(kind=kind,fit=f,entropy=e,target_c=c_target,target_q=q))
dump(O/'fitting_regression.json',dict(passed=True,rows=rows,scope='Actual campaign fit function recovers known signed oscillatory power/exponential correlations and freely fitted OBC entropy c, using both frozen windows. Not evidence of a physical floating phase.'))
print('Signed-correlation and free-c entropy regression passed')
