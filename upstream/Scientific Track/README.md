# Theory Track: Mapping the Phase Diagram of the ANNNI Model Under Noise

# Overview

> **Map the phase diagram of the 1D ANNNI model in the (κ, h) plane using PennyLane. Then study how depolarizing noise on two-qubit gates distorts the phase boundaries. Identify which phases are most robust to noise and which are most fragile.**

### What You Submit

1. A Jupyter notebook with your full implementation and analysis
2. Phase diagram images: clean (p=0), noisy (p=0.01), noisy (p=0.05)
3. A 2–3 page writeup with your method, results, and physical interpretation
4. A 5–7 minute presentation

### How You're Scored

| Category | Weight |
|---|---|
| Phase diagram accuracy (vs. known analytical boundaries) | 25% |
| Noise analysis depth (which phases shift, by how much, why) | 25% |
| Physical insight (connecting results to physics) | 20% |
| Technical sophistication (method complexity, system size, novelty) | 15% |
| Presentation and clarity | 15% |

### Bonus Opportunities

- Detecting the **floating phase** (very hard at small system sizes)
- Pushing to **N ≥ 12 qubits**
- Comparing **multiple methods** on the same system
- Implementing **error mitigation** to recover clean boundaries from noisy data
- Using **Trotterized time evolution** for dynamical phase signatures

### This Challenge Extends Two PennyLane Resources

| Resource | What It Provides | Link |
|---|---|---|
| **"A Noisy Heisenberg Model"** (challenge) | Trotterization with depolarizing noise, fidelity computation | [pennylane.ai/challenges/heisenberg_model](https://pennylane.ai/challenges/heisenberg_model) |
| **"ANNNI Phase Detection"** (demo) | ANNNI Hamiltonian, QCNN + autoencoder architectures, phase boundary formulas | [pennylane.ai/qml/demos/tutorial_annni](https://pennylane.ai/qml/demos/tutorial_annni) |

You should read both before starting. The starter kit builds on top of them.

---

# The ANNNI Model

## Spins on a Chain

Imagine a row of tiny magnets (spins), each pointing either **up** (↑) or **down** (↓). In quantum mechanics, each spin can also be in a **superposition** of up and down, which we denote by (→).

**The Hamiltonian**:
```
H = -ΣZᵢZᵢ₊₁ + κΣZᵢZᵢ₊₂ - hΣXᵢ
```

The Hamiltonian is the function of the orientations of the spins that determines the energy of each configuration. Unlike a more familiar phase transition such as ice melting into water, we will study the phases of this system at zero temperature. In this setting, the system prefers the ground state of the Hamiltonian; the state with the lowest total energy.

```
Site:     1    2    3    4    5    6    7    8
Spin:     ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑     ← ferromagnetic (all aligned)
          ↑    ↑    ↓    ↓    ↑    ↑    ↓    ↓     ← antiphase (period-4 pattern)
          →    →    →    →    →    →    →    →     ← paramagnetic (aligned with field)
```


## Three competing interactions

One way to gain intuition about the ground state of the Hamiltonian is to study it in different limits, where different interactions dominate. In these limits, the ground state is the state which minimizes the energy of each interaction individually.

### Nearest-Neighbor Coupling ($-\sum_i Z_i Z_{i+1}$)

The configurations that minimize this term have all spins **aligned** either up or down. In analogy with a magnet, this is called the ferromagnetic interaction. If this interaction dominates, all spins point the same way.

```
J₁ wins:   ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑    (ferromagnetic phase)
            "align with your neighbor"
```

### Next-Nearest-Neighbor Frustration ($+\kappa \sum_i Z_i Z_{i+2}$)

The energy of this interaction is minimized when the next-nearest-neighbor (NNN) spins are **anti-aligned** (one up, one down). When $\kappa$ is order unity, it is impossible to minimize the NNN interaction and the ferromagnetic intertaction simultaneously, which is known as classical frustration.

```
|J₂| wins:   ↑ ↑ ↓ ↓ ↑ ↑ ↓ ↓    (antiphase)
              "anti-align with your next-nearest neighbor"
```

### Transverse Field ($-h \sum_i X_i$)

An external magnetic field pointing sideways tries to rotate all spins to point along its direction. 

```
h wins:    → → → → → → → →    (paramagnetic - everyone follows the field)
           "ignore your neighbors, follow the field"
```

## The Hamiltonian

Putting it all together, 

$$H = - \sum_i Z_i Z_{i+1} \;+\; \kappa \sum_i Z_i Z_{i+2} - h \sum_i X_i$$

The positive sign on the second term reflects that the next-nearest interaction is antiferromagnetic (it prefers anti-aligned spins two sites apart, competing with the nearest-neighbor ferromagnetic alignment). The two free parameters are:

- **$\kappa \geq 0$** — frustration strength. At $\kappa = 0$ there is no competing interaction; above $\kappa \approx 0.5$ the antiphase becomes the dominant ordered phase at low field.
- **$h \geq 0$** — transverse field strength.

By sweeping $\kappa$ from 0 to 1 and $h$ from 0 to 2, we can map out the **phase diagram** - a 2D plot showing which phase the system is in at each $(\kappa, h)$ point.

The starter kit in `Scientific Track/starter_kit/` provides a helper function that builds this Hamiltonian in PennyLane:

```python
from starter_kit import build_annni_hamiltonian

H = build_annni_hamiltonian(n_qubits=8, kappa=0.3, h=0.5)
```

## The Four Phases

| Phase | Where in $(\kappa, h)$ | Spin Pattern | How to Detect |
|---|---|---|---|
| **Ferromagnetic** | $\kappa < 0.5$, low $h$ | ↑↑↑↑↑↑↑↑ | Large nearest-neighbor correlation and, with symmetry breaking, nonzero magnetization |
| **Antiphase** | $\kappa > 0.5$, low $h$ | ↑↑↓↓↑↑↓↓ | Large staggered magnetization or structure factor peak at wavevector $\pi/2$ |
| **Paramagnetic** | High $h$ | →→→→→→→→ | Both $M$ and staggered magnetization ≈ 0 |
| **Floating** | Narrow sliver for $\kappa > 0.5$ between antiphase and paramagnetic | Incommensurate | Algebraically decaying correlations (very hard to detect at small $N$) |

---

# Phase Transitions - What Are We Looking For?

## What Is a Phase Transition?

A phase transition is an abrupt change in some measurable quantity due to the emergent collective behavior of many constituent parts.
**Quantum phase transitions** are similar but driven by changing the Hamiltonian parameters (like $\kappa$ and $h$) at zero temperature. As you smoothly change a parameter, the **ground state** (lowest-energy state) of the system can suddenly change its character. The points where this abrupt change happens are **phase boundaries**, and finding them is the core of this challenge.

## How to Detect Phase Transitions Computationally

There are several valid approaches. You choose whichever fits your skills and interests:

### Approach 1: Order Parameters

**Idea**: measure a quantity that takes different values in different phases. Where it changes sharply, there's a transition.

- **Magnetization** $M = \frac{1}{N}\sum_i \langle Z_i \rangle$ - nonzero in the ferromagnetic phase, near zero elsewhere
- **Staggered magnetization** - measures the ↑↑↓↓ pattern; large in the antiphase, small elsewhere
- **Correlation functions** $\langle Z_i Z_j \rangle$ - how correlated distant spins are

**Workflow**: use VQE or exact diag to find the ground state at each $(\kappa, h)$ point, measure the order parameter, plot it as a heatmap.

**Reference**: [PennyLane: Seeing Quantum Phase Transitions](https://pennylane.ai/qml/demos/tutorial_quantum_phase_transitions) - does exactly this for the simpler transverse-field Ising model.

### Approach 2: Quantum Machine Learning (QCNN)

**Idea**: train a quantum convolutional neural network to classify states into phases using labeled training points from regions where the phase is known analytically. Then use the trained QCNN to classify the entire parameter space.

**Workflow**: prepare ground states, label some as "ferromagnetic" or "paramagnetic" based on known boundaries, train a QCNN, predict the rest.

**Reference**: [PennyLane: ANNNI Phase Detection Demo](https://pennylane.ai/qml/demos/tutorial_annni) - implements exactly this approach, plus a quantum autoencoder variant.

### Approach 3: Quantum Autoencoder (Unsupervised)

**Idea**: train a quantum autoencoder to compress ground states. States in the same phase compress similarly; states in different phases compress differently. Use the reconstruction error as a phase indicator - no labels needed.

**Workflow**: prepare ground states, train autoencoder, plot reconstruction error across parameter space, look for boundaries where it changes.

**Reference**: also covered in the [PennyLane ANNNI Demo](https://pennylane.ai/qml/demos/tutorial_annni).

### Approach 4: Fidelity Susceptibility

**Idea**: compute the overlap (fidelity) between ground states at neighboring parameter values: $F(\lambda, \lambda + \delta) = |\langle \psi(\lambda) | \psi(\lambda + \delta) \rangle|^2$. At a phase transition, the ground state changes rapidly, so fidelity drops sharply.

**Workflow**: compute ground states at a grid of points, compute fidelity between neighbors, plot. Peaks in $\chi_F = -\partial^2 F / \partial \lambda^2$ mark transitions.

### Approach 5: Trotterized Time Evolution (Dynamics)

**Idea**: instead of finding ground states, prepare a simple initial state and time-evolve it under $H$. Measure dynamical quantities like the **Loschmidt echo** (overlap with initial state over time). Phase transitions leave signatures in the dynamics.

**Workflow**: implement Trotterization (as in the [Noisy Heisenberg challenge](https://pennylane.ai/challenges/heisenberg_model)), run time evolution, analyze dynamical observables.

This approach connects most directly to the Noisy Heisenberg challenge you're extending.

## The Known Phase Boundaries (for reference)

The analytical transition lines (from the [PennyLane ANNNI demo](https://pennylane.ai/qml/demos/tutorial_annni)):

- **Ising transition** (ferro ↔ para, for $\kappa < 0.5$):

$$h_I(\kappa) \approx \frac{1-\kappa}{\kappa}\left(1 - \sqrt{\frac{1-3\kappa+4\kappa^2}{1-\kappa}}\right)$$

- **Kosterlitz-Thouless (KT) transition** (floating ↔ para, for $\kappa > 0.5$) — the upper boundary of the floating phase:

$$h_{KT}(\kappa) \approx 1.05\sqrt{(\kappa-0.5)(\kappa-0.1)}$$

- **BKT transition** (antiphase ↔ floating, for $\kappa > 0.5$) — the lower boundary of the floating phase:

$$h_{BKT}(\kappa) \approx 1.05(\kappa - 0.5)$$

For $\kappa > 0.5$, ordering from low to high field: antiphase → floating → paramagnetic, bounded by $h_{BKT}$ and $h_{KT}$ respectively. Your clean phase diagram should roughly match these curves. The starter kit provides functions to plot them as overlays, but at finite $N$ with periodic boundaries they are best treated as qualitative reference lines rather than exact boundaries.

---

# The Noise Twist - From PennyLane's Noisy Heisenberg Challenge

## What Is Depolarizing Noise?

In a perfect quantum computer, gates execute exactly as intended. In a real one, every gate has a small chance of introducing an error.

**Depolarizing noise** is a standard error model for quantum gates. After each CNOT, the target qubit undergoes a random Pauli error with total probability $p$: each of X, Y, and Z is applied with probability $p/3$, so the qubit is left unchanged with probability $1 - p$.

- At $p = 0$: no noise, perfect gates
- At $p = 0.01$: 1% total error probability per CNOT — mild noise
- At $p = 0.05$: 5% total error probability per CNOT — significant noise

## How to Add Noise in PennyLane

From the [Noisy Heisenberg challenge](https://pennylane.ai/challenges/heisenberg_model): place a `qml.DepolarizingChannel` after every CNOT, targeting the CNOT's target qubit.

```python
# Noisy CNOT: apply CNOT, then depolarizing noise on the target
qml.CNOT(wires=[control, target])
qml.DepolarizingChannel(p, wires=target)
```

Important: you need to use `"default.mixed"` device instead of `"default.qubit"` for noise simulation, since noise turns pure states into mixed states (density matrices).

```python
dev = qml.device("default.mixed", wires=n_qubits)
```

The starter kit's `noise_utils.py` provides a small wrapper that demonstrates this convention automatically.

## What Noise Does to Phase Detection

**Intuition**: noise scrambles quantum correlations. Ordered phases (ferromagnetic and antiphase) are defined by specific correlation patterns between spins. Noise degrades these correlations, making ordered phases look more like the disordered (paramagnetic) phase.

**What you should expect to see**:
- At $p = 0.01$: phase boundaries shift slightly, phases are still distinguishable
- At $p = 0.05$: significant blurring — the ordered phases shrink as noise pushes more of parameter space toward looking paramagnetic
- The **ferromagnetic** phase may be more robust than the **antiphase** (because the antiphase has a more complex correlation pattern that's more fragile)
- The **floating phase** (if you can detect it at all) will likely be the first to disappear under noise

**Your task**: map the diagram at $p = 0$, $p = 0.01$, and $p = 0.05$, then analyze the differences.

---

# Tools & Methods Available

## Building the ANNNI Hamiltonian

The starter kit provides a helper, but you can also build it yourself using PennyLane's Pauli operators:

```python
import pennylane as qml
from pennylane import numpy as np

def build_annni_hamiltonian(n_qubits, kappa, h, j1=1.0, periodic=True):
    coeffs = []
    obs = []

    # Nearest-neighbor ZZ (ferromagnetic)
    for i in range(n_qubits - 1 + int(periodic)):
        coeffs.append(-j1)
        obs.append(qml.Z(i % n_qubits) @ qml.Z((i+1) % n_qubits))

    # Next-nearest-neighbor ZZ (frustrating)
    for i in range(n_qubits - 2 + 2*int(periodic)):
        coeffs.append(j1 * kappa)  # positive: penalizes aligned next-nearest pairs (antiferromagnetic at this distance)
        obs.append(qml.Z(i % n_qubits) @ qml.Z((i+2) % n_qubits))

    # Transverse field X
    for i in range(n_qubits):
        coeffs.append(-h)
        obs.append(qml.X(i))

    return qml.dot(coeffs, obs)
```

Also see: [PennyLane: How to Build Spin Hamiltonians](https://pennylane.ai/qml/demos/tutorial_how_to_build_spin_hamiltonians) for the `qml.spin` module approach.

## Finding the Ground State

### Option A: Exact Diagonalization (classical reference)

For N ≤ 12, you can exactly diagonalize the Hamiltonian matrix and extract the ground state. This is fast and exact - use it as a reference to validate your quantum methods.

One subtle point: for finite systems, the exact ground state often preserves the global symmetry, so raw $\langle Z_i \rangle$ can stay near zero even in an ordered phase. Correlation-based observables such as $\langle Z_i Z_{i+1} \rangle$ and $\langle Z_i Z_{i+2} \rangle$ are usually more informative in a starter workflow.

```python
import scipy.linalg

H_matrix = qml.matrix(H)
eigenvalues, eigenvectors = scipy.linalg.eigh(H_matrix)
ground_state = eigenvectors[:, 0]  # lowest eigenvalue
ground_energy = eigenvalues[0]
```

### Option B: Variational Quantum Eigensolver (VQE)

VQE is a hybrid quantum-classical algorithm that variationally optimizes a parameterized circuit to minimize $\langle \psi(\theta) | H | \psi(\theta) \rangle$. This is the standard quantum approach.

```python
dev = qml.device("default.qubit", wires=n_qubits)

@qml.qnode(dev)
def cost(params):
    # Your ansatz here (e.g., hardware-efficient layers)
    for i in range(n_qubits):
        qml.RY(params[i], wires=i)
    for i in range(n_qubits - 1):
        qml.CNOT(wires=[i, i+1])
    return qml.expval(H)
```

See: [PennyLane VQE Demo](https://pennylane.ai/qml/demos/tutorial_vqe) and [PennyLane: Seeing Quantum Phase Transitions](https://pennylane.ai/qml/demos/tutorial_quantum_phase_transitions) for full VQE implementations.

## Phase Classification Methods

Each of these is a valid approach with different tradeoffs:

| Method | Type | Needs Labels? | PennyLane Reference | Difficulty |
|---|---|---|---|---|
| **VQE + order parameters** | Direct measurement | No | [Phase Transitions Demo](https://pennylane.ai/qml/demos/tutorial_quantum_phase_transitions) | Medium |
| **QCNN** | Supervised ML | Yes (from known regions) | [ANNNI Demo](https://pennylane.ai/qml/demos/tutorial_annni) | Medium-Hard |
| **Quantum autoencoder** | Unsupervised ML | No | [ANNNI Demo](https://pennylane.ai/qml/demos/tutorial_annni) | Medium-Hard |
| **Fidelity susceptibility** | Ground state overlap | No | No demo (implement from formula) | Medium |
| **Trotterized dynamics** | Time evolution | No | [Noisy Heisenberg Challenge](https://pennylane.ai/challenges/heisenberg_model) | Hard |

**You choose your method - there is no single right approach.** Teams using different methods may all produce excellent results.

---

# Deliverables, Scoring & Strategy

## What to Submit

| Deliverable | Format | Required? |
|---|---|---|
| Implementation notebook | `.ipynb` | ✅ Yes |
| Clean phase diagram ($p = 0$) | Image (PNG/PDF) | ✅ Yes |
| Noisy phase diagram ($p = 0.01$) | Image (PNG/PDF) | ✅ Yes |
| Noisy phase diagram ($p = 0.05$) | Image (PNG/PDF) | ✅ Yes |
| Writeup | Markdown or PDF, 2–3 pages | ✅ Yes |
| Presentation | 5–7 minutes | ✅ Yes |

## Judging Rubric Detail

### Phase Diagram Accuracy (25%)

- Do the three main phases (ferro, antiphase, para) appear in roughly the right locations?
- Do the boundaries approximately match the analytical transition lines?
- Is the grid resolution sufficient (at least 15×15)?
- Is the $\kappa = 0.5$ multicritical point region handled correctly?

### Noise Analysis Depth (25%)

- Goes beyond "it gets worse with noise" - which phases shift, in which direction, by how much?
- Quantitative comparison (e.g., "the ferro-para boundary at $\kappa = 0.3$ shifts from $h = 0.72$ to $h = 0.65$ at $p = 0.05$")
- Identifies which phase is most robust and which is most fragile, with explanation
- Comments on whether the floating phase (if detected) survives noise

### Physical Insight (20%)

- Connects noise effects to physical properties (e.g., "the antiphase requires long-range correlations that noise destroys")
- Interprets results in the language of the model (frustration, ordering, correlation length)
- Notes limitations of the approach and system size

### Technical Sophistication (15%)

- Method complexity and appropriateness
- System size (N=8 baseline, N≥12 impressive)
- Multiple methods compared
- Error mitigation attempted
- Custom ansatz design or novel approaches

### Presentation & Clarity (15%)

- Clear, well-labeled plots
- Organized notebook with comments
- Accessible writeup
- Engaging presentation

## Suggested workflow

-  Read this handout and the two PennyLane resources. Build the Hamiltonian. Get one ground state working at a single $(\kappa, h)$ point. Verify against exact diagonalization.
- Implement your phase classification method. Scan the full $(\kappa, h)$ grid. Produce the clean phase diagram. Compare to analytical boundaries. Debug.
- Add depolarizing noise. Re-run at $p = 0.01$ and $p = 0.05$. Produce noisy phase diagrams. Start the comparison analysis.
- Write analysis, create figures, prepare presentation. Attempt bonus goals if time permits.

## Key Resources - Annotated

### Must-Read Before Starting

- 📖 [PennyLane: ANNNI Phase Detection Demo](https://pennylane.ai/qml/demos/tutorial_annni) - **your primary starting point**. Contains everything: the Hamiltonian, ground state prep with VQE, QCNN architecture, autoencoder architecture, and phase boundary formulas. Read this first.
- 📖 [PennyLane: A Noisy Heisenberg Model](https://pennylane.ai/challenges/heisenberg_model) - the noise model you'll extend. Short challenge showing Trotterization with depolarizing noise and fidelity computation.

### Helpful Background

- 📖 [PennyLane: Seeing Quantum Phase Transitions](https://pennylane.ai/qml/demos/tutorial_quantum_phase_transitions) - VQE-based phase detection on the simpler transverse-field Ising model. Good warmup before tackling ANNNI.
- 📖 [PennyLane: How to Build Spin Hamiltonians](https://pennylane.ai/qml/demos/tutorial_how_to_build_spin_hamiltonians) - deep dive into the `qml.spin` module for constructing lattice Hamiltonians.
- 🔧 [CERN Quantum Phase Detection GitHub](https://github.com/CERN-IT-INNOVATION/Quantum-Phase-Detection-ANNNI) - full reference implementation with notebooks, pre-computed data, and both QCNN and autoencoder approaches.

### For Going Deep

- 📄 Monaco et al., "Quantum phase detection generalization from marginal QNN models" ([Phys. Rev. B 107, 2023](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.107.L081105)) - the paper behind the ANNNI demo
- 📄 Cea et al., "Exploring the Phase Diagram of the quantum 1D ANNNI model" ([arXiv:2402.11022](https://arxiv.org/abs/2402.11022)) - extended study with floating phase analysis at larger system sizes
- 📄 arXiv:2504.10673 (2025) - QSVM + VQC approach to ANNNI classification with SHAP feature importance analysis
- 📖 [PennyLane: Resource Estimation for Hamiltonian Simulation with GQSP](https://pennylane.ai/qml/demos/tutorial_estimator_hamiltonian_simulation_gqsp) - advanced Hamiltonian simulation resource estimation
