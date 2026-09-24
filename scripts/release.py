"""Self-contained release operations. Historical data are read-only; outputs go to build/."""
import os,sys,json,csv,hashlib,platform,time,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# Clean-room audit: forbid historical workspace I/O except the declared installed environment.
if os.environ.get('ANNNI_FORBID_HISTORY'):
 forbidden=Path(os.environ['ANNNI_FORBID_HISTORY']).resolve()
 allowed=[ROOT,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()]
 def history_guard(event,args):
  if event not in ('open','os.listdir','os.scandir') or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
  p=Path(os.fsdecode(args[0])).absolute()
  if p.is_relative_to(forbidden) and not any(p.is_relative_to(a) for a in allowed):raise PermissionError('CLEAN_ROOM_FORBIDDEN_HISTORY: '+str(p))
 sys.addaudithook(history_guard)

os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/matplotlib'))
import numpy as np
from annni.upgrade_gates import compile_circuit,evolve,density,observations,vector,resources,geometry,h_action
from annni.upgrade_mitigation import estimated_vector,RICHARDSON,measurement_probs
F='results/stage6_followup_v1'
def path(rel):
 p=(ROOT/rel).resolve()
 if not p.is_relative_to(ROOT):raise ValueError('Input escapes release root: '+str(p))
 if not p.is_file():raise FileNotFoundError(p)
 return p
def read(rel):return json.loads(path(rel).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=lambda a:a.item() if isinstance(a,np.generic) else a.tolist() if isinstance(a,np.ndarray) else str(a)))
def env():
 import scipy
 return dict(python=platform.python_version(),python_build=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),machine=platform.machine(),bit_generator=type(np.random.default_rng().bit_generator).__name__)
def records():return [(rel,read(rel)) for rel in read('data/core/active_measurements.json')]
def samples_from_counts(r,a):
 """All repeats; joint probabilities preserve C/Mx/parity covariance, no fresh RNG."""
 counts=a['counts'];_,z,_=geometry(8);parity=np.prod(z,axis=1);off=0;vs=[]
 for s in r['settings']:
  d={b:counts[:,off+i,:]/num for i,(b,num) in enumerate(zip(s['bases'],s['allocations']))};off+=len(s['bases'])
  pz=d['Z'*8];px=d['X'*8]
  pair=np.einsum('ri,ij,ik->rjk',pz,z,z,optimize=True);mx=(px@z).mean(-1)
  if r['method']=='sv':
   P=px@parity;den=1+P;op=np.tile(np.eye(8),(len(P),1,1))*P[:,None,None]
   for i in range(8):
    for j in range(i+1,8):
     b=['X']*8;b[i]=b[j]='Y';op[:,i,j]=op[:,j,i]=-(d[''.join(b)]@parity)
   pair=(pair+op)/den[:,None,None];mx=(mx+(px@(parity[:,None]*z)).mean(-1))/den
  c=np.array([np.mean([pair[:,i,(i+k)%8] for i in range(8)],axis=0) for k in range(8)]).T
  v=np.column_stack([c,np.fft.fft(c,axis=1).real/8,mx])
  if r['method']=='sv':v[den<=.05]=np.nan
  vs.append(v)
 return np.einsum('f,frj->rj',RICHARDSON,np.array(vs)) if len(vs)==3 else vs[0]
def statistics(out):
 rows=list(csv.DictReader(path('results/stage4_upgrade_v1/matched_grid.csv').open()));rows=[r for r in rows if r['method']=='B3']
 b=[]
 for p in [0,.01,.05]:
  a=[r for r in rows if float(r['p'])==p]
  assert len(a)==420
  b.append(dict(p=p,n=420,B0_median_CNOT=float(np.median([float(r['old_cnots']) for r in a])),B3_median_CNOT=float(np.median([float(r['new_cnots']) for r in a])),B0_joint_pass=sum(r['old_pass']=='True' for r in a),B3_joint_pass=sum(r['new_pass']=='True' for r in a),B0_mean_max_C_error=float(np.mean([float(r['epsilon_c_old']) for r in a])),B3_mean_max_C_error=float(np.mean([float(r['epsilon_c_new']) for r in a])),B3_better=sum(float(r['epsilon_c_new'])<float(r['epsilon_c_old']) for r in a)))
 inputs=read(F+'/inputs.json');B={r['point_id'] for r in read(F+'/B_index.json')};groups={};per=[]
 for rel,r in records():
  if r['point_id'] not in B or (r['mode']=='equal_shots' and r['budget']!=100000):continue
  with np.load(path(r['archive'])) as a:
   target=np.load(path(inputs[r['point_id']]['archive']))['ed'];d=a['samples']-target;own=a['samples']-a['own_clean'];exact=a['exact'];sm=a['samples']-exact
   v=dict(point_id=r['point_id'],p=r['p'],mode=r['mode'],budget=r['budget'],method=r['method'],MSE_ED=float(np.mean(d*d)),MSE_own_p0=float(np.mean(own*own)),bias_squared=float(np.mean((exact-target)**2)),sampling_MSE=float(np.mean(sm*sm)),shots=r['shots_per_repeat'],G=r['CNOT_shots_per_repeat'],settings=r['measurement_settings'],labelled=inputs[r['point_id']]['label'] is not None)
  per.append(v);groups.setdefault((r['mode'],r['budget'],r['p'],r['method']),[]).append(v)
 eq=[]
 for (mode,budget,p,method),rs in sorted(groups.items()):
  assert len(rs)==45
  q=dict(mode=mode,budget=budget,p=p,method=method,n=len(rs),labelled=sum(x['labelled'] for x in rs))
  for key in ['MSE_ED','MSE_own_p0','bias_squared','sampling_MSE','shots','G','settings']:q[key]=float(np.mean([x[key] for x in rs]))
  eq.append(q)
 paired=[]
 for mode,budget,p in sorted({(r['mode'],r['budget'],r['p']) for r in per}):
  a=[r for r in per if (r['mode'],r['budget'],r['p'])==(mode,budget,p)];rr={r['point_id']:r for r in a if r['method']=='raw'}
  for m in ['zne_quadratic','sv']:
   xx=[r for r in a if r['method']==m];paired.append(dict(mode=mode,budget=budget,p=p,method=m,n=45,better=sum(r['MSE_ED']<rr[r['point_id']]['MSE_ED'] for r in xx),worse=sum(r['MSE_ED']>rr[r['point_id']]['MSE_ED'] for r in xx)))
 conf=list(csv.DictReader(path('results/stage6_v1/confirmation/confirmation_all_selected.csv').open()));n12=list(csv.DictReader(path('results/stage6_v1/n12_transfer/n12_all_selected.csv').open()));extensions=[]
 for cohort,rs in [('low_field_confirmation',[r for r in conf if r['region']=='low_field']),('confirmation',conf),('n12',n12)]:
  for method in ['B3','H6']:
   a=[r for r in rs if r['method']==method]
   if a:extensions.append(dict(cohort=cohort,method=method,n=len(a),candidate_exists=sum(r['candidate_pool_exists']=='True' for r in a),joint_pass=sum(r['joint_pass']=='True' for r in a),observable_pass=sum(r['observable_pass']=='True' for r in a),median_CNOT=float(np.median([float(r['cnots']) for r in a])),nfev=sum(float(r['search_nfev']) for r in a)))
 result=dict(scope='Recomputed from archived numerical rows and saved joint-count estimates; no new scientific runs',b0_b3=b,equal_resource=eq,paired=paired,extensions=extensions,windows=read(F+'/window_completion/coverage.json'),floating=read('results/stage6_v1/floating_boundary_scan/interval_evidence_v4.json'),denominators=dict(active_records=len(read('data/core/active_measurements.json')),active_coordinates=len({r['point_id'] for _,r in records()}),B_coordinates=len(B),A_coordinates=len(read(F+'/A_index.json')),repeats=32,excluded_attempt_records=648))
 dump(out/'release_statistics.json',result)
 flat=[]
 def walk(x,prefix=''):
  if isinstance(x,dict):
   for k,v in x.items():walk(v,prefix+'/'+str(k))
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,prefix+'/'+str(i))
  else:flat.append((prefix,x))
 walk(result)
 with (out/'release_statistics.csv').open('w') as f:w=csv.writer(f);w.writerow(['metric_path','value']);w.writerows(flat)
 return result

def verify_data(out):
 t=time.perf_counter();manifest=ROOT/'package_manifest.json';hashed=0
 if manifest.exists():
  for rel,h in read('package_manifest.json')['files'].items():assert sha(path(rel))==h,rel;hashed+=1
 inputs=read(F+'/inputs.json');rs=records();assert len(rs)==2718
 B={r['point_id'] for r in read(F+'/B_index.json')};assert len(B)==45
 assert len({r['point_id'] for _,r in rs})==110
 metric={r['archive']:r for r in read(F+'/equal_gate_budget/point_metrics.json')};equal={};reps=0
 for rel,r in rs:
  a_path=path(r['archive']);assert sha(a_path)==r['sha256']
  row=inputs[r['point_id']];assert (row['kappa'],row['h'])==(r['kappa'],r['h'])
  for s,pr in zip(r['settings'],r['probabilities']):
   expected=[g for g in row['gates'] for _ in range(s['fold'] if g[0]=='CNOT' else 1)]
   assert expected==pr['key']['gates'];assert pr['p']==r['p'];assert resources(expected,8)['cnots']==pr['cnots']==pr['noise_channels']
   assert sha(path(pr['archive']))==pr['sha256']
  with np.load(a_path) as a:
   alloc=[x for s in r['settings'] for x in s['allocations']];np.testing.assert_array_equal(a['counts'].sum(-1),np.tile(alloc,(32,1)))
   v=samples_from_counts(r,a);np.testing.assert_allclose(v,a['samples'],atol=2e-12,rtol=2e-12,equal_nan=True)
   target=np.load(path(row['archive']))['ed'];mse=float(np.mean((v-target)**2));np.testing.assert_allclose(mse,metric[r['archive']]['MSE_ED'],atol=2e-12,rtol=2e-12)
   reps+=len(v)
  G=sum(sum(s['allocations'])*p['cnots'] for s,p in zip(r['settings'],r['probabilities']));assert G==r['CNOT_shots_per_repeat']
  if r['mode']=='equal_gate':equal.setdefault((r['point_id'],r['p'],r['budget']),[]).append(G)
 assert len(equal)==270 and all(len(g)==3 and len(set(g))==1 for g in equal.values())
 refs=read(F+'/window_reference.json');assert len(refs)==6 and sum(r['frozen_reference']['resolvable'] for r in refs)==5
 # Reconstruct original420-point error comparison from saved observables, no new evolution.
 baseline=np.load(path('results/baseline/grid_n8.npz'));old=read('results/stage3_v1/grid/observations.json');new=read('results/stage4_upgrade_v1/map/noise_index.json');lookup={(r['kappa'],r['h'],r['p']):r for r in old}
 table=[r for r in csv.DictReader(path('results/stage4_upgrade_v1/matched_grid.csv').open()) if r['method']=='B3']
 keyed={(float(r['kappa']),float(r['h']),float(r['p'])):r for r in table}
 for pt in new:
  i=int(np.argmin(abs(baseline['kappa']-pt['kappa'])));j=int(np.argmin(abs(baseline['h']-pt['h'])));target=baseline['correlations'][i,j]
  for r in pt['methods']['B3']:
   key=(pt['kappa'],pt['h'],r['p']);b=lookup[key];tab=keyed[key]
   for rec,col in [(r,'epsilon_c_new'),(b,'epsilon_c_old')]:
    vals=np.load(path(rec['archive']))['correlations'];np.testing.assert_allclose(max(abs(vals-target)),float(tab[col]),atol=2e-12,rtol=2e-12)
 for row in read('data/core/b3_map_circuits.json'):
  pp=row['parameters'];gg=compile_circuit(8,row['reference'],pp['words'],pp['params']);assert [list(g) for g in gg]==row['gates'];assert resources(gg,8)['cnots']==pp['cnots']
 result=dict(status='PASS',environment=env(),matched_noisy_observable_records=2520,all420_gate_tables_recompiled=True,manifest_files=hashed,active_records=len(rs),saved_repeat_estimates_reconstructed=reps,equal_G_groups=len(equal),requested_windows=6,reference_resolvable=5,tolerance=2e-12,seconds=time.perf_counter()-t,random_resampling=False)
 dump(out/'verify_data.json',result);return result

def physics(out,sdk=False):
 t=time.perf_counter();inputs=read(F+'/inputs.json');rs=records()
 r=next(r for _,r in rs if r['p']==.01 and r['method']=='raw' and r['disposition']=='newly_executed')
 row=inputs[r['point_id']];par=row['selected_parameters'];g=compile_circuit(8,row['reference'],par['words'],par['params']);assert [list(x) for x in g]==row['gates']
 a=np.load(path(row['archive']));s=evolve(g,8);np.testing.assert_allclose(s,a['state'],atol=2e-10,rtol=0)
 rho0=density(g,8,0);np.testing.assert_allclose(rho0,np.outer(s,s.conj()),atol=2e-10,rtol=0)
 rho=density(g,8,.01);pr=r['probabilities'][0];probs=np.load(path(pr['archive']));errors=[]
 for i,b in enumerate(pr['bases']):
  fresh=measurement_probs(rho,b);np.testing.assert_allclose(fresh,probs['p'+str(i)],atol=2e-10,rtol=0);errors.append(float(np.max(abs(fresh-probs['p'+str(i)]))))
 assert abs(np.trace(rho)-1)<2e-10 and np.max(abs(rho-rho.conj().T))<2e-10 and np.linalg.eigvalsh(rho).min()>-2e-10
 o=vector(observations(s,8));np.testing.assert_allclose(o[8:16],np.fft.fft(o[:8]).real/8,atol=2e-10)
 e=float(np.vdot(s,h_action(s,8,row['kappa'],row['h'])).real);np.testing.assert_allclose(e,8*(-o[1]+row['kappa']*o[2]-row['h']*o[16]),atol=2e-10)
 # Distinct computational-basis bits check wire0 is MSB.
 for j in [0,3,7]:assert np.argmax(abs(evolve([('X',j)],8)))==1<<(7-j)
 sdk_status='NOT_REQUESTED'
 if sdk:
  import pennylane as qml
  @qml.qnode(qml.device('default.mixed',wires=8,shots=None))
  def q(p):
   for gate in g:
    name=gate[0]
    if name=='CNOT':qml.CNOT(wires=gate[1:3]);qml.DepolarizingChannel(p,wires=gate[2])
    elif name=='H':qml.Hadamard(wires=gate[1])
    elif name=='X':qml.PauliX(wires=gate[1])
    elif name=='RX':qml.RX(gate[2],wires=gate[1])
    elif name=='RZ':qml.RZ(gate[2],wires=gate[1])
    else:raise ValueError(gate)
   return qml.state()
  np.testing.assert_allclose(q(.01),rho,atol=2e-10,rtol=0);np.testing.assert_allclose(q(0),rho0,atol=2e-10,rtol=0);sdk_status='PASS PennyLane '+qml.__version__
 result=dict(status='PASS',environment=env(),point=[row['kappa'],row['h']],parameters_to_gates=True,cnots=resources(g,8)['cnots'],target_counts=resources(g,8)['target_counts'],p=[0,.01],energy_p0=e,probability_max_error=max(errors),atol=2e-10,SDK=sdk_status,seconds=time.perf_counter()-t)
 dump(out/'verify_physics.json',result);return result

def exact_replay(out):
 contract=read('provenance/replay_contract.json');current=env();mismatch={k:dict(expected=v,actual=current.get(k)) for k,v in contract['environment'].items() if current.get(k)!=v}
 for rel,h in contract['input_hashes'].items():assert sha(path(rel))==h,rel
 if mismatch:
  r=dict(status='SKIPPED_ENV_MISMATCH',mismatch=mismatch,environment=current,root_cause='Not isolated; cannot attribute historical external failure to one library.');dump(out/'verify_exact_replay.json',r);return r
 r=read(contract['measurement'])
 assert r['key']['code']==sha(path('annni/stage6_followup.py'))
 assert r['key']['estimator']==sha(path('annni/upgrade_mitigation.py'))
 assert r['key']['seed']==read(F+'/config.json')['seed']
 for pr in r['probabilities']:
  assert pr['key']['backend']==sha(path('annni/upgrade_gates.py'))
  assert pr['key']['measurement_code']==sha(path('annni/stage5_measurement_groups.py'))
 a=np.load(path(r['archive']));checked=0
 for rep in [0,1,31]:
  offset=0
  for setting,pr in zip(r['settings'],r['probabilities']):
   d=np.load(path(pr['archive']))
   for i,(basis,num) in enumerate(zip(setting['bases'],setting['allocations'])):
    identity=dict(key=r['key'],repeat=rep,fold=setting['fold'],basis=basis)
    uid=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    seed=np.random.SeedSequence([r['key']['seed'],*np.frombuffer(bytes.fromhex(uid),dtype='<u4').tolist()])
    fresh=np.random.default_rng(seed).multinomial(num,d['p'+str(i)])
    np.testing.assert_array_equal(fresh,a['counts'][rep,offset+i]);checked+=1
   offset+=len(setting['bases'])
 result=dict(status='PASS',scope='One frozen record, repeats0/1/31, every setting; not universal cross-environment replay',environment=current,settings_replayed=checked,archived_key_used_verbatim=True)
 dump(out/'verify_exact_replay.json',result);return result

def redraw(out):
 from release_figures import draw
 return draw(out,statistics(out))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['statistics','verify-data','verify-physics','verify-exact-replay','redraw']);ap.add_argument('--out',default='build');ap.add_argument('--quick',action='store_true');ap.add_argument('--sdk',action='store_true');a=ap.parse_args();out=(ROOT/a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 result={'statistics':lambda:statistics(out),'verify-data':lambda:verify_data(out),'verify-physics':lambda:physics(out,a.sdk),'verify-exact-replay':lambda:exact_replay(out),'redraw':lambda:redraw(out)}[a.action]();print(json.dumps(result,indent=2)[:6000])
if __name__=='__main__':main()
