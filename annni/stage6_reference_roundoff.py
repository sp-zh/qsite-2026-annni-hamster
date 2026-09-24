"""Machine-roundoff compatibility for declared reference-region endpoints only.

This is not coordinate rounding for simulation, cache keys or data isolation.
The original reference function and all frozen evaluation cohorts stay unchanged.
"""
import numpy as np
from .stage6_diagnostics import physical_reference

def endpoint_value(value,endpoints):
    value=float(value)
    for endpoint in endpoints:
        if abs(value-endpoint)<=16*np.finfo(float).eps*max(1,abs(endpoint)):
            return float(endpoint)
    return value

def map_reference(n,k,h,obs,binder):
    rk=endpoint_value(k,[0,.3,.65])
    rh=endpoint_value(h,[.1,.2,.7,1.3,1.6])
    old=physical_reference(n,k,h,None,obs,binder)
    new=physical_reference(n,rk,rh,None,obs,binder)
    return new,dict(version='declared_endpoint_machine_roundoff_v1',original_coordinates=[float(k),float(h)],reference_comparison_coordinates=[rk,rh],original_reference_label=old[0],original_reference_level=old[1],reference_label_changed=old[0]!=new[0],scope='Only16machine-epsilon neighborhoods of declared comparison endpoints; original Hamiltonian coordinates, states, detectors, cache keys and frozen cohort evaluations remain unchanged.')
