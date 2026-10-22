"""
Comprehensive Unit Tests for Quantum Phase Estimation (QPE).

Covers:
- Exact dyadic phases (theta = 0.5, 0.25, 0.125, 0.375)
- Non-dyadic approximate phases (theta = 1/3, 1/5)
- Qubit precision scaling (t = 2 to 6)
- Inverse QFT unitary verification (QFT * IQFT == I)
- Ideal vs Noisy simulation behaviors
- Bit-ordering and endianness verification
"""

import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from qpe.circuit import build_qpe_circuit, get_circuit_metadata
from qpe.inverse_qft import create_inverse_qft, create_forward_qft
from qpe.simulator import (
    run_qpe_simulation,
    binary_to_decimal_phase,
    decimal_to_binary_fraction,
    estimate_phase_from_counts
)
from qpe.noise import create_depolarizing_noise_model, get_preset_noise_model
from qpe.analysis import (
    analyze_precision_scaling,
    compare_cases,
    calculate_theoretical_probability,
    calculate_distribution_entropy
)


def test_inverse_qft_unitary():
    """Verify that QFT * IQFT = Identity operator for various qubit counts."""
    for n in [2, 3, 4]:
        qft = create_forward_qft(n)
        iqft = create_inverse_qft(n)
        
        # Compose QFT and IQFT
        combined = QuantumCircuit(n)
        combined.compose(qft, inplace=True)
        combined.compose(iqft, inplace=True)
        
        op = Operator(combined)
        identity = Operator(np.eye(2 ** n))
        
        # Check if op is close to identity up to a global phase
        assert op.equiv(identity), f"QFT followed by IQFT is not identity for n={n}"


def test_binary_to_decimal_phase():
    """Test binary to decimal phase conversion correctness."""
    # 3 qubits: 2^3 = 8
    assert binary_to_decimal_phase("100", 3) == 4 / 8 == 0.5
    assert binary_to_decimal_phase("010", 3) == 2 / 8 == 0.25
    assert binary_to_decimal_phase("001", 3) == 1 / 8 == 0.125
    assert binary_to_decimal_phase("011", 3) == 3 / 8 == 0.375
    assert binary_to_decimal_phase("000", 3) == 0.0

    # 4 qubits: 2^4 = 16
    assert binary_to_decimal_phase("1000", 4) == 8 / 16 == 0.5
    assert binary_to_decimal_phase("0100", 4) == 4 / 16 == 0.25
    assert binary_to_decimal_phase("0010", 4) == 2 / 16 == 0.125


def test_decimal_to_binary_fraction():
    """Test decimal phase to binary fraction string conversion."""
    assert decimal_to_binary_fraction(0.5, 4) == "0.1"
    assert decimal_to_binary_fraction(0.25, 4) == "0.01"
    assert decimal_to_binary_fraction(0.125, 4) == "0.001"
    assert decimal_to_binary_fraction(0.375, 4) == "0.011"


@pytest.mark.parametrize("theta, expected_bitstring", [
    (0.5, "100"),     # 1/2 = 4/8 -> 100
    (0.25, "010"),    # 1/4 = 2/8 -> 010
    (0.125, "001"),   # 1/8 = 1/8 -> 001
    (0.375, "011"),   # 3/8 = 3/8 -> 011
])
def test_exact_phases_3_qubits_ideal(theta, expected_bitstring):
    """
    Test exact dyadic phases with 3 counting qubits in ideal simulator.
    In ideal simulation, an exact phase must be measured with 100% probability.
    """
    result = run_qpe_simulation(
        theta=theta,
        num_counting_qubits=3,
        shots=1000,
        noise_model=None
    )
    assert result.most_probable_bitstring == expected_bitstring
    assert result.estimated_phase == theta
    assert result.absolute_error == 0.0
    assert result.success_probability == 1.0
    assert result.is_exact_phase is True


def test_theta_one_third_precision_scaling():
    """
    Test theta = 1/3 ~ 0.333333 with different counting qubits (3, 4, 5, 6).
    The absolute error must strictly stay within theoretical bound 1 / 2^t.
    """
    theta = 1.0 / 3.0
    for t in [3, 4, 5, 6]:
        result = run_qpe_simulation(
            theta=theta,
            num_counting_qubits=t,
            shots=1000,
            noise_model=None
        )
        bound = 1.0 / (2 ** t)
        assert result.absolute_error <= bound, (
            f"Error {result.absolute_error} exceeded bound {bound} for t={t}"
        )
        assert result.is_exact_phase is False


def test_theta_one_fifth_precision_scaling():
    """
    Test theta = 1/5 = 0.2 with different counting qubits (3, 4, 5, 6).
    """
    theta = 0.2
    for t in [3, 4, 5, 6]:
        result = run_qpe_simulation(
            theta=theta,
            num_counting_qubits=t,
            shots=1000,
            noise_model=None
        )
        bound = 1.0 / (2 ** t)
        assert result.absolute_error <= bound, (
            f"Error {result.absolute_error} exceeded bound {bound} for t={t}"
        )


def test_noisy_simulation_behavior():
    """
    Test that noisy simulation retains the correct peak state but exhibits
    lower success probability and higher distribution entropy due to noise.
    """
    theta = 0.25
    noise_model = create_depolarizing_noise_model(p_1q=0.01, p_2q=0.03, p_readout=0.03)
    
    ideal_result = run_qpe_simulation(theta=theta, num_counting_qubits=3, shots=2000, noise_model=None)
    noisy_result = run_qpe_simulation(theta=theta, num_counting_qubits=3, shots=2000, noise_model=noise_model)
    
    # Peak state should still be correct
    assert noisy_result.most_probable_bitstring == "010"
    
    # Success probability drops under noise
    assert noisy_result.success_probability < ideal_result.success_probability
    assert noisy_result.success_probability > 0.60  # Still clearly distinguishable
    
    # Entropy increases under noise
    ideal_entropy = calculate_distribution_entropy(ideal_result.probabilities)
    noisy_entropy = calculate_distribution_entropy(noisy_result.probabilities)
    assert ideal_entropy == 0.0
    assert noisy_entropy > 0.0


def test_circuit_metadata():
    """Verify circuit metadata extraction."""
    qc = build_qpe_circuit(theta=0.25, num_counting_qubits=3)
    meta = get_circuit_metadata(qc)
    assert meta["num_qubits"] == 4  # 3 counting + 1 target
    assert meta["num_clbits"] == 3
    assert meta["has_measurements"] is True
    assert meta["depth"] > 0


def test_compare_cases_dataframe():
    """Verify that compare_cases generates a valid DataFrame with all predefined cases."""
    df = compare_cases(num_counting_qubits=3, shots=500, custom_theta=0.15)
    assert len(df) == 7  # 6 predefined + 1 custom
    assert "Case Name" in df.columns
    assert "Estimated θ" in df.columns
    assert "Success Probability" in df.columns


def test_precision_scaling_dataframe():
    """Verify analyze_precision_scaling output structure."""
    df = analyze_precision_scaling(theta=0.333333, min_qubits=2, max_qubits=5, shots=500)
    assert len(df) == 4
    assert list(df["Counting Qubits (t)"]) == [2, 3, 4, 5]
    # Check that theoretical error strictly decreases
    bounds = list(df["Theoretical Error Bound (1/2^t)"])
    assert bounds == sorted(bounds, reverse=True)


def test_theoretical_probability_formula():
    """Verify analytical formula from Nielsen & Chuang."""
    # When 2^t * theta = integer m, probability must be 1.0
    prob_exact = calculate_theoretical_probability(theta=0.25, num_qubits=3, m=2)
    assert np.isclose(prob_exact, 1.0)
    
    # Orthogonal states must have zero probability
    prob_zero = calculate_theoretical_probability(theta=0.25, num_qubits=3, m=1)
    assert np.isclose(prob_zero, 0.0, atol=1e-10)
