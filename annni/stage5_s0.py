"""Exact historical S0 compatibility correction; frozen S1/S2 remain unchanged.

The original Stage5 helper incorrectly used variance before energy for final
same-CNOT S0 ties. This wrapper restores the original two-stage energy rule.
No ED fields, new thresholds or coordinate exceptions are used.
"""
from .stage5_selection import choose as frozen_choose

def choose(candidates,rule,cfg=None):
 if rule!='S0':return frozen_choose(candidates,rule,cfg)
 n=candidates[0]['n'];groups={}
 for c in candidates:groups.setdefault((c['ref'],c['seed']),[]).append(c)
 reduced=[]
 for g in groups.values():
  emin=min(c['energy'] for c in g);reduced.append(min((c for c in g if c['energy']<=emin+n*1e-4),key=lambda c:(c['cnots'],c['energy'])))
 emin=min(c['energy'] for c in reduced);winner=min((c for c in reduced if c['energy']<=emin+n*1e-4),key=lambda c:(c['cnots'],c['energy']))
 return dict(candidate=winner,selection_unresolved=False,rule='S0',energy_tolerance_total=n*1e-4,state_access_assisted=False,compatibility='Original CNOT-then-energy ties, no variance tie')
