"""
Quantum Phase Estimation (QPE) Circuit Builder Module.

Implements the complete quantum circuit for Quantum Phase Estimation:
    U |psi> = exp(2 * pi * i * theta) |psi>
Estimating the unknown phase theta in [0, 1) using quantum measurement.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, Optional
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qpe.inverse_qft import create_inverse_qft


def create_phase_unitary(theta: float) -> tuple[float, str]:
    """
    Returns the angle parameter lambda = 2 * pi * theta for a Phase gate P(lambda),
    along with its LaTeX/textual representation.
    """
    angle = 2.0 * np.pi * theta
    label = f"P(2π · {theta:.4f})"
    return angle, label


def build_qpe_circuit(
    theta: float,
    num_counting_qubits: int = 3,
    prepare_eigenstate: bool = True,
    insert_barriers: bool = True,
    include_measurements: bool = True,
    unitary_type: str = "phase"
) -> QuantumCircuit:
    """
    Constructs the complete Quantum Phase Estimation circuit.

    Architecture:
        - Counting Register: `num_counting_qubits` qubits (indices 0 to t-1).
        - Target Register: 1 qubit (index t).
        - Classical Register: `num_counting_qubits` bits for measuring counting qubits.

    Workflow:
        1. Initialization:
           - Target qubit prepared in eigenstate |1> (via Pauli-X gate).
           - Phase gate P(2*pi*theta) has eigenstate |1> with eigenvalue exp(2*pi*i*theta).
        2. Superposition:
           - Hadamard gates applied to all counting qubits (0 to t-1).
        3. Controlled Unitary Powers:
           - For each counting qubit j in [0, t-1], apply controlled-U^(2^j) to target qubit.
           - For P(2*pi*theta), U^(2^j) = P(2^j * 2*pi*theta).
        4. Inverse Quantum Fourier Transform (IQFT):
           - Transforms phase kickback from Fourier basis back to computational basis.
        5. Quantum Measurement:
           - Measures counting qubits into classical register.

    Parameters:
        theta: Phase to estimate, typically in [0, 1).
        num_counting_qubits: Number of counting qubits (precision parameter t).
        prepare_eigenstate: If True, applies X to target qubit to prepare |1>.
        insert_barriers: If True, inserts barriers between logical stages.
        include_measurements: If True, adds measurement operators to the circuit.
        unitary_type: Type of unitary ('phase', 'T', 'S', 'Z').

    Returns:
        QuantumCircuit: The synthesized QPE circuit.
    """
    if num_counting_qubits < 1:
        raise ValueError(f"num_counting_qubits must be >= 1, got {num_counting_qubits}")

    # Standardize predefined unitary types if chosen
    if unitary_type.lower() == "z":
        theta = 0.5  # Z |1> = -|1> = exp(2pi * i * 0.5) |1>
    elif unitary_type.lower() == "s":
        theta = 0.25 # S |1> = i |1> = exp(2pi * i * 0.25) |1>
    elif unitary_type.lower() == "t":
        theta = 0.125 # T |1> = exp(i*pi/4)|1> = exp(2pi * i * 0.125) |1>

    t = num_counting_qubits
    q_counting = QuantumRegister(t, name="c_qubit")
    q_target = QuantumRegister(1, name="target")
    
    if include_measurements:
        c_reg = ClassicalRegister(t, name="meas")
        qc = QuantumCircuit(q_counting, q_target, c_reg, name=f"QPE_theta_{theta:.4f}")
    else:
        qc = QuantumCircuit(q_counting, q_target, name=f"QPE_theta_{theta:.4f}")

    target_idx = t  # Target qubit index

    # Stage 1: Eigenstate Preparation
    # For Phase gate P(lambda) = [[1, 0], [0, exp(i*lambda)]]:
    # P(lambda)|0> = 1|0>, eigenvalue = 1 = exp(2pi*i*0) -> phase 0
    # P(lambda)|1> = exp(i*lambda)|1> -> phase theta = lambda / (2*pi)
    if prepare_eigenstate:
        qc.x(target_idx)

    if insert_barriers:
        qc.barrier()

    # Stage 2: Superposition of Counting Qubits
    for i in range(t):
        qc.h(i)

    if insert_barriers:
        qc.barrier()

    # Stage 3: Controlled-U^(2^j) Operations (Phase Kickback)
    for j in range(t):
        power = 2 ** j
        controlled_angle = 2.0 * np.pi * theta * power
        # Apply controlled phase gate CP(controlled_angle)
        qc.cp(controlled_angle, j, target_idx)

    if insert_barriers:
        qc.barrier()

    # Stage 4: Inverse Quantum Fourier Transform
    iqft_circuit = create_inverse_qft(t, insert_barriers=False)
    qc = qc.compose(iqft_circuit, qubits=range(t))

    if insert_barriers:
        qc.barrier()

    # Stage 5: Measurement of Counting Qubits
    if include_measurements:
        qc.measure(range(t), range(t))

    return qc


def get_circuit_metadata(qc: QuantumCircuit) -> Dict[str, Any]:
    """
    Extracts educational and architectural metrics from the quantum circuit.
    """
    gate_counts = dict(qc.count_ops())
    return {
        "num_qubits": qc.num_qubits,
        "num_clbits": qc.num_clbits,
        "depth": qc.depth(),
        "gate_counts": gate_counts,
        "total_gates": sum(gate_counts.values()),
        "has_measurements": "measure" in gate_counts,
    }
