import sys,argparse,collections,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_observation_analysis import *
from annni.stage6_arms import load
from annni.stage6_area import cell_weights
from annni.stage6_io import measurement_rows
from annni.stage6_reference_roundoff import map_reference
from annni.upgrade_gates import geometry,h_action
parser=argparse.ArgumentParser();parser.add_argument('--task',default='map');args=parser.parse_args();task=args.task;f=json.loads((OUT/'confirmation/method_frozen.json').read_text());new=f['physical_method'];old=np.load(ROOT/'results/baseline/grid_n8.npz');rows=[];n=8;_,z,_=geometry(n);m=z.mean(1)
for batch in [measurement_rows((OUT/'end_to_end').glob(task+'_*_index.json'))]:
 for point in batch:
  k,h=point['kappa'],point['h'];ki=np.flatnonzero(abs(old['kappa']-k)<1e-12);hi=np.flatnonzero(abs(old['h']-h)<1e-12)
  if len(ki) and len(hi):
   i,j=int(ki[0]),int(hi[0]);state=old['states'][i,j];target=np.r_[old['correlations'][i,j],old['structure_factor'][i,j],old['mx'][i,j]];energy=float(old['energy_per_site'][i,j]*n);reference_archive='results/baseline/grid_n8.npz'
  else:
   r=record(n,k,h);state=np.load(ROOT/r['archive'])['state'];target=np.r_[r['correlations'],r['structure_factor'],r['mx']];energy=r['energy'];reference_archive=r['archive']
  m2=float(abs(state)**2@m**2);binder=1-float(abs(state)**2@m**4)/(3*m2**2);(label,level,evidence),reference_roundoff=map_reference(n,k,h,dict(structure_factor=target[n:2*n],mx=target[-1]),binder);qualities={}
  for method in ['B3',new]:
   arm=load(k,h,method,task='historical_map' if method=='B3' and task=='map' else task);s=arm['state'];v=vector(observations(s,n));de=float((np.vdot(s,h_action(s,n,k,h)).real-energy)/n);assert de>=-1e-9;fidelity=float(abs(np.vdot(state,s))**2);e=scores(v,target,n);op=de<=.001 and e['max_c']<=.02 and e['max_sf']<=.02 and e['mx_error']<=.02;qualities[method]=dict(delta_e=de,fidelity=fidelity,observable_pass=op,state_pass=fidelity>=.99,joint_pass=op and fidelity>=.99,source=arm['source_archive'])
  es=[]
  for entry in point['entries']:
   r=entry['record'];a=np.load(ROOT/r['archive']);wp=wall_estimates(r);exact=predict(a['exact'],n,wp);single=a['samples_100000'][0];mean=a['samples_100000'].mean(0);ws=wall_estimates(r,100000);pred_single=predict(single,n,None if ws is None else ws[0]);pred_mean=predict(mean,n,None if ws is None else ws.mean(0));es.append(dict(method=entry['method'],estimator=entry['estimator'],p=r['p'],exact=a['exact'],single_rep0_100k=single,mean32x100k=mean,standard_deviation32=np.std(a['samples_100000'],axis=0,ddof=1),predictions_exact=exact,predictions_single=pred_single,predictions_mean32=pred_mean,error_exact_ED=scores(a['exact'],target,n),MSE_ED_100k=float(np.mean((a['samples_100000']-target)**2)),MSE_own_p0_100k=float(np.mean((a['samples_100000']-a['own_clean'])**2)),archive=r['archive'],cost=r['cost'],preparation_quality=qualities[entry['method']]))
  rows.append(dict(n=n,kappa=k,h=h,reference_label=label,reference_level=level,reference_evidence=evidence,reference_roundoff=reference_roundoff,reference_archive=reference_archive,target=target,entries=es))
 dump(OUT/f'n8_maps/{task}_analysis.json',rows);print(task,len(rows),flush=True)
ks=sorted(map(float,old['kappa'])) if task=='map' else PLAN['atlas']['low_kappa'];hs=sorted(float(h) for h in old['h'] if h>0) if task=='map' else PLAN['atlas']['low_h'];domain=[min(ks),max(ks),min(hs),max(hs)];requested={(k,h) for k in ks for h in hs};executed={(r['kappa'],r['h']) for r in rows};dump(OUT/f'n8_maps/{task}_coverage.json',dict(requested_coordinates=len(requested),executed_coordinates=len(executed),missing_coordinates=sorted(requested-executed),coordinate_hash=uid(sorted(requested)),domain=domain));regions=dict(full=domain,low_field=[.4,.6,.01,.35],antiphase_transition_band=[.6,1,.2,.7]);summary={}
for name,region in regions.items():
 weights=cell_weights(ks,hs,domain,region);area=float(weights.sum());items={};covered=0
 for method,p,est in sorted({(e['method'],e['p'],e['estimator']) for r in rows for e in r['entries']}):
  totals={d:collections.defaultdict(float) for d in ['D1','D3','D4','D5']};mse=joint=covered=labelarea=0.;count=0
  for r in rows:
   e=next((e for e in r['entries'] if (e['method'],e['p'],e['estimator'])==(method,p,est)),None)
   if e is None:continue
   w=float(weights[ks.index(r['kappa']),hs.index(r['h'])]);covered+=w;count+=w>0;mse+=w*e['MSE_ED_100k'];joint+=w*e['preparation_quality']['joint_pass'];labelarea+=w*(r['reference_label'] is not None)
   for d,y in e['predictions_single'].items():totals[d][label_status(y,r['reference_label'])]+=w
  items[f'{method}_{p}_{est}']=dict(requested_coordinates_in_region=int(np.sum(weights>0)),executed_coordinates_in_region=count,requested_area=area,executed_area=covered,executed_area_fraction=covered/area if area else None,reference_label_area=labelarea,reference_label_coverage=labelarea/covered if covered else None,preparation_joint_pass_area_fraction=joint/covered if covered else None,MSE_ED_area_weighted=mse/covered if covered else None,single_rep0_label_area={d:dict(v) for d,v in totals.items()})
 summary[name]=dict(domain=region,intersection_area=area,methods=items)
dump(OUT/f'n8_maps/{task}_area_summary.json',summary);dump(OUT/f'n8_maps/{task}_cost_scope.json',dict(exact='Analytic simulated expectations, no shots',single='One saved rep0 at100k totalshots per coordinate/p/preparation/estimator',mean='Mean of32 repeats costs3.2million totalshots per coordinate/p/preparation/estimator; not presented as a100k map',domain=domain,area='Voronoi cell intersection area; low-resolution and refined maps assessed separately, never pooled by point count',reference='Only explicit R0/interior-extension labels; elsewhere continuous RN observables, no artificial truth labels'))
