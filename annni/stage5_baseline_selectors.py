"""Compatibility-only S0/S1 definitions; frozen S2 delegated unchanged."""
from .stage5_s0 import choose as compatible_choose
from .stage5_adapt import PLAN

def choose(candidates,rule,cfg=None):
 if rule!='S1':return compatible_choose(candidates,rule,cfg)
 tol=PLAN['selector_numerical_tie_total'];emin=min(c['energy'] for c in candidates);winner=min((c for c in candidates if c['energy']<=emin+tol),key=lambda c:(c['cnots'],c['energy']))
 return dict(candidate=winner,selection_unresolved=False,rule='S1',energy_tolerance_total=tol,state_access_assisted=False,compatibility='Energy and resource only; variance never read')
