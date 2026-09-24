from __future__ import annotations

import numpy as np
import pennylane as qml

from .annni import build_annni_hamiltonian


def noisy_entangling_layer(n_qubits: int, theta: float, p: float) -> None:
    """A small ring ansatz with depolarizing noise after each CNOT target."""
    for wire in range(n_qubits):
        qml.RY(theta, wires=wire)
    for wire in range(n_qubits):
        target = (wire + 1) % n_qubits
        qml.CNOT(wires=[wire, target])
        if p > 0:
            qml.DepolarizingChannel(p, wires=target)


def simple_noisy_energy(
    n_qubits: int,
    kappa: float,
    h: float,
    theta: float,
    p: float,
    layers: int = 2,
) -> float:
    """Evaluate a simple noisy ansatz against the ANNNI Hamiltonian."""
    hamiltonian = build_annni_hamiltonian(n_qubits=n_qubits, kappa=kappa, h=h, periodic=True)
    dev = qml.device("default.mixed", wires=n_qubits)

    @qml.qnode(dev)
    def circuit() -> float:
        for _ in range(layers):
            noisy_entangling_layer(n_qubits=n_qubits, theta=theta, p=p)
        return qml.expval(hamiltonian)

    return float(circuit())
