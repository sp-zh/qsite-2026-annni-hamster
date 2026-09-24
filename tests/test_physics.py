import importlib.util
from pathlib import Path

import numpy as np
import pennylane as qml
import pytest

from annni.model import Chain, GroundState, fidelity_susceptibility


def upstream_builder():
    path = Path(__file__).resolve().parents[1]/"upstream/Scientific Track/starter_kit/annni.py"
    spec = importlib.util.spec_from_file_location("upstream_annni", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_annni_hamiltonian


@pytest.mark.parametrize("n,kappa,h", [(5,.3,.7),(6,.8,.2),(8,.5,1.1)])
def test_against_upstream_pennylane_and_dense(n, kappa, h):
    chain = Chain(n)
    matrix = qml.matrix(upstream_builder()(n,kappa,h),wire_order=range(n)).real
    np.testing.assert_allclose(chain.full_matrix(kappa,h).toarray(),matrix,atol=1e-13)
    energies, vectors = np.linalg.eigh(matrix)
    result = chain.ground_state(kappa,h)
    assert abs(result.energy-energies[0]) < 1e-10
    assert abs(np.vdot(result.state,vectors[:,0]))**2 > 1-1e-8
    assert np.linalg.norm(matrix@result.state-result.energy*result.state) < 1e-8
    obs = chain.observables(result)
    assert abs(obs['energy_per_site']-(-obs['c1']+kappa*obs['c2']-h*obs['mx'])) < 1e-10


@pytest.mark.parametrize("kappa,energy,c1,c2,ferro,ap,deg",[
    (.2,-6.4,1,1,1,0,2),(.8,-6.4,0,-1,0,.5,4)])
def test_classical_limits(kappa,energy,c1,c2,ferro,ap,deg):
    chain=Chain(8)
    state=chain.ground_state(kappa,0)
    obs=chain.observables(state)
    np.testing.assert_allclose([state.energy,obs['c1'],obs['c2'],obs['m2_ferro'],obs['m2_antiphase']],
                               [energy,c1,c2,ferro,ap],atol=1e-12)
    assert state.state is None and state.classical_degeneracy==deg
    assert obs['mx']==0


def test_multiphase_point_mixture():
    chain=Chain(8)
    result=chain.ground_state(.5,0)
    assert result.classical_degeneracy > 4
    assert result.energy == -4
    assert np.isclose(result.probabilities.sum(),1)


def test_plus_state_background_and_momentum_sum_rule():
    chain=Chain(8)
    state=np.ones(256)/16
    obs=chain.observables(GroundState(0,state,state**2,0,0))
    np.testing.assert_allclose(obs['structure_factor'],np.ones(8)/8,atol=1e-12)
    assert np.isclose(obs['mx'],1)
    assert np.isclose(obs['m2_antiphase'],1/8)


@pytest.mark.parametrize("n,h",[(8,.2),(8,1.),(12,1.5)])
def test_exact_transverse_ising_energy(n,h):
    # Independent Jordan-Wigner finite-ring ground energy in even sector.
    momenta=(2*np.arange(n)+1)*np.pi/n
    exact=-np.sum(np.sqrt(1+h*h-2*h*np.cos(momenta)))
    result=Chain(n).ground_state(0,h)
    assert abs(result.energy-exact) < 1e-9


def test_fidelity_convention_and_zero_field_mask():
    angle=.1
    _, chi=fidelity_susceptibility([None,np.array([1.,0.]),np.array([np.cos(angle),np.sin(angle)])],np.array([0.,.1,.2]))
    assert np.isnan(chi[0])
    assert np.isclose(chi[1],-np.log(np.cos(angle)**2)/.1**2)


def test_structure_against_explicit_correlations():
    chain=Chain(8)
    result=chain.ground_state(.8,.4)
    obs=chain.observables(result)
    zz=chain.z.T@(result.probabilities[:,None]*chain.z)
    for j,q in enumerate(2*np.pi*np.arange(8)/8):
        weights=np.exp(1j*q*np.arange(8))
        direct=np.vdot(weights,zz@weights).real/64
        assert abs(obs['structure_factor'][j]-direct)<1e-12
    assert np.isclose(obs['structure_factor'].sum(),1)


def test_low_field_translation_and_fidelity():
    chain=Chain(16)
    states=[chain.ground_state(.8,h).state for h in [.05,.1]]
    shifted=((chain.indices << 1) & (chain.dim-1)) | (chain.indices >> 15)
    for state in states:
        np.testing.assert_allclose(state,state[shifted],atol=1e-12)
    # Deep antiphase small-field changes must not swap arbitrary cat states.
    assert abs(np.vdot(*states))**2 > .99
