"""
Quantum Phase Estimation (QPE) Simulator Module.

Executes QPE circuits on Qiskit Aer simulators (Ideal or Noisy),
analyzes measurement distributions, and extracts phase estimates.
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

from qpe.circuit import build_qpe_circuit


@dataclass
class MeasuredState:
    """Represents a single measured computational basis state."""
    binary_str: str
    decimal_int: int
    shots: int
    probability: float
    estimated_phase: float
    absolute_error: float


@dataclass
class QPEResult:
    """Encapsulates the complete result of a QPE simulation run."""
    actual_phase: float
    num_counting_qubits: int
    total_shots: int
    simulation_mode: str  # "Ideal" or "Noisy"
    raw_counts: Dict[str, int]
    probabilities: Dict[str, float]
    most_probable_bitstring: str
    estimated_phase: float
    absolute_error: float
    relative_error: float
    success_probability: float
    is_exact_phase: bool
    all_states: List[MeasuredState]
    circuit: QuantumCircuit


def binary_to_decimal_phase(bitstring: str, num_qubits: int) -> float:
    """
    Converts a measured binary bitstring into a decimal phase theta.

    Formula:
        theta_est = decimal_value / (2^t)
        where decimal_value = int(bitstring, 2) and t = num_qubits.

    Example:
        For t = 3, bitstring '010':
            int('010', 2) = 2
            theta_est = 2 / 2^3 = 2 / 8 = 0.25
    """
    decimal_val = int(bitstring, 2)
    return decimal_val / (2 ** num_qubits)


def decimal_to_binary_fraction(theta: float, max_bits: int = 8) -> str:
    """
    Converts a decimal phase theta in [0, 1) to its binary fraction representation: 0.b1b2b3...
    """
    bits = []
    rem = theta % 1.0
    for _ in range(max_bits):
        rem *= 2
        bit = int(rem)
        bits.append(str(bit))
        rem -= bit
        if rem == 0:
            break
    return "0." + "".join(bits)


def estimate_phase_from_counts(
    counts: Dict[str, int],
    num_counting_qubits: int,
    actual_phase: float
) -> Dict[str, Any]:
    """
    Extracts the estimated phase from the simulation measurement counts.
    """
    total_shots = sum(counts.values())
    if total_shots == 0:
        raise ValueError("Counts dictionary is empty.")

    # Find the most frequent bitstring
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    best_bitstring, best_count = sorted_counts[0]

    estimated_phase = binary_to_decimal_phase(best_bitstring, num_counting_qubits)
    abs_error = abs(actual_phase - estimated_phase)
    rel_error = (abs_error / actual_phase) if actual_phase != 0 else abs_error
    success_prob = best_count / total_shots

    # Check if actual phase is mathematically an exact dyadic rational (k / 2^t)
    exact_int_check = round(actual_phase * (2 ** num_counting_qubits))
    is_exact = bool(np.isclose(actual_phase, exact_int_check / (2 ** num_counting_qubits), atol=1e-9))

    # Detailed list of all measured states
    all_states: List[MeasuredState] = []
    probabilities: Dict[str, float] = {}

    for bitstring, count in sorted_counts:
        prob = count / total_shots
        probabilities[bitstring] = prob
        state_phase = binary_to_decimal_phase(bitstring, num_counting_qubits)
        state_err = abs(actual_phase - state_phase)
        all_states.append(MeasuredState(
            binary_str=bitstring,
            decimal_int=int(bitstring, 2),
            shots=count,
            probability=prob,
            estimated_phase=state_phase,
            absolute_error=state_err
        ))

    return {
        "best_bitstring": best_bitstring,
        "best_count": best_count,
        "estimated_phase": estimated_phase,
        "absolute_error": abs_error,
        "relative_error": rel_error,
        "success_probability": success_prob,
        "is_exact_phase": is_exact,
        "probabilities": probabilities,
        "all_states": all_states,
    }


def run_qpe_simulation(
    theta: float,
    num_counting_qubits: int = 3,
    shots: int = 2048,
    noise_model: Optional[NoiseModel] = None,
    seed_simulator: Optional[int] = 42
) -> QPEResult:
    """
    Constructs and executes the QPE algorithm on AerSimulator.

    Parameters:
        theta: Unknown phase to estimate in [0, 1).
        num_counting_qubits: Number of counting qubits t (precision parameter).
        shots: Number of repetitions of the quantum circuit.
        noise_model: Optional Qiskit Aer NoiseModel for noisy simulation.
        seed_simulator: Random seed for reproducibility.

    Returns:
        QPEResult: Detailed simulation results including counts, errors, and circuit.
    """
    # Build complete QPE circuit
    qc = build_qpe_circuit(
        theta=theta,
        num_counting_qubits=num_counting_qubits,
        prepare_eigenstate=True,
        insert_barriers=True,
        include_measurements=True
    )

    # Configure backend with thread-safe single parallel thread on macOS
    sim_mode = "Noisy" if noise_model is not None else "Ideal"
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=seed_simulator, max_parallel_threads=1)

    # Execute
    job = simulator.run(qc, shots=shots)
    raw_counts = job.result().get_counts()

    # Analyze counts
    analysis = estimate_phase_from_counts(raw_counts, num_counting_qubits, theta)

    return QPEResult(
        actual_phase=theta,
        num_counting_qubits=num_counting_qubits,
        total_shots=shots,
        simulation_mode=sim_mode,
        raw_counts=raw_counts,
        probabilities=analysis["probabilities"],
        most_probable_bitstring=analysis["best_bitstring"],
        estimated_phase=analysis["estimated_phase"],
        absolute_error=analysis["absolute_error"],
        relative_error=analysis["relative_error"],
        success_probability=analysis["success_probability"],
        is_exact_phase=analysis["is_exact_phase"],
        all_states=analysis["all_states"],
        circuit=qc
    )
