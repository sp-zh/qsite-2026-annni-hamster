"""Same-coordinate counterparts for actual adaptive structure switches on 3 slices."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
O=OUT/'branches';O.mkdir(exist_ok=True);index=json.loads((OUT/'map/index.json').read_text());
shard=OUT/'map_shard_high_k/index.json'
if shard.exists():
 combined={(r['kappa'],r['h']):r for r in json.loads(shard.read_text())}
 combined.update({(r['kappa'],r['h']):r for r in index});index=list(combined.values())
assert all(sum(abs(r['kappa']-k)<1e-12 for r in index)==20 for k in [0,.3,.8]),'Wait until all three slices are present'
rows=[];t=time.perf_counter()
def counterpart(source,k,h):
 key=dict(source=source['sha256'],kappa=k,h=h,params=source['selected']['params'],words=source['selected']['words'],fp=fp(),protocol='fixed structure reoptimization at opposite endpoint, same source initial parameters')
 uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();meta=O/(uid+'.json');archive=O/(uid+'.npz')
 if meta.exists():
  r=json.loads(meta.read_text());assert r['key']==key and sha(archive)==r['sha256'];return r
 s=source['selected'];start=time.perf_counter();fit,state=optimize_words(8,k,h,source['ref'],s['words'],np.array(s['params']));met,obs,ed=assess(state,8,k,h);g=compile_circuit(8,source['ref'],s['words'],fit.x);selected=dict(params=fit.x.tolist(),words=s['words'],**resources(g,8),**met)
 np.savez_compressed(archive,params=fit.x,initial=s['params'],state=state,ed_state=ed,**obs)
 row=dict(key=key,n=8,kappa=k,h=h,ref=source['ref'],selected=selected,**met,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),seconds=time.perf_counter()-start,optimizer_success=bool(fit.success),nfev=int(fit.nfev),disposition='newly_executed');dump(meta,row);return row
for k in [0,.3,.8]:
 points=sorted([p for p in index if abs(p['kappa']-k)<1e-12],key=lambda p:p['h'])
 for left,right in zip(points[:-1],points[1:]):
  a=left['methods']['B3'];b=right['methods']['B3'];ida=(a['ref'],a['selected']['words']);idb=(b['ref'],b['selected']['words']);switched=ida!=idb
  row=dict(kappa=k,left_h=left['h'],right_h=right['h'],actual_structure_switch=switched,actual_switch_pair_checked=False,opposite_direction_checked=False,endpoints=[])
  if switched:
   bl=counterpart(b,k,left['h']);ar=counterpart(a,k,right['h'])
   for h,paira,pairb in [(left['h'],a,bl),(right['h'],ar,b)]:
    comparisons=[]
    for p in [0,.01,.05]:
     ra=noise_record(paira,p);rb=noise_record(pairb,p);va=np.load(ROOT/ra['archive']);vb=np.load(ROOT/rb['archive']);diff=vector(dict(correlations=va['correlations'],structure_factor=va['structure_factor'],mx=float(va['mx'])))-vector(dict(correlations=vb['correlations'],structure_factor=vb['structure_factor'],mx=float(vb['mx'])))
     comparisons.append(dict(p=p,difference=diff.tolist(),sensitive=bool(max(abs(diff))>.02),a_archive=ra['archive'],b_archive=rb['archive'],a_sha256=ra['sha256'],b_sha256=rb['sha256']))
    row['endpoints'].append(dict(h=h,a_state_archive=paira['archive'],b_state_archive=pairb['archive'],a_params_sha=paira['sha256'],b_params_sha=pairb['sha256'],both_prep_pass=paira['joint_pass'] and pairb['joint_pass'],comparisons=comparisons))
   row['actual_switch_pair_checked']=True
  rows.append(row);dump(O/'index.json',rows)
 print(k,len(rows),round(time.perf_counter()-t,2),flush=True)
