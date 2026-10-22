"""
Inverse Quantum Fourier Transform (IQFT) Module.

In the Quantum Phase Estimation (QPE) algorithm, the Inverse QFT transforms
the relative phase kickback encoded in the counting register into the
computational basis, allowing direct classical measurement of the binary phase.
"""

from __future__ import annotations
import numpy as np
from qiskit import QuantumCircuit


def create_inverse_qft(num_qubits: int, insert_barriers: bool = False, as_gate: bool = False) -> QuantumCircuit:
    """
    Constructs an explicit gate-level Inverse Quantum Fourier Transform (IQFT) circuit.

    Mathematical Formulation:
        The standard QFT maps:
            |j> -> (1 / sqrt(2^n)) * sum_{k=0}^{2^n-1} exp(2 * pi * i * j * k / 2^n) |k>
        The Inverse QFT (QFT^dagger) inverts this mapping:
            |k> -> (1 / sqrt(2^n)) * sum_{j=0}^{2^n-1} exp(-2 * pi * i * j * k / 2^n) |j>

    Gate Sequence:
        1. Swap qubits i and (n - 1 - i) for i in [0, n // 2 - 1] to reverse qubit ordering.
        2. For each qubit i from 0 to n - 1:
           a. Apply controlled phase rotations CP(-pi / 2^(i - j)) for each j < i.
           b. Apply Hadamard gate H to qubit i.

    Parameters:
        num_qubits: Number of counting qubits in the register.
        insert_barriers: Whether to insert visual barriers between steps for readability.
        as_gate: If True, returns the circuit converted into a single reusable Gate object.

    Returns:
        QuantumCircuit: The Inverse QFT circuit on `num_qubits`.
    """
    if num_qubits < 1:
        raise ValueError(f"num_qubits must be at least 1, got {num_qubits}")

    qc = QuantumCircuit(num_qubits, name="IQFT")

    # Step 1: Reversal of qubit order using SWAP gates
    for i in range(num_qubits // 2):
        qc.swap(i, num_qubits - 1 - i)

    if insert_barriers and num_qubits > 1:
        qc.barrier()

    # Step 2: Inverse rotations and Hadamard gates
    for i in range(num_qubits):
        for j in range(i):
            # Rotation angle: -pi / 2^(i - j)
            angle = -np.pi / (2 ** (i - j))
            qc.cp(angle, j, i)
        qc.h(i)
        if insert_barriers and i < num_qubits - 1:
            qc.barrier()

    if as_gate:
        return qc.to_gate(label="QFT†")

    return qc


def create_forward_qft(num_qubits: int) -> QuantumCircuit:
    """
    Constructs the forward Quantum Fourier Transform (QFT) circuit for verification.
    QFT * IQFT must equal the identity operator.
    """
    qc = QuantumCircuit(num_qubits, name="QFT")

    for i in reversed(range(num_qubits)):
        qc.h(i)
        for j in reversed(range(i)):
            angle = np.pi / (2 ** (i - j))
            qc.cp(angle, j, i)

    for i in range(num_qubits // 2):
        qc.swap(i, num_qubits - 1 - i)

    return qc
