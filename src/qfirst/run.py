"""Run all circuits on a simulator, save histograms and a results table.

Usage:  python -m qfirst.run            (ideal simulator)
        python -m qfirst.run --noisy    (simple depolarizing noise model)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from qiskit import transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .circuits import bell_circuit, ghz_circuit, grover_circuit

SHOTS = 4096
SEED = 42
MARKED = "101"


def make_backend(noisy: bool) -> AerSimulator:
    if not noisy:
        return AerSimulator(seed_simulator=SEED)
    nm = NoiseModel()
    # Illustrative error rates, NOT calibrated to any real IBM device.
    nm.add_all_qubit_quantum_error(depolarizing_error(0.001, 1), ["h", "x", "u", "sx", "rz"])
    nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ["cx", "cz", "ecr"])
    return AerSimulator(noise_model=nm, seed_simulator=SEED)


def run_counts(qc, backend) -> dict[str, int]:
    tqc = transpile(qc, backend, seed_transpiler=SEED)
    return backend.run(tqc, shots=SHOTS).result().get_counts()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--noisy", action="store_true")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    backend = make_backend(args.noisy)
    tag = "noisy" if args.noisy else "ideal"

    jobs = {
        "bell": (bell_circuit(), {"00", "11"}),
        "ghz3": (ghz_circuit(3), {"000", "111"}),
        "grover3": (grover_circuit(3, MARKED), {MARKED}),
    }
    summary = {}
    for name, (qc, good) in jobs.items():
        counts = run_counts(qc, backend)
        p_good = sum(counts.get(s, 0) for s in good) / SHOTS
        summary[name] = {"expected_outcomes": sorted(good), "p_expected": round(p_good, 4),
                         "counts": dict(sorted(counts.items()))}
        plot_histogram(counts, title=f"{name} ({tag}, {SHOTS} shots)").savefig(
            out / f"{name}_{tag}.png", dpi=120, bbox_inches="tight")
        qc.draw("mpl").savefig(out / f"{name}_circuit.png", dpi=120, bbox_inches="tight")
        print(f"{name:8s} P(expected outcomes) = {p_good:.3f}")

    (out / f"summary_{tag}.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
