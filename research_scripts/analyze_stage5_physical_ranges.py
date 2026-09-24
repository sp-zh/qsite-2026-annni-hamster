import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
current_archives=set()
for name in ['validation','core','refined','full_best','full_raw','n12']:
 index=OUT/'end_to_end'/f'{name}_index.json'
 if not index.exists():continue
 for point in json.loads(index.read_text()):
  records=[point] if 'statistics' in point else [e['record'] for e in point['entries']]
  current_archives.update(r['archive'] for r in records)
rows=[]
for p in (OUT/'end_to_end/measurements').glob('*.json'):
 r=json.loads(p.read_text());a=np.load(ROOT/r['archive']);n=r['n']
 for budget in ['10000','100000']:
  v=a['samples_'+budget];bad_c=(abs(v[:,:n])>1+1e-12).any(1);bad_sf=((v[:,n:2*n]<-1e-12)|(v[:,n:2*n]>1+1e-12)).any(1);bad_mx=abs(v[:,-1])>1+1e-12;rows.append(dict(used_in_current_frozen_analysis=r['archive'] in current_archives,n=n,kappa=r['kappa'],h=r['h'],p=r['p'],method=r['method'],shots=int(budget),repetitions=32,nonphysical_C=int(sum(bad_c)),nonphysical_SF=int(sum(bad_sf)),nonphysical_Mx=int(sum(bad_mx)),any_nonphysical=int(sum(bad_c|bad_sf|bad_mx)),minimum_SF=float(v[:,n:2*n].min()),maximum_abs_C=float(abs(v[:,:n]).max()),archive=r['archive'],note='Supplementary complete physical-range audit; original runtime counter checked absolute bounds only. Raw values and estimator remain unchanged.'))
dump(OUT/'end_to_end/physical_range_audit.json',rows);print(len(rows))
