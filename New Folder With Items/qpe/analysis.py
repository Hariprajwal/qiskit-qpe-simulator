"""
Comprehensive Analysis Module for Quantum Phase Estimation (QPE).

Includes:
1. Multi-case experimental comparison (dyadic vs non-dyadic phases).
2. Precision scaling across counting qubits (t = 2 to 8).
3. Theoretical probability distributions (Nielsen & Chuang analytical formula).
4. Ideal vs Noisy comparative benchmarks.
5. Shannon entropy and dispersion metrics.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from qiskit_aer.noise import NoiseModel

from qpe.simulator import run_qpe_simulation, QPEResult, decimal_to_binary_fraction


PREDEFINED_CASES = [
    {
        "name": "Phase θ = 1/2",
        "theta": 0.5,
        "fraction_str": "1/2",
        "category": "Exact (Dyadic)",
        "description": "Corresponds to Pauli-Z gate eigenstate phase. Exactly representable with ≥ 1 qubit."
    },
    {
        "name": "Phase θ = 1/4",
        "theta": 0.25,
        "fraction_str": "1/4",
        "category": "Exact (Dyadic)",
        "description": "Corresponds to S gate eigenstate phase. Exactly representable with ≥ 2 qubits."
    },
    {
        "name": "Phase θ = 1/8",
        "theta": 0.125,
        "fraction_str": "1/8",
        "category": "Exact (Dyadic)",
        "description": "Corresponds to T gate eigenstate phase. Exactly representable with ≥ 3 qubits."
    },
    {
        "name": "Phase θ = 3/8",
        "theta": 0.375,
        "fraction_str": "3/8",
        "category": "Exact (Dyadic)",
        "description": "Binary expansion 0.011_2. Exactly representable with ≥ 3 qubits."
    },
    {
        "name": "Phase θ = 1/3",
        "theta": 1.0 / 3.0,
        "fraction_str": "1/3",
        "category": "Approximate (Non-dyadic)",
        "description": "Repeating binary expansion 0.010101..._2. Demonstrates quantum leakage and broadening."
    },
    {
        "name": "Phase θ = 1/5",
        "theta": 0.2,
        "fraction_str": "1/5",
        "category": "Approximate (Non-dyadic)",
        "description": "Repeating binary expansion 0.00110011..._2. Requires higher counting qubits for convergence."
    }
]


def calculate_theoretical_probability(theta: float, num_qubits: int, m: int) -> float:
    """
    Computes the theoretical measurement probability of state |m> using
    the analytical formula derived in Nielsen & Chuang (Equation 5.26):

        P(m) = (1 / 2^(2t)) * [ sin^2(pi * (2^t * theta - m)) / sin^2(pi * (theta - m / 2^t)) ]

    When 2^t * theta = m exactly, P(m) = 1.0.
    """
    two_t = 2 ** num_qubits
    delta = two_t * theta - m

    if np.isclose(delta, 0.0, atol=1e-12):
        return 1.0

    numerator = np.sin(np.pi * delta) ** 2
    denom_arg = np.pi * (theta - m / two_t)
    denominator = (two_t ** 2) * (np.sin(denom_arg) ** 2)

    if np.isclose(denominator, 0.0, atol=1e-14):
        return 1.0

    return float(numerator / denominator)


def calculate_distribution_entropy(probabilities: Dict[str, float]) -> float:
    """
    Calculates the Shannon Entropy H = - sum(p * log2(p)) of the measurement distribution.
    A purely deterministic distribution (exact dyadic phase in ideal simulator) has H = 0.
    A broadened or noisy distribution has higher entropy.
    """
    entropy = 0.0
    for p in probabilities.values():
        if p > 1e-12:
            entropy -= p * np.log2(p)
    return float(entropy)


def calculate_qpe_metrics(result: QPEResult) -> Dict[str, Any]:
    """
    Calculates detailed metrics for a single simulation result.
    """
    theoretical_bound = 1.0 / (2 ** result.num_counting_qubits)
    entropy = calculate_distribution_entropy(result.probabilities)
    
    return {
        "actual_phase": result.actual_phase,
        "estimated_phase": result.estimated_phase,
        "absolute_error": result.absolute_error,
        "relative_error_pct": result.relative_error * 100.0,
        "success_probability": result.success_probability,
        "theoretical_error_bound": theoretical_bound,
        "shannon_entropy": entropy,
        "is_within_bound": result.absolute_error <= theoretical_bound,
        "is_exact_phase": result.is_exact_phase,
        "binary_representation": decimal_to_binary_fraction(result.actual_phase, result.num_counting_qubits)
    }


def compare_cases(
    num_counting_qubits: int = 4,
    shots: int = 2048,
    noise_model: Optional[NoiseModel] = None,
    custom_theta: Optional[float] = None
) -> pd.DataFrame:
    """
    Executes QPE for all predefined experimental cases plus an optional custom phase.
    Returns a benchmark DataFrame.
    """
    cases = list(PREDEFINED_CASES)
    if custom_theta is not None and 0.0 <= custom_theta < 1.0:
        cases.append({
            "name": f"Custom θ = {custom_theta:.4f}",
            "theta": custom_theta,
            "fraction_str": f"{custom_theta:.4f}",
            "category": "Custom",
            "description": "User-defined experimental phase."
        })

    records = []
    for case in cases:
        theta = case["theta"]
        res = run_qpe_simulation(
            theta=theta,
            num_counting_qubits=num_counting_qubits,
            shots=shots,
            noise_model=noise_model
        )
        metrics = calculate_qpe_metrics(res)

        records.append({
            "Case Name": case["name"],
            "Fraction": case["fraction_str"],
            "Category": case["category"],
            "Actual θ": round(theta, 5),
            "Estimated θ": round(res.estimated_phase, 5),
            "Measured Bitstring": res.most_probable_bitstring,
            "Absolute Error": f"{metrics['absolute_error']:.6f}",
            "Success Probability": f"{metrics['success_probability'] * 100:.2f}%",
            "Entropy (bits)": f"{metrics['shannon_entropy']:.3f}",
            "Exact Dyadic": "Yes" if res.is_exact_phase else "No",
        })

    return pd.DataFrame(records)


def analyze_precision_scaling(
    theta: float,
    min_qubits: int = 2,
    max_qubits: int = 8,
    shots: int = 2048,
    noise_model: Optional[NoiseModel] = None
) -> pd.DataFrame:
    """
    Sweeps counting qubits from min_qubits to max_qubits to evaluate precision scaling.
    Returns a DataFrame containing empirical error, theoretical bound, and success probability.
    """
    records = []
    for t in range(min_qubits, max_qubits + 1):
        res = run_qpe_simulation(
            theta=theta,
            num_counting_qubits=t,
            shots=shots,
            noise_model=noise_model
        )
        metrics = calculate_qpe_metrics(res)
        theoretical_bound = 1.0 / (2 ** t)

        records.append({
            "Counting Qubits (t)": t,
            "Total States (2^t)": 2 ** t,
            "Actual Phase": round(theta, 6),
            "Estimated Phase": round(res.estimated_phase, 6),
            "Measured State": res.most_probable_bitstring,
            "Absolute Error": metrics["absolute_error"],
            "Theoretical Error Bound (1/2^t)": theoretical_bound,
            "Success Probability (%)": res.success_probability * 100.0,
            "Entropy": metrics["shannon_entropy"],
            "Is Exact": res.is_exact_phase
        })

    return pd.DataFrame(records)


def run_noise_comparison(
    theta: float,
    num_counting_qubits: int = 4,
    shots: int = 2048,
    noise_model: Optional[NoiseModel] = None
) -> Dict[str, Any]:
    """
    Runs identical QPE circuits under both Ideal and Noisy conditions
    and computes a side-by-side comparative analysis.
    """
    ideal_res = run_qpe_simulation(
        theta=theta,
        num_counting_qubits=num_counting_qubits,
        shots=shots,
        noise_model=None
    )
    noisy_res = run_qpe_simulation(
        theta=theta,
        num_counting_qubits=num_counting_qubits,
        shots=shots,
        noise_model=noise_model
    )

    ideal_metrics = calculate_qpe_metrics(ideal_res)
    noisy_metrics = calculate_qpe_metrics(noisy_res)

    comparison_table = pd.DataFrame([
        {
            "Metric": "Estimated Phase",
            "Ideal Simulator": f"{ideal_res.estimated_phase:.6f}",
            "Noisy Simulator": f"{noisy_res.estimated_phase:.6f}",
            "Difference": f"{abs(ideal_res.estimated_phase - noisy_res.estimated_phase):.6f}"
        },
        {
            "Metric": "Most Probable Bitstring",
            "Ideal Simulator": ideal_res.most_probable_bitstring,
            "Noisy Simulator": noisy_res.most_probable_bitstring,
            "Difference": "Matched" if ideal_res.most_probable_bitstring == noisy_res.most_probable_bitstring else "Mismatched"
        },
        {
            "Metric": "Absolute Error",
            "Ideal Simulator": f"{ideal_metrics['absolute_error']:.6f}",
            "Noisy Simulator": f"{noisy_metrics['absolute_error']:.6f}",
            "Difference": f"{abs(ideal_metrics['absolute_error'] - noisy_metrics['absolute_error']):.6f}"
        },
        {
            "Metric": "Peak State Probability",
            "Ideal Simulator": f"{ideal_res.success_probability * 100:.2f}%",
            "Noisy Simulator": f"{noisy_res.success_probability * 100:.2f}%",
            "Difference": f"{(ideal_res.success_probability - noisy_res.success_probability) * 100:.2f}% drop"
        },
        {
            "Metric": "Shannon Entropy (bits)",
            "Ideal Simulator": f"{ideal_metrics['shannon_entropy']:.3f}",
            "Noisy Simulator": f"{noisy_metrics['shannon_entropy']:.3f}",
            "Difference": f"{noisy_metrics['shannon_entropy'] - ideal_metrics['shannon_entropy']:+.3f}"
        },
        {
            "Metric": "Active Basis States Measured",
            "Ideal Simulator": len(ideal_res.raw_counts),
            "Noisy Simulator": len(noisy_res.raw_counts),
            "Difference": f"+{len(noisy_res.raw_counts) - len(ideal_res.raw_counts)} noisy leakage states"
        }
    ])

    return {
        "ideal_result": ideal_res,
        "noisy_result": noisy_res,
        "comparison_table": comparison_table,
    }
