"""Keep all proxy agreement counts alongside stricter physical-evidence coverage."""
import sys,argparse,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_observation_analysis import label_status
p=argparse.ArgumentParser();p.add_argument('--task',default='core');task=p.parse_args().task;data=json.loads((OUT/f'end_to_end/{task}_analysis.json').read_text());groups={}
for r in data:
 for entry in r['entries']:
  for budget in PLAN['measurement']['budgets']:
   samples=[s for s in entry['samples'] if s['budget']==budget]
   for detector in ['D1','D3','D4','D5']:
    key=(entry['method'],entry['estimator'],entry['p'],budget,detector);g=groups.setdefault(key,dict(coordinates=0,physical_labelled=0,RN_proxy_labelled=0,physical_counts=collections.Counter(),RN_proxy_counts=collections.Counter(),reference_levels=collections.Counter(),RN_proxy_attribution=collections.Counter()));g['RN_proxy_attribution'][entry['RN_proxy_attribution'][detector]]+=1;g['coordinates']+=1;g['physical_labelled']+=r['reference_label'] is not None;g['RN_proxy_labelled']+=r['RN_proxy_label'] is not None;g['reference_levels'][r['reference_scope']['legacy_reference_level']]+=1
    for s in samples:g['physical_counts'][s['reference_status'][detector]]+=1/len(samples);g['RN_proxy_counts'][s['RN_proxy_status'][detector]]+=1/len(samples)
rows=[dict(method=k[0],estimator=k[1],p=k[2],budget=k[3],detector=k[4],**v) for k,v in groups.items()]
dump(OUT/f'end_to_end/{task}_reference_scope_audit.json',dict(rows=rows,note='Both columns retain every requested/executed coordinate. Physical labels use independent R0/interior evidence; RN proxy labels retain v1 multi-N order/Binder/gap patterns. Better apparent accuracy after reducing label coverage is NOT treated as an algorithm improvement. Thirty-two repeats normalized within each coordinate.'))
print(task,len(rows),'scope comparison rows')
