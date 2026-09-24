"""H = -sum ZZ_nn + kappa sum ZZ_nnn - h sum X, with periodic boundaries.

Wire 0 is the most significant bit, matching PennyLane wire_order=range(N).
For h>0 the connected stoquastic Hamiltonian has a unique positive ground
state, hence global spin-flip parity +1. We solve only that sector. No
lowest-level splitting is used as a phase boundary diagnostic.
"""
from dataclasses import dataclass

import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import eigsh


@dataclass
class GroundState:
    energy: float
    state: np.ndarray | None
    probabilities: np.ndarray
    residual: float
    classical_degeneracy: int


class Chain:
    def __init__(self, n: int):
        if not isinstance(n, int) or n < 5:
            raise ValueError("Use integer N>=5 to avoid duplicate short-ring bonds.")
        self.n = n
        self.dim = 1 << n
        self.indices = np.arange(self.dim, dtype=np.int64)
        self.z = (1 - 2 * ((self.indices[:, None] >> np.arange(n-1, -1, -1)) & 1)).astype(np.int8)
        self.nn = np.sum(self.z * np.roll(self.z, -1, axis=1), axis=1)
        self.nnn = np.sum(self.z * np.roll(self.z, -2, axis=1), axis=1)
        # |r,+> = (|r> + |complement(r)>)/sqrt(2), r's leading bit = 0.
        half = self.dim // 2
        reps = np.arange(half)
        targets = np.stack([reps ^ (1 << i) for i in range(n)])
        targets = np.where(targets < half, targets, (self.dim-1) ^ targets)
        self.x_even = coo_matrix((np.ones(n*half),
                                 (np.tile(reps, n), targets.ravel())),
                                shape=(half, half)).tocsr()
        self.correlation_diagonals = np.stack([
            np.mean(self.z * np.roll(self.z, -r, axis=1), axis=1)
            for r in range(n)
        ])

    def full_matrix(self, kappa: float, h: float):
        rows = np.tile(self.indices, self.n)
        cols = np.concatenate([self.indices ^ (1 << i) for i in range(self.n)])
        flip = coo_matrix((np.full(len(rows), -h), (rows, cols)),
                          shape=(self.dim, self.dim)).tocsr()
        return flip + diags(-self.nn + kappa*self.nnn, dtype=float)

    def ground_state(self, kappa: float, h: float, tol: float = 1e-11) -> GroundState:
        if not np.isfinite(kappa) or not np.isfinite(h) or kappa < 0 or h < 0:
            raise ValueError("kappa and h must be finite and nonnegative")
        diagonal = -self.nn + kappa*self.nnn
        if h == 0:
            mask = np.isclose(diagonal, diagonal.min(), atol=1e-12, rtol=0)
            return GroundState(float(diagonal.min()), None,
                               mask.astype(float)/mask.sum(), 0., int(mask.sum()))
        half = self.dim//2
        matrix = diags(diagonal[:half], dtype=float) - h*self.x_even
        # Uniform positive start is also translation/reflection invariant.
        # Random starts can retain almost-degenerate momentum components at
        # low h even with an excellent residual, corrupting fidelity.
        v0 = np.ones(half) / np.sqrt(half)
        energy, vectors = eigsh(matrix, k=1, which="SA", tol=tol, v0=v0,
                                maxiter=20000)
        even = vectors[:, 0]
        if even.sum() < 0:
            even = -even
        state = np.concatenate([even, even[::-1]]) / np.sqrt(2.)
        # Remove numerical leakage into other momenta. The unique h>0 ground
        # state has momentum zero by positivity and translation invariance.
        shifted = self.indices.copy()
        projected = state.copy()
        for _ in range(1, self.n):
            shifted = ((shifted << 1) & (self.dim-1)) | (shifted >> (self.n-1))
            projected += state[shifted]
        state = projected / np.linalg.norm(projected)
        even = np.sqrt(2.) * state[:half]
        energy[0] = even @ (matrix @ even)
        residual = float(np.linalg.norm(matrix @ even - energy[0]*even))
        if residual > 1e-8*max(1., abs(energy[0])):
            raise RuntimeError(f"Eigensolver residual too large: {residual}")
        return GroundState(float(energy[0]), state, state**2, residual, 0)

    def observables(self, result: GroundState) -> dict:
        corr = self.correlation_diagonals @ result.probabilities
        # m_q^2 = sum_r exp(i q r) C(r) / N, including the 1/N self term.
        structure = np.fft.fft(corr).real / self.n
        q = np.pi/2
        m_ap = float(np.dot(np.cos(q*np.arange(self.n)), corr)/self.n) if self.n%4 == 0 else float(
            np.dot(result.probabilities,
                   np.abs(self.z @ np.exp(1j*q*np.arange(self.n)))**2)/self.n**2)
        mx = 0. if result.state is None else float(sum(
            np.vdot(result.state, result.state[self.indices ^ (1 << i)]).real
            for i in range(self.n))/self.n)
        return dict(energy_per_site=result.energy/self.n, mx=mx,
                    c1=float(corr[1]), c2=float(corr[2]),
                    m2_ferro=float(structure[0]), m2_antiphase=m_ap,
                    correlations=corr, structure_factor=structure,
                    residual=result.residual,
                    classical_degeneracy=result.classical_degeneracy)


def fidelity_susceptibility(states: list[np.ndarray | None], fields: np.ndarray):
    """-log(|<psi(h)|psi(h+dh)>|^2)/dh^2 at interval midpoints.

    Intervals touching a degenerate h=0 mixture are intentionally NaN.
    This is a finite-difference diagnostic, not a fitted critical field.
    """
    values = np.full(len(fields)-1, np.nan)
    for i, (left, right) in enumerate(zip(states[:-1], states[1:])):
        if left is not None and right is not None:
            f = np.clip(abs(np.vdot(left, right))**2, np.finfo(float).tiny, 1.)
            values[i] = -np.log(f)/(fields[i+1]-fields[i])**2
    return (fields[:-1]+fields[1:])/2, values
