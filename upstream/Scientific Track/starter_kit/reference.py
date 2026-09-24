from __future__ import annotations

import numpy as np


def ising_transition(kappa: np.ndarray | float) -> np.ndarray:
    kappa = np.asarray(kappa, dtype=float)
    safe = np.maximum(kappa, 1e-9)
    numerator = 1.0 - kappa
    inside = np.clip((1.0 - 3.0 * kappa + 4.0 * kappa**2) / np.maximum(1.0 - kappa, 1e-9), 0.0, None)
    values = numerator * (1.0 - np.sqrt(inside)) / safe
    return np.where(kappa < 0.5, values, np.nan)


def kt_transition(kappa: np.ndarray | float) -> np.ndarray:
    kappa = np.asarray(kappa, dtype=float)
    inside = np.clip((kappa - 0.5) * (kappa - 0.1), 0.0, None)
    values = 1.05 * np.sqrt(inside)
    return np.where(kappa > 0.5, values, np.nan)


def bkt_transition(kappa: np.ndarray | float) -> np.ndarray:
    kappa = np.asarray(kappa, dtype=float)
    values = 1.05 * (kappa - 0.5)
    return np.where(kappa > 0.5, values, np.nan)
