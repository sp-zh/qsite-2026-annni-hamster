"""Correct measurement-cost accounting, kept separate from frozen numerical solver.
Raw solver counter counts appended rounds only (and erroneously assigns one
round to the fixed pilot). This module supplies audited counts without changing
any historical state, parameter, circuit or selection.
"""
from .upgrade_gates import pool

def search_cost(row):
 fixed=row['key']['fixed'];rounds=0 if fixed else len(row['steps'])+int(row['stop']=='pool_gradient')
 candidates=rounds*len(pool(row['n'],row['key']['extended']))
 reopt=sum(2*(len(row['selected']['params']) if fixed else s['step'])*s['nfev'] for s in row['steps'])
 return dict(pool_gradient_rounds=rounds,pool_derivatives=candidates,pool_parameter_shift_energy_evaluations=2*candidates,reoptimization_parameter_shift_energy_evaluations=reopt,optimizer_energy_evaluations=row['nfev'],hardware_two_basis_circuit_evaluations_upper_bound=2*(2*candidates+reopt+row['nfev']),actual_hardware_executions=0,scope='prospective two-basis parameter-shift cost; all actual optimization uses analytic statevectors')
