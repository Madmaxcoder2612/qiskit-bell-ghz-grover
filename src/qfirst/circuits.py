"""Three small quantum circuits: Bell pair, GHZ state, Grover search.

Qiskit uses little-endian bit order: in a measured bitstring such as "101",
the RIGHTMOST character is qubit 0.
"""
from __future__ import annotations

import math

from qiskit import QuantumCircuit


def bell_circuit(measure: bool = True) -> QuantumCircuit:
    """Two qubits entangled into (|00> + |11>) / sqrt(2)."""
    qc = QuantumCircuit(2, 2 if measure else 0, name="bell")
    qc.h(0)        # put qubit 0 into an equal superposition of 0 and 1
    qc.cx(0, 1)    # flip qubit 1 if qubit 0 is 1 -> entanglement
    if measure:
        qc.measure([0, 1], [0, 1])
    return qc


def ghz_circuit(n: int = 3, measure: bool = True) -> QuantumCircuit:
    """n qubits in (|00..0> + |11..1>) / sqrt(2)."""
    if n < 2:
        raise ValueError("GHZ needs at least 2 qubits")
    qc = QuantumCircuit(n, n if measure else 0, name=f"ghz{n}")
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    if measure:
        qc.measure(range(n), range(n))
    return qc


def _oracle(n: int, marked: str) -> QuantumCircuit:
    """Phase oracle: flips the sign of the amplitude of the marked bitstring."""
    qc = QuantumCircuit(n, name="oracle")
    # Qiskit bit order: marked[-1] is qubit 0. Turn 0-bits into 1s so that
    # the multi-controlled Z fires exactly on the marked state.
    zeros = [i for i, bit in enumerate(reversed(marked)) if bit == "0"]
    for q in zeros:
        qc.x(q)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for q in zeros:
        qc.x(q)
    return qc


def _diffuser(n: int) -> QuantumCircuit:
    """Inversion about the mean: amplifies the marked amplitude."""
    qc = QuantumCircuit(n, name="diffuser")
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def optimal_grover_iterations(n: int) -> int:
    """About (pi/4) * sqrt(N) iterations for N = 2**n items and 1 marked item."""
    return max(1, math.floor(math.pi / 4 * math.sqrt(2**n)))


def grover_circuit(n: int = 3, marked: str = "101", iterations: int | None = None,
                   measure: bool = True) -> QuantumCircuit:
    """Grover search for one marked bitstring among 2**n."""
    if len(marked) != n or set(marked) - {"0", "1"}:
        raise ValueError(f"marked must be a {n}-character bitstring")
    if n < 2:
        raise ValueError("Grover here needs at least 2 qubits")
    k = optimal_grover_iterations(n) if iterations is None else iterations
    qc = QuantumCircuit(n, n if measure else 0, name=f"grover{n}")
    qc.h(range(n))
    for _ in range(k):
        qc.compose(_oracle(n, marked), inplace=True)
        qc.compose(_diffuser(n), inplace=True)
    if measure:
        qc.measure(range(n), range(n))
    return qc
