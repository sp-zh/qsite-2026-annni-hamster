"""Audit the labels actually used before the later, stricter reporting scope."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_reference_scopes import scopes
out={}
for task in ['development','validation']:
 rows=[]
 for r in json.loads((OUT/f'reference_atlas/{task}_evaluation.json').read_text()):
  s=scopes(r['label'],r['level'],r)
  rows.append(dict(kappa=r['kappa'],h=r['h'],used_label=r['label'],used_in_training_or_threshold_selection=r['label'] is not None,**s))
 used=[r for r in rows if r['used_in_training_or_threshold_selection']]
 out[task]=dict(rows=rows,used_coordinates=len(used),physical_label_supported=sum(r['physical_label'] is not None for r in used),pattern_proxy_only=sum(r['physical_label'] is None for r in used),original_label_counts=dict(collections.Counter(r['used_label'] for r in used)))
dump(OUT/'confirmation/detector_training_scope_audit.json',dict(tasks=out,frozen_method_sha=sha(OUT/'confirmation/method_frozen.json'),interpretation='Frozen D4/D5 were trained/tuned using declared v1 development/validation labels, including some later downgraded RN multi-size pattern proxies. The original training metadata wording independent-labelled is therefore too broad. No retraining or threshold change follows this audit. Report physical-interior scores and RN pattern agreement separately; proxy labels are not independent thermodynamic truth.',confirmation_used=False))
print({k:{a:b for a,b in v.items() if a!='rows'} for k,v in out.items()})
