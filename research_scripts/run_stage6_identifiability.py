"""Full-state binary diagnosis; templates are never passed to deployment detectors."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_noise import physical
from annni.stage6_distinguish import distances,likelihood_errors
from annni.stage6_detector import predict
from annni.stage6_wall_features import features,predict as wall_predict
f=json.loads((OUT/'confirmation/method_frozen.json').read_text());pairs=json.loads((OUT/'noise_diagnosability/pairs.json').read_text())['pairs'];rows=[]
for i,pair in enumerate(pairs):
 for method in ['B3',f['physical_method']]:
  arms=[load(x['kappa'],x['h'],method,task=x['source_task']) for x in [pair['a'],pair['b']]]
  for p in [0,.01,.05]:
   guard();start=time.perf_counter();rs=[physical(a,p,keep=True)[1] for a in arms];key=dict(pair=pair,method=method,p=p,sources=[r['sha256'] for r in rs],code=sha(__file__),binary_code=sha(ROOT/'annni/stage6_distinguish.py'),frozen_sha=sha(OUT/'confirmation/method_frozen.json'));base=OUT/'noise_diagnosability/pair_cache'/uid(key);meta=base.with_suffix('.json')
   if meta.exists():row=json.loads(meta.read_text());assert sha(ROOT/row['counts_archive'])==row['counts_sha256']
   else:
    arrays=[np.load(ROOT/r['archive']) for r in rs];d,pa,pb=distances(*[a['rho'] for a in arrays]);seed=np.random.SeedSequence([6201,*np.frombuffer(bytes.fromhex(uid(dict(pair=pair,method=method,p=p))),dtype='<u4').tolist()]);children=seed.spawn(3);diagnostics=[];counts={}
    for budget,s in zip([10000,100000,1000000],children):
     value=likelihood_errors(pa,pb,budget,s);counts[f'counts_{budget}']=value.pop('counts');value.update(seed_entropy=s.entropy,seed_spawn_key=s.spawn_key);diagnostics.append(value)
    predictions=[]
    for a,ps in zip(arrays,[pa,pb]):
     v=a['observables'];predictions.append(dict(D4=predict(v,f['detectors']['8']),D5=wall_predict(features(ps[0],v[-1],8),f['wall_detectors']['8'])))
    base.parent.mkdir(exist_ok=True);archive=base.with_suffix('.npz');np.savez_compressed(archive,probabilities_A=pa,probabilities_B=pb,**counts)
    row=dict(key=key,pair_index=i,pair=pair,method=method,p=p,**d,oracle_measurement=diagnostics,compressed_feature_l2=float(np.linalg.norm(arrays[0]['observables']-arrays[1]['observables'])),predictions=predictions,probability_records=rs,seconds=time.perf_counter()-start,counts_archive=str(archive.relative_to(ROOT)),counts_sha256=sha(archive),counts_order='First32 queries from A, next32 from B; axis1 Z/X setting; bitstrings wire0 MSB',disposition='newly_executed');dump(meta,row)
   rows.append(row);dump(OUT/'noise_diagnosability/identifiability.json',rows);print(i,method,p,row['trace_distance'],row['xz_joint_total_variation'],flush=True)
 progress('identifiability',len(rows),'.venv/bin/python scripts/run_stage6_identifiability.py',pairs_completed=i+1)
