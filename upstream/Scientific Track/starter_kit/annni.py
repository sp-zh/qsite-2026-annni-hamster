from __future__ import annotations

import math

import pennylane as qml


def build_annni_hamiltonian(
    n_qubits: int,
    kappa: float,
    h: float,
    j1: float = 1.0,
    periodic: bool = True,
) -> qml.operation.Operator:
    """Construct the ANNNI Hamiltonian in the Z/Z/X convention."""
    coeffs: list[float] = []
    obs: list[qml.operation.Operator] = []

    limit_nn = n_qubits if periodic else n_qubits - 1
    limit_nnn = n_qubits if periodic else n_qubits - 2

    for i in range(limit_nn):
        j = (i + 1) % n_qubits
        coeffs.append(-j1)
        obs.append(qml.Z(i) @ qml.Z(j))

    for i in range(limit_nnn):
        j = (i + 2) % n_qubits
        coeffs.append(j1 * kappa)
        obs.append(qml.Z(i) @ qml.Z(j))

    for i in range(n_qubits):
        coeffs.append(-h)
        obs.append(qml.X(i))

    return qml.dot(coeffs, obs)


def coupling_edges(n_qubits: int, periodic: bool = True) -> dict[str, list[tuple[int, int]]]:
    """Return nearest- and next-nearest-neighbor couplings."""
    limit_nn = n_qubits if periodic else n_qubits - 1
    limit_nnn = n_qubits if periodic else n_qubits - 2
    nearest = [(i, (i + 1) % n_qubits) for i in range(limit_nn)]
    next_nearest = [(i, (i + 2) % n_qubits) for i in range(limit_nnn)]
    return {"nearest": nearest, "next_nearest": next_nearest}


def coupling_positions(n_qubits: int) -> dict[int, tuple[float, float]]:
    """Place the spin chain on a circle for quick visualizations."""
    positions: dict[int, tuple[float, float]] = {}
    for i in range(n_qubits):
        angle = 2.0 * math.pi * i / n_qubits
        positions[i] = (math.cos(angle), math.sin(angle))
    return positions
