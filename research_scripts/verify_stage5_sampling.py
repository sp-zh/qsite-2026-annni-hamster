"""Check actual finite-shot RNG namespaces and cross-view reused measurement archives."""
import sys,json
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump
physical=defaultdict(list)
for p in (OUT/'end_to_end/measurements').glob('*.json'):physical[int(p.stem[:8],16)].append(p.stem)
collisions={str(k):v for k,v in physical.items() if len(v)>1};assert not collisions,collisions
refs=defaultdict(list)
for name in ['core','refined','full_best','full_raw','n12']:
 p=OUT/'end_to_end'/f'{name}_index.json'
 if not p.exists():continue
 for r in json.loads(p.read_text()):
  for e in r['entries']:
   m=e['record'];refs[m['archive']].append(dict(view=name,arm=e['arm'],n=m['n'],kappa=m['kappa'],h=m['h'],p=m['p'],method=m['method']))
dump(OUT/'end_to_end/measurement_randomization_audit_v2.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),unique_measurement_keys=len(physical),seed_prefix_collisions=collisions,shared_measurement_archives=[dict(archive=k,uses=v) for k,v in refs.items() if len(v)>1],policy='32 independent repetitions per key and budget. Same physical estimation key reused across arm labels or index views has exactly the same counts. Distinct observed32-bit key prefixes have distinct seeded streams. Within each basis all observables share joint-bitstring counts; covariance is stored. No cross-arm independence is assumed for shared archives.',earlier_correction='measurement_randomization_clarification.json preserves the first correction of the overbroad early metadata phrase. This v2 extends the audit to newly completed full raw and N12 indices.'))
print('RNG audit passed:',len(physical),'distinct key prefixes;',sum(len(v)>1 for v in refs.values()),'shared archives')
