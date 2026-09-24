import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from annni.stage6_diagnostics import *
O=OUT/'reference_atlas';features=[];regions=[];boundaries=[];curves={};windows=[]
for n in [8,12,16]:
 path=O/f'slices_n{n}.json'
 if not path.exists():continue
 for ktext,rows in json.loads(path.read_text()).items():
  k=float(ktext);hs=np.array([r['h'] for r in rows]);states=[np.load(ROOT/r['archive'])['state'] for r in rows];vs=np.array([np.r_[r['correlations'],r['structure_factor'],r['mx']] for r in rows]);cur=response_curves(hs,vs,n,states,[r['reference_numerical_ambiguous'] for r in rows]);curves[f'n{n}_k{k}']={**cur,'h':hs,'values':vs,'binder':[r['binder'] for r in rows]}
  for r,s in zip(rows,states):
   label,level,reason=physical_reference(n,k,r['h'],s,r,r['binder']);q=np.arange(n)*2*np.pi/n;_,z,_=geometry(n);m=z@np.exp(1j*np.pi/2*np.arange(n))/n;prob=abs(s)**2;ap4=float(prob@abs(m)**4);ap2=r['structure_factor'][n//4];apbinder=1-ap4/(2*ap2**2)
   features.append(dict(n=n,kappa=k,h=r['h'],m0=r['structure_factor'][0],map=ap2,mx=r['mx'],binder=r['binder'],antiphase_binder=apbinder,sector_gap=r['sector_gap'],residual=r['residual'],ambiguous=r['reference_numerical_ambiguous'],source=r['archive'],level='RN',bc='PBC'))
   regions.append(dict(n=n,kappa=k,h=r['h'],label=label or 'unlabeled',level=level,evidence=reason,source=r['archive'],bc='PBC'))
  for name in ['minus_dm0_dh','minus_dmap_dh','dmx_dh','chi_f']:
   result=peaks_and_primary(hs,cur[name]);primary=result['primary'];boundaries.append(dict(n=n,kappa=k,feature=name,level='RN',bc='PBC',resolvable=result['resolvable'],low=primary['interval_low'] if primary else None,high=primary['interval_high'] if primary else None,position=primary['coordinate'] if primary else None,all_peaks=result['peaks'],competing=result['competing'],physical_interpretation='Finite-size named feature only; C and SF are Fourier-related, not independent evidence',reference_numerical_ambiguous_count=sum(r['reference_numerical_ambiguous'] for r in rows)))
  if n==8 and k in [0,.3,.45,.5,.55,.8]:
   metric='minus_dm0_dh' if k<.5 else 'minus_dmap_dh';p=peaks_and_primary(hs,cur[metric])['primary'];center=p['coordinate'] if p else .15
   # Common predeclared window for all methods/noise; not selected by circuit success.
   for h in np.arange(max(.01,round(center/.0125)*.0125-.10),min(2,round(center/.0125)*.0125+.10001),.0125):windows.append(dict(kappa=k,h=round(float(h),6),region='boundary_window',feature=metric))
dump(O/'curves.json',curves);dump(O/'boundary_reference.json',boundaries);dump(O/'reference_regions.json',regions);dump(O/'circuit_window_coordinates.json',windows)
for name,rows in [('reference_features',features),('reference_regions',regions),('boundary_reference',boundaries)]:
 with (O/(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
dump(O/'protocol.json',dict(levels=dict(R0='analytic limits/controlled interiors; R0_extension explicit finite-field physics evidence',RN='PBC same-N sector ED and named continuous response peaks',Rlarge='separate multi-size evidence, appended after MPS; never copies labels to N8'),grid_weight='Tensor product Voronoi cell widths on each stated rectangular domain; never pool refined point counts for an area fraction',peak_rule=peaks_and_primary([0,1,2],[0,1])['rule'],reference_denominators={str(n):dict(requested_kappa_slices=len(PLAN['atlas']['kappa_n8'] if n==8 else PLAN['atlas']['kappa_large']),resolvable_named_features=sum(r['resolvable'] for r in boundaries if r['n']==n),requested_named_features=sum(r['n']==n for r in boundaries)) for n in [8,12,16]},warning='Single kappa>.5 peak is not split into two transitions; endpoints retained as unresolved. C/SF redundancy explicitly removed for new feature distance.'))
print('atlas features',len(features),'boundary records',len(boundaries),'window coordinates',len(windows))
