import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.upgrade_detection import predict
O=OUT/'n8_maps';rows=json.loads((O/'noise_index.json').read_text());mit=json.loads((OUT/'end_to_end/full_best_index.json').read_text());raw_shots=json.loads((OUT/'end_to_end/full_raw_index.json').read_text());assert len(rows)==len(mit)==len(raw_shots)==420;raw_by={(r['kappa'],r['h']):r for r in raw_shots};ks=sorted(set(r['kappa'] for r in rows));hs=sorted(set(r['h'] for r in rows));cfg=json.loads((ROOT/'results/stage4_upgrade_v1/detection/frozen.json').read_text());classes=['ferro-like','antiphase-like','paramagnetic-like','uncertain','degraded'];branch=json.loads((OUT/'end_to_end/branches/index.json').read_text());prepared=np.zeros((len(ks),len(hs)),bool);unresolved=prepared.copy();obs=np.zeros((3,len(ks),len(hs),17));prep=np.zeros_like(obs);noise=np.zeros_like(obs);mitobs=np.zeros_like(obs);rawmean=np.zeros_like(obs);detlabels=np.zeros((3,len(ks),len(hs)),int);labels=np.zeros((2,3,len(ks),len(hs)),int);branch_checked=np.zeros_like(labels[0],bool);branch_sensitive=branch_checked.copy();records=[]
for point,mp in zip(sorted(rows,key=lambda r:(r['kappa'],r['h'])),sorted(mit,key=lambda r:(r['kappa'],r['h']))):
 k,h=point['kappa'],point['h'];assert abs(mp['kappa']-k)<1e-10 and abs(mp['h']-h)<1e-10;i=ks.index(k);j=hs.index(h);unresolved[i,j]=point['selection_unresolved']
 for z,p in enumerate([0,.01,.05]):
  r=next(r for r in point['B5'] if r['p']==p);a=np.load(ROOT/r['archive']);v=vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx'])));obs[z,i,j]=v;prep[z,i,j]=a['prep'];noise[z,i,j]=a['noise'];prepared[i,j]=r['prep_joint_pass'];detlabels[z,i,j]=classes.index(predict(v,cfg)['D1']);raw=next(e['record'] for e in raw_by[k,h]['entries'] if e['record']['p']==p);ra=np.load(ROOT/raw['archive']);rawmean[z,i,j]=ra['samples_100000'].mean(0);rawpred=raw['statistics']['100000']['D1'];labels[0,z,i,j]=int(np.argmax([rawpred.count(c) for c in classes]));m=next(e['record'] for e in mp['entries'] if e['record']['p']==p);a=np.load(ROOT/m['archive']);mitobs[z,i,j]=a['samples_100000'].mean(0);pred=m['statistics']['100000']['D1'];counts=[pred.count(c) for c in classes];labels[1,z,i,j]=int(np.argmax(counts));records.append(dict(kappa=k,h=h,p=p,method=m['method'],D1_counts=counts,anchor=m['anchor'],prep_pass=prepared[i,j].item()))
  for b in branch:
   if abs(b['kappa']-k)>1e-10:continue
   for ep in b['endpoints']:
    if abs(ep['h']-h)<1e-10:
     comp=next(c for c in ep['comparisons'] if c['p']==p);branch_checked[z,i,j]=True;branch_sensitive[z,i,j]|=comp['sensitive']
np.savez_compressed(O/'maps.npz',kappa=ks,h=hs,p=[0,.01,.05],q=2*np.pi*np.arange(8)/8,raw_observables=obs,epsilon_prep=prep,delta_noise=noise,mitigated_mean_100k=mitobs,raw_mean_100k=rawmean,D1_labels_deterministic=detlabels,D1_labels=labels,preparation_failed=~prepared,selection_unresolved=unresolved,branch_checked=branch_checked,branch_sensitive=branch_sensitive)
dump(O/'mitigated_predictions.json',dict(classes=classes,rows=records,layout='arrays [p,kappa,h,feature]; labels [raw_or_mitigated,p,kappa,h]; features C[0:N],SF[0:N],Mx',raw_and_mitigated_label='Both are mode of32 D1 labels at100k total shots; fixed class order breaks ties. Deterministic raw labels saved separately.',branch_scope='Only actually audited slice coordinates; unchecked is separate from insensitive'))
print('Exported full420 raw and mitigated maps')
