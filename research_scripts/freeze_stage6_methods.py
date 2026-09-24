"""Freeze before any confirmation results are read. Validation choices fully retained."""
import sys,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_detector import train,predict
from annni.stage6_reference import record
from annni.stage6_candidates import select
from annni.stage6_assess import assess_run
from annni.stage6_hybrid import low_field
from annni.upgrade_gates import vector
from annni.stage6_wall_features import pure_features,train as train_wall,predict as predict_wall
p=OUT/'confirmation/method_frozen.json'
if p.exists():raise SystemExit('Frozen methods retained')
import subprocess
subprocess.run([sys.executable,'scripts/compact_stage6_indices.py','--task','validation'],check=True)
dev=json.loads((OUT/'failure_mechanisms/development_assessment.json').read_text());val=json.loads((OUT/'failure_mechanisms/validation_assessment.json').read_text());assert len(dev)==36 and len(val)==24
rank=[]
for m in ['C1','C2','C3']:
 values=[x['methods'][m] for x in val];low=[x['methods'][m] for x in val if .4<=x['kappa']<=.6 and x['h']<=.15];rank.append(dict(method=m,low_pass=sum(x['joint_pass'] for x in low),all_pass=sum(x['joint_pass'] for x in values),mean_cnot=float(np.mean([x['cnots'] for x in values])),total_seconds=sum(x['total_seconds'] for x in values)))
rawval=[r for pth in (OUT/'domain_wall_candidates').glob('validation_*_index.json') for r in json.loads(pth.read_text())];hybrid_rank=[];hybrid_rows={}
for candidate in ['C2','C3']:
 values=[]
 for r in rawval:
  names=['C0',candidate] if low_field(r['kappa'],r['h']) else ['C0'];runs=[json.loads((ROOT/path).read_text()) for name in names for path in r['methods'][name]['runs']];chosen=select(runs);met=assess_run(chosen);values.append(dict(kappa=r['kappa'],h=r['h'],components=names,metrics=met,total_seconds=sum(x['seconds'] for x in runs),selected_source=chosen['archive']))
 hybrid_rows[candidate]=values;lo=[r for r in values if low_field(r['kappa'],r['h'])];hybrid_rank.append(dict(method=candidate,low_pass=sum(r['metrics']['joint_pass'] for r in lo),all_pass=sum(r['metrics']['joint_pass'] for r in values),mean_cnot=float(np.mean([r['metrics']['cnots'] for r in values])),total_seconds=sum(r['total_seconds'] for r in values)))
wall=min(hybrid_rank,key=lambda x:(-x['low_pass'],-x['all_pass'],x['mean_cnot'],x['total_seconds']))['method'];methods=['C1','H6']
detector_configs={};wall_configs={};validation_detector=[]
for n in [8,12]:
 refdev=json.loads((OUT/'reference_atlas/development_evaluation.json').read_text());trainvec=[];labels=[]
 for r in refdev:
  if r['label']:
   a=record(n,r['kappa'],r['h']);trainvec.append(np.r_[a['correlations'],a['structure_factor'],a['mx']]);labels.append(r['label'])
 cfg=train(trainvec,labels,n);refval=json.loads((OUT/'reference_atlas/validation_evaluation.json').read_text());options=[]
 for distance,margin in itertools.product([3.,5.,7.],[.2,.5]):
  c=dict(cfg,maximum_distance=distance,minimum_margin=margin);correct=wrong=rejected=0
  for r in refval:
   if not r['label']:continue
   a=record(n,r['kappa'],r['h']);y=predict(np.r_[a['correlations'],a['structure_factor'],a['mx']],c)['label'];correct+=y==r['label'];wrong+=y in ['ferro-like','antiphase-like','paramagnetic-like'] and y!=r['label'];rejected+=y in ['degraded','uncertain']
  options.append(dict(maximum_distance=distance,minimum_margin=margin,correct=correct,wrong=wrong,rejected=rejected))
 best=min(options,key=lambda x:(x['wrong'],-x['correct'],x['maximum_distance'],-x['minimum_margin']));detector_configs[str(n)]=dict(cfg,maximum_distance=best['maximum_distance'],minimum_margin=best['minimum_margin']);validation_detector.append(dict(n=n,options=options,selected=best))
for n in [8,12]:
 trainvals=[];labs=[]
 for r in json.loads((OUT/'reference_atlas/development_evaluation.json').read_text()):
  if r['label']:
   a=record(n,r['kappa'],r['h']);trainvals.append(pure_features(np.load(ROOT/a['archive'])['state'],n));labs.append(r['label'])
 cfg=train_wall(trainvals,labs,n);options=[]
 for distance,margin in itertools.product([3.,5.,7.],[.2,.5]):
  c=dict(cfg,maximum_distance=distance,minimum_margin=margin);correct=wrong=rejected=0
  for r in json.loads((OUT/'reference_atlas/validation_evaluation.json').read_text()):
   if not r['label']:continue
   a=record(n,r['kappa'],r['h']);y=predict_wall(pure_features(np.load(ROOT/a['archive'])['state'],n),c)['label'];correct+=y==r['label'];wrong+=y in ['ferro-like','antiphase-like','paramagnetic-like'] and y!=r['label'];rejected+=y in ['degraded','uncertain']
  options.append(dict(maximum_distance=distance,minimum_margin=margin,correct=correct,wrong=wrong,rejected=rejected))
 best=min(options,key=lambda x:(x['wrong'],-x['correct'],x['maximum_distance'],-x['minimum_margin']));wall_configs[str(n)]=dict(cfg,maximum_distance=best['maximum_distance'],minimum_margin=best['minimum_margin']);validation_detector.append(dict(n=n,detector='D5_wall_histogram',options=options,selected=best))
result=dict(timestamp=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),methods=methods,physical_method='H6',wall_component=wall,dispatch=dict(wall_kappa_interval=[.4,.6],wall_h_max=.35,threshold_roundoff_tolerance=1e-12,inside='C0 physical candidates UNION selected wall-component candidates; choose ONE circuit by energy/resource',otherwise='C0',reason='Pre-confirmation fixed regional construction: wall innovation targets low-field competition; matched-effort physical greedy elsewhere. Pure C2/C3 ablations retained in development/validation. This prevents costly unhelpful wall searches in far high-field controls; not oracle per-point selection.'),method_ranking=rank,hybrid_method_ranking=hybrid_rank,all_hybrid_validation=hybrid_rows,hybrid_code=sha(ROOT/'annni/stage6_hybrid.py'),runner_sha=sha(ROOT/'scripts/run_stage6_candidates.py'),candidate_code=sha(ROOT/'annni/stage6_candidates.py'),legacy_code=sha(ROOT/'annni/stage6_legacy.py'),detector_code=sha(ROOT/'annni/stage6_detector.py'),detectors=detector_configs,wall_detectors=wall_configs,wall_detector_code=sha(ROOT/'annni/stage6_wall_features.py'),detector_validation=validation_detector,selection='Energy window1e-6 per site then CNOT then energy; no hard symmetry gate; no ED at selection',method_rule='Carry C1 and H6 only. H6 generates C0 plus validation-selected wall candidates within fixed kappa[.4,.6],h<=.35; energy/resource selects one real circuit. Outside, C0 only. All added classical search is charged; no state averaging or ED selector. All component runs and hybrid validation outcomes retained. No confirmation-dependent routing.',validation_sha=sha(OUT/'failure_mechanisms/validation_assessment.json'),new_confirmation_seed=631,coordinate_sha=PLAN['coordinate_hash'],state_access_cost='Analytic statevector energy and gradients; no free final projection; D4 inference uses observable features only; D2 full-state comparisons separately costed')
result['hybrid_validation']=hybrid_rows[wall]
dump(p,result)
conf=PLAN['confirmation'];points=[dict(r) for r in conf[:48:4]]+[dict(r) for r in conf[48:72:2]]+[dict(r) for r in conf[72::2]];assert len(points)==36;dump(OUT/'n12_transfer/coordinates.json',points);print('Frozen',methods,rank)
