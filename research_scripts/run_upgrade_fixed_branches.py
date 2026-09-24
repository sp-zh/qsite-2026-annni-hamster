import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scipy.signal import find_peaks
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
from annni.upgrade_detection import uhlmann_squared
O=OUT/'fixed_branches';O.mkdir(exist_ok=True);index=json.loads((OUT/'map/index.json').read_text());
shard=OUT/'map_shard_high_k/index.json'
if shard.exists():
 combined={(r['kappa'],r['h']):r for r in json.loads(shard.read_text())}
 combined.update({(r['kappa'],r['h']):r for r in index});index=list(combined.values())
assert all(sum(abs(r['kappa']-k)<1e-12 for r in index)==20 for k in [0,.3,.8]),'Wait until all three slices are present'
rows=[];curves=[];peaks=[];t=time.perf_counter()
for k in [0,.3,.8]:
 for anchor in [.5,1.]:
  source=next(p['methods']['B3'] for p in index if abs(p['kappa']-k)<1e-12 and abs(p['h']-anchor)<1e-12);s=source['selected'];prepared=[]
  for h in np.arange(1,21)/10:
   h=float(h);uid=hashlib.sha256(json.dumps(dict(source=source['sha256'],k=k,h=h,code=sha(Path(__file__))),sort_keys=True).encode()).hexdigest();meta=O/(uid+'.json');archive=O/(uid+'.npz')
   if meta.exists():
    row=json.loads(meta.read_text());assert row['sha256']==sha(archive)
   else:
    fit,state=optimize_words(8,k,h,source['ref'],s['words'],np.array(s['params']));m,o,ed=assess(state,8,k,h);g=compile_circuit(8,source['ref'],s['words'],fit.x);selected=dict(params=fit.x.tolist(),words=s['words'],**resources(g,8),**m)
    np.savez_compressed(archive,initial=s['params'],params=fit.x,state=state,ed_state=ed,**o);row=dict(n=8,kappa=k,h=h,anchor_h=anchor,ref=source['ref'],source=source['archive'],source_sha256=source['sha256'],source_code_sha=sha(Path(__file__)),selected=selected,**m,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),optimizer_success=bool(fit.success),nfev=int(fit.nfev),initialization='same anchor parameters at every h, fixed structure; no ED selection',disposition='newly_executed');dump(meta,row)
   prepared.append(row);rows.append(row)
  for p in [0,.01,.05]:
   density_rows=[noise_record(row,p,keep=True) for row in prepared];rho=[np.load(ROOT/r['archive'])['rho'] for r in density_rows];v=np.array([vector(observations(r,8)) for r in rho]);hs=np.array([r['h'] for r in prepared]);quality=np.array([r['joint_pass'] for r in prepared])
   for stride in [1,2,4]:
    ids=np.arange(0,20,stride);x=hs[ids];vv=v[ids];rr=[rho[i] for i in ids];f=np.array([uhlmann_squared(a,b) for a,b in zip(rr[:-1],rr[1:])]);mid=(x[:-1]+x[1:])/2;valid=quality[ids[:-1]]&quality[ids[1:]];data=dict(change=np.linalg.norm(np.diff(vv,axis=0),axis=1)/np.diff(x),mx=np.abs(np.diff(vv[:,-1]))/np.diff(x),chi=-np.log(np.maximum(f,1e-300))/np.diff(x)**2)
    curves.append(dict(kappa=k,anchor_h=anchor,p=p,stride=stride,h_mid=mid.tolist(),h=x.tolist(),quality=quality[ids].tolist(),structure_identity=dict(ref=source['ref'],words=s['words']),**{q:a.tolist() for q,a in data.items()}))
    for metric,y in data.items():
     for j in find_peaks(y)[0]:peaks.append(dict(kappa=k,anchor_h=anchor,p=p,stride=stride,metric=metric,h=float(mid[j]),value=float(y[j]),support=[float(x[j]),float(x[j+1])],both_prep_pass=bool(valid[j]),endpoint=False,step=float(.1*stride),smoothing=None))
  dump(O/'index.json',rows);dump(O/'curves.json',curves);dump(O/'peaks.json',peaks);print(k,anchor,len(rows),round(time.perf_counter()-t,2),flush=True)
