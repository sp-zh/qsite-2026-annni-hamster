"""Both existing ZNE fits on identical1/3/5 scale counts, no extra quantum data."""
from .stage6_common import *
from .stage6_noise_v2 import measured
from .upgrade_mitigation import RICHARDSON,estimated_vector

def measurement(row,p,method,budgets=None):
 if method!='zne_quadratic':return measured(row,p,method,budgets)
 base_record=measured(row,p,'zne',budgets);key=dict(source=base_record['sha256'],source_key=base_record['key'],estimator='existing_Richardson_1_3_5',code=sha(__file__));base=OUT/'end_to_end/measurements'/uid(key);meta=base.with_suffix('.json')
 if meta.exists():r=json.loads(meta.read_text());assert sha(ROOT/r['archive'])==r['sha256'];return r
 n=row['n'];source=np.load(ROOT/base_record['archive']);data={};exact=[];t=time.perf_counter()
 for r in base_record['probability_records']:
  a=np.load(ROOT/r['archive']);d={b:a[f'p{i}'] for i,b in enumerate(r['bases'])};exact.append(estimated_vector(d,n,False)[0])
 quality={}
 for btext,settings in base_record['sampling'].items():
  budget=int(btext);counts=source[f'counts_{budget}'];samples=[]
  for cc in counts:
   offset=0;v=[]
   for setting in settings:
    bs=setting['bases'];alloc=setting['allocations'];d={basis:cc[offset+i]/a for i,(basis,a) in enumerate(zip(bs,alloc))};offset+=len(bs);v.append(estimated_vector(d,n,False)[0])
   samples.append(RICHARDSON@np.array(v))
  v=np.array(samples);data[f'samples_{budget}']=v;data[f'covariance_{budget}']=np.cov(v,rowvar=False);quality[btext]=dict(denominators=None,nonfinite=int((~np.isfinite(v)).sum()),outside_range=int(np.sum((v[:,:n]<-1-1e-9)|(v[:,:n]>1+1e-9))),negative_structure_factor=int(np.sum(v[:,n:2*n]<-1e-9)),physical_comparison_tolerance=1e-9)
 archive=base.with_suffix('.npz');np.savez_compressed(archive,exact=RICHARDSON@np.array(exact),own_clean=source['own_clean'],**data)
 r=dict(base_record,key=key,method=method,archive=str(archive.relative_to(ROOT)),sha256=sha(archive),counts_archive=base_record['archive'],shared_quantum_data_with=base_record['archive'],quality=quality,seconds=time.perf_counter()-t,disposition='new_analysis_of_shared_ZNE_counts_no_additional_quantum_samples',coefficients=RICHARDSON.tolist(),unclipped=True);dump(meta,r);return r
