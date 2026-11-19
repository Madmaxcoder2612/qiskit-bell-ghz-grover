import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from qfirst import bell_circuit, ghz_circuit, grover_circuit, optimal_grover_iterations


def probs(qc):
    return Statevector.from_instruction(qc).probabilities_dict()


def test_bell_state_is_00_11_half_each():
    p = probs(bell_circuit(measure=False))
    assert p["00"] == pytest.approx(0.5)
    assert p["11"] == pytest.approx(0.5)
    assert "01" not in p and "10" not in p


@pytest.mark.parametrize("n", [2, 3, 5])
def test_ghz_only_all_zeros_or_all_ones(n):
    p = probs(ghz_circuit(n, measure=False))
    assert p["0" * n] == pytest.approx(0.5)
    assert p["1" * n] == pytest.approx(0.5)
    assert len(p) == 2


@pytest.mark.parametrize("marked", ["000", "101", "110", "111"])
def test_grover_3_qubits_finds_marked_state(marked):
    p = probs(grover_circuit(3, marked, measure=False))
    assert max(p, key=p.get) == marked
    assert p[marked] > 0.94  # theory: sin^2(5*asin(1/sqrt8)) ~ 0.945


def test_grover_2_qubits_is_exact():
    p = probs(grover_circuit(2, "10", measure=False))
    assert p["10"] == pytest.approx(1.0)


def test_grover_too_many_iterations_overshoots():
    good = probs(grover_circuit(3, "101", iterations=2, measure=False))["101"]
    bad = probs(grover_circuit(3, "101", iterations=4, measure=False)).get("101", 0)
    assert bad < good


def test_optimal_iterations():
    assert optimal_grover_iterations(3) == 2
    assert optimal_grover_iterations(2) == 1


def test_invalid_inputs():
    with pytest.raises(ValueError):
        grover_circuit(3, "10")
    with pytest.raises(ValueError):
        ghz_circuit(1)
