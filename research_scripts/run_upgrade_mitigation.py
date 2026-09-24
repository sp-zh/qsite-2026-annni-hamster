import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_noise import *
from annni.upgrade_mitigation import *
O=OUT/'mitigation';O.mkdir(exist_ok=True);points=list(PLAN['mitigation_points'])
for k,hs in PLAN['mitigation_windows']:
 for h in hs:
  if [k,h] not in points:points.append([k,h])
rows=[];t=time.perf_counter()
for pi,(k,h) in enumerate(points):
 row=select([adaptive(8,k,h,ref,11,128,group='mitigation') for ref in PLAN['refs']]);s=row['selected'];cn=s['cnots'];v0=vector(observations(np.load(ROOT/row['archive'])['state'],8));ved=vector(observations(np.load(ROOT/row['archive'])['ed_state'],8))
 for p in [.01,.05]:
  name=f'k{k:.3f}_h{h:.3f}_p{p:.2f}';meta=O/(name+'.json');archive=O/(name+'.npz');key=dict(row_sha=row['sha256'],p=p,code=sha(ROOT/'annni/upgrade_mitigation.py'),runner=sha(Path(__file__)))
  if meta.exists():
   r=json.loads(meta.read_text());assert r['key']==key and r['sha256']==sha(archive);rows.append(r);continue
  rhos=[];vs=[];probs=[]
  for fold in [1,3,5]:
   nr=noise_record(row,p,fold,keep=True);rho=np.load(ROOT/nr['archive'])['rho'];rhos.append(rho);vs.append(vector(observations(rho,8)));probs.append(groups(rho) if fold==1 else {b:measurement_probs(rho,b) for b in ['Z'*8,'X'*8]})
  algebra_check(rhos[0]);vsv,den=estimated_vector(probs[0],8,True);bias=dict(raw=vs[0]-v0,zne=LINEAR@np.array(vs)-v0,richardson=RICHARDSON@np.array(vs)-v0,sv=vsv-v0);samples={};stats={};costs={}
  for budget in PLAN['mitigation_shots']:
   accum={m:[] for m in ['raw','zne','sv']};rng=np.random.default_rng(np.random.SeedSequence([2026,pi,round(p*1000),budget]))
   for rep in range(PLAN['mitigation_replicates']):
    v,c=sample_estimate(probs[0],8,budget,rng);accum['raw'].append(v);costs[f'raw_{budget}']=c|dict(gate_shots=budget*cn)
    v,c=sample_estimate(probs[0],8,budget,rng,True);accum['sv'].append(v);costs[f'sv_{budget}']=c|dict(gate_shots=budget*cn,measurement_extra_cnots=0,measurement_single_qubit_rotations=sum(b!='Z' for word in probs[0] for b in word))
    alloc=np.array([budget//3]*3);alloc[:budget%3]+=1;v=[]
    for dist,b in zip(probs,alloc):a,_=sample_estimate(dist,8,int(b),rng);v.append(a)
    accum['zne'].append(LINEAR@v);costs[f'zne_{budget}']=dict(shots=int(sum(alloc)),scale_allocations=alloc.tolist(),groups=6,gate_shots=int(np.dot(alloc,[1,3,5])*cn))
   for method,vals in accum.items():
    a=np.array(vals);samples[f'{method}_{budget}']=a;stats[f'{method}_{budget}']=dict(bias=(a.mean(0)-v0).tolist(),variance=a.var(0,ddof=1).tolist(),mse=np.mean((a-v0)**2,axis=0).tolist(),replicates=len(a),max_bias=float(max(abs(a.mean(0)-v0))),mean_mse=float(np.mean((a-v0)**2)))
  np.savez_compressed(archive,ideal=v0,ed=ved,raw_scale_observables=vs,sv=vsv,zne=LINEAR@vs,richardson=RICHARDSON@vs,**samples)
  r=dict(key=key,kappa=k,h=h,p=p,cnots=cn,preparation_pass=row['joint_pass'],selected_archive=row['archive'],archive=str(archive.relative_to(ROOT)),sha256=sha(archive),unclipped=True,zne_coefficients=LINEAR.tolist(),richardson_coefficients=RICHARDSON.tolist(),variance_amplification_equal_scale_shots=float(LINEAR@LINEAR),sv_denominator=den,bias={m:v.tolist() for m,v in bias.items()},statistics=stats,costs=costs,disposition='newly_executed');dump(meta,r);rows.append(r)
 dump(O/'index.json',rows);print(pi+1,len(points),round(time.perf_counter()-t,2),flush=True)
