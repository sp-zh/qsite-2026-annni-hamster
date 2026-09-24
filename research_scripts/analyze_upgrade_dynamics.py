"""Frozen time means, descriptive static association, with held-out fields separate."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_detection import predict
rows=json.loads((OUT/'dynamics/index.json').read_text());mapping=json.loads((OUT/'map/index.json').read_text());cfg=json.loads((OUT/'detection/frozen.json').read_text());out=[]
for r in rows:
 m=next(x for x in mapping if abs(x['kappa']-r['kappa'])<1e-10 and abs(x['h']-r['h'])<1e-10)
 selected=m['methods']['B3'];a=np.load(ROOT/selected['archive'])
 # ED validates static features; it never trains the frozen time-average extraction.
 from annni.upgrade_gates import observations,vector
 ed=reference(8,r['kappa'],r['h'])
 out.append(dict(kappa=r['kappa'],h=r['h'],initial=r['initial'],dt=r['dt'],p=r['p'],heldout_h=r['heldout_h'],dynamic_features=r['features'],static_circuit_diagnostic=predict(vector(observations(a['state'],8)),cfg),static_preparation_pass=selected['selected']['joint_pass'],static_ED_observables=vector(observations(ed[0],8)).tolist()))
associations=[]
for initial in PLAN['dynamics']['initial']:
 for p in [0,.01,.05]:
  for dt in [.2,.1,.05]:
   g=[x for x in out if x['initial']==initial and x['p']==p and x['dt']==dt]
   for hold in [False,True]:
    a=[x for x in g if x['heldout_h']==hold]
    for dynamic,idx in [('mean_c1',1),('mean_sf0',8),('mean_sfpi2',10),('mean_mx',16)]:
     x=np.array([r['dynamic_features'][dynamic] for r in a]);y=np.array([r['static_ED_observables'][idx] for r in a]);corr=float(np.corrcoef(x,y)[0,1]) if min(x.std(),y.std())>1e-12 else None
     associations.append(dict(initial=initial,p=p,dt=dt,heldout_h=hold,points=len(a),feature=dynamic,pearson_descriptive=corr,mean_absolute_dynamic_static_difference=float(np.mean(abs(x-y)))))
dump(OUT/'dynamics/static_association.json',dict(rows=out,associations=associations,protocol='Previously frozen uniform mean over 11 samples t=0..2; held-out h=.6,1.4. No fitted mapping or threshold. Correlations are descriptive with only four held-out coordinates and no independent uncertainty estimate; no equilibrium classification claim.'))
print('Saved held-out/static descriptive comparison',len(out))
