"""Physical-interior support versus finite-size multi-N pattern proxies.
No detector training, raw label or prepared state is changed by these scopes.
"""
import json
from pathlib import Path
from .stage6_common import ROOT

def low_field_support(reference):
 if reference is None:return None
 k,h=reference['kappa'],reference['h'];gap=4*abs(1-2*k)
 if not (0<=k<=1 and h>0 and gap>0 and h/gap<=.05):return None
 data=[json.loads((ROOT/Path(p).with_suffix('.json')).read_text()) for p in reference['sources'][1:]]
 if len(data)!=2 or [r['n'] for r in data]!=[12,16] or any(r['reference_numerical_ambiguous'] for r in data):return None
 if k<.5:
  supported=all(r['structure_factor'][0]>.8 and r['binder']>.62 and r['mx']<.3 for r in data) and reference['m0_ratio_16_12']>.98
 else:
  supported=all(r['structure_factor'][r['n']//4]>.45 and r['mx']<.3 for r in data) and min(reference['ap_binder'])>.47 and reference['ap_ratio_16_12']>.98
 if not supported:return None
 return dict(classical_defect_gap=gap,local_h_over_gap=h/gap,criterion='h/Delta_classical<=.05; N12/16 order, fourth-moment Binder, polarization and<2%size drop jointly agree. This local energy-scale check is NOT an operator-norm perturbation theorem or an exact phase boundary.')

def scopes(label,level,reference=None):
 if level=='Rlarge_ED_interior':
  support=low_field_support(reference)
  if support:
   return dict(physical_label=label,physical_level='R0_extension_low_field_multiN',RN_proxy_label=label,legacy_reference_level=level,reason='Classical ordered limit with a nonzero independently enumerated defect gap, small transverse field relative to that local scale, and strong multi-size order/Binder evidence.',additional_evidence=support)
  return dict(physical_label=None,physical_level='RN_multisize_ED_pattern',RN_proxy_label=label,legacy_reference_level=level,reason='N12/16 order/Binder/gap criteria alone support a finite-size pattern; commensurability can hide an incommensurate region. Not independent thermodynamic phase truth.')
 return dict(physical_label=label,physical_level=level,RN_proxy_label=label,legacy_reference_level=level,reason='Analytic or explicitly qualified small/high-field interior evidence; finite-field extensions remain distinguishable from exact R0.')
