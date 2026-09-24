from __future__ import annotations

from functools import lru_cache

import numpy as np
import pennylane as qml

from .annni import build_annni_hamiltonian
from .observables import order_parameter_summary

I2 = np.eye(2, dtype=np.complex128)
XMAT = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
ZMAT = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def _kron_all(factors: list[np.ndarray]) -> np.ndarray:
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


@lru_cache(maxsize=None)
def _single_site_matrix(n_qubits: int, site: int, kind: str) -> np.ndarray:
    base = XMAT if kind == "x" else ZMAT
    factors = [I2] * n_qubits
    factors[site] = base
    return _kron_all(factors)


@lru_cache(maxsize=None)
def _pair_zz_matrix(n_qubits: int, site_a: int, site_b: int) -> np.ndarray:
    factors = [I2] * n_qubits
    factors[site_a] = ZMAT
    factors[site_b] = ZMAT
    return _kron_all(factors)


def _dense_annni_matrix(n_qubits: int, kappa: float, h: float, periodic: bool) -> np.ndarray:
    limit_nn = n_qubits if periodic else n_qubits - 1
    limit_nnn = n_qubits if periodic else n_qubits - 2
    dimension = 2**n_qubits
    matrix = np.zeros((dimension, dimension), dtype=np.complex128)

    for i in range(limit_nn):
        matrix -= _pair_zz_matrix(n_qubits, i, (i + 1) % n_qubits)
    for i in range(limit_nnn):
        matrix += kappa * _pair_zz_matrix(n_qubits, i, (i + 2) % n_qubits)
    for i in range(n_qubits):
        matrix -= h * _single_site_matrix(n_qubits, i, "x")
    return matrix


def exact_ground_state(
    n_qubits: int,
    kappa: float,
    h: float,
    periodic: bool = True,
) -> dict[str, object]:
    """Return the lowest-energy eigenpair and observable summary."""
    hamiltonian = build_annni_hamiltonian(n_qubits=n_qubits, kappa=kappa, h=h, periodic=periodic)
    matrix = _dense_annni_matrix(n_qubits=n_qubits, kappa=kappa, h=h, periodic=periodic)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    ground_state = eigenvectors[:, 0]
    summary = order_parameter_summary(ground_state, n_qubits)
    return {
        "hamiltonian": hamiltonian,
        "matrix": matrix,
        "eigenvalues": eigenvalues,
        "ground_energy": float(np.real(eigenvalues[0])),
        "energy_gap": float(np.real(eigenvalues[1] - eigenvalues[0])),
        "state": ground_state,
        "summary": summary,
    }
