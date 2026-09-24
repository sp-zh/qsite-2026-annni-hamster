from __future__ import annotations

from functools import lru_cache

import numpy as np


I2 = np.eye(2, dtype=np.complex128)
XMAT = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
ZMAT = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


def _kron_all(factors: list[np.ndarray]) -> np.ndarray:
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


@lru_cache(maxsize=None)
def _single_site_operator(n_qubits: int, site: int, kind: str) -> np.ndarray:
    base = XMAT if kind == "x" else ZMAT
    factors = [I2] * n_qubits
    factors[site] = base
    return _kron_all(factors)


@lru_cache(maxsize=None)
def _pair_operator(n_qubits: int, site_a: int, site_b: int) -> np.ndarray:
    factors = [I2] * n_qubits
    factors[site_a] = ZMAT
    factors[site_b] = ZMAT
    return _kron_all(factors)


def _expval_from_matrix(state: np.ndarray, matrix: np.ndarray) -> float:
    return float(np.real(np.vdot(state, matrix @ state)))


def order_parameter_summary(state: np.ndarray, n_qubits: int) -> dict[str, float]:
    """Compute simple finite-size observables for the Z/Z/X ANNNI convention."""
    z_values = [_expval_from_matrix(state, _single_site_operator(n_qubits, i, "z")) for i in range(n_qubits)]
    x_values = [_expval_from_matrix(state, _single_site_operator(n_qubits, i, "x")) for i in range(n_qubits)]
    zz_nearest = [
        _expval_from_matrix(state, _pair_operator(n_qubits, i, (i + 1) % n_qubits)) for i in range(n_qubits)
    ]
    zz_next = [
        _expval_from_matrix(state, _pair_operator(n_qubits, i, (i + 2) % n_qubits)) for i in range(n_qubits)
    ]
    antiphase_string = [zz_nearest[i] * zz_nearest[(i + 2) % n_qubits] for i in range(n_qubits)]

    return {
        "z_mean": float(np.mean(z_values)),
        "z_abs_mean": float(np.mean(np.abs(z_values))),
        "x_mean": float(np.mean(x_values)),
        "zz_nearest_mean": float(np.mean(zz_nearest)),
        "zz_next_nearest_mean": float(np.mean(zz_next)),
        "antiphase_string_mean": float(np.mean(antiphase_string)),
    }
