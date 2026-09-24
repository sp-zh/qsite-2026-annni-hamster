"""Same-coordinate counterparts for actual adaptive structure switches on 3 slices."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_noise import *
O=OUT/'end_to_end/branches_refined';O.mkdir(exist_ok=True);index=json.loads((OUT/'selector_benchmark/windows/index.json').read_text())+json.loads((OUT/'selector_benchmark/refined/index.json').read_text())
rows=[];t=time.perf_counter()
def counterpart(source,k,h):
 key=dict(source=source['sha256'],kappa=k,h=h,params=source['selected']['params'],words=source['selected']['words'],fp=fp(),protocol='fixed structure reoptimization at opposite endpoint, same source initial parameters')
 uid=hashlib.sha256(json.dumps(key,sort_keys=True).encode()).hexdigest();meta=O/(uid+'.json');archive=O/(uid+'.npz')
 if meta.exists():
  r=json.loads(meta.read_text());assert r['key']==key and sha(archive)==r['sha256'];return r
 s=source['selected'];start=time.perf_counter();fit,state=optimize_words(8,k,h,source['ref'],s['words'],np.array(s['params']),maxiter=2000);met,obs,ed=assess(state,8,k,h);g=compile_circuit(8,source['ref'],s['words'],fit.x);selected=dict(params=fit.x.tolist(),words=s['words'],**resources(g,8),**met)
 np.savez_compressed(archive,params=fit.x,initial=s['params'],state=state,ed_state=ed,**obs)
 row=dict(key=key,n=8,kappa=k,h=h,ref=source['ref'],selected=selected,**met,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),seconds=time.perf_counter()-start,optimizer_success=bool(fit.success),nfev=int(fit.nfev),disposition='newly_executed');dump(meta,row);return row
for k in [0,.3,.8]:
 points=sorted([p for p in index if abs(p['kappa']-k)<1e-12],key=lambda p:p['h'])
 for left,right in zip(points[:-1],points[1:]):
  a=left['B5'];b=right['B5'];ida=(a['ref'],a['selected']['words']);idb=(b['ref'],b['selected']['words']);switched=ida!=idb
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

# Fixed structure with continuous parameters; no branch projection or smoothing.
fixed=[]
for k,hs in PLAN['windows']:
 points=sorted([p for p in index if abs(p['kappa']-k)<1e-12],key=lambda p:p['h']);center=len(points)//2;anchor=points[center]['B5'];branches={center:anchor}
 for direction,indices in [('ascending',range(center+1,len(points))),('descending',range(center-1,-1,-1))]:
  previous=anchor
  for j in indices:
   previous=counterpart(previous,k,points[j]['h']);branches[j]=previous
 for j,row in sorted(branches.items()):
  fixed.append(dict(kappa=k,h=points[j]['h'],state=row,noise=[noise_record(row,p,keep=True) for p in [0,.01,.05]],protocol='Frozen center structure, energy-only continuation outward, maxiter2000'))
  dump(O/'fixed_index.json',fixed)
