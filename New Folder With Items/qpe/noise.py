"""
Noise Models Module for Noisy Quantum Simulation.

Implements realistic NISQ (Noisy Intermediate-Scale Quantum) device noise models
using Qiskit Aer, including:
1. Depolarizing error (single-qubit and two-qubit gate errors)
2. Readout (measurement bit-flip) errors
3. Thermal relaxation errors (T1 and T2 decoherence)
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    ReadoutError,
    thermal_relaxation_error
)


def create_depolarizing_noise_model(
    p_1q: float = 0.005,
    p_2q: float = 0.02,
    p_readout: float = 0.02
) -> NoiseModel:
    """
    Creates a depolarizing noise model with readout error.

    Parameters:
        p_1q: Probability of depolarizing error on 1-qubit gates (h, x, p, u).
        p_2q: Probability of depolarizing error on 2-qubit gates (cp, cx, swap).
        p_readout: Measurement readout error probability (0 -> 1 or 1 -> 0).

    Returns:
        NoiseModel: Configured Qiskit Aer NoiseModel instance.
    """
    noise_model = NoiseModel()

    # 1-Qubit Gate Depolarizing Error
    if p_1q > 0:
        error_1q = depolarizing_error(p_1q, 1)
        noise_model.add_all_qubit_quantum_error(error_1q, ["u", "p", "h", "x"])

    # 2-Qubit Gate Depolarizing Error
    if p_2q > 0:
        error_2q = depolarizing_error(p_2q, 2)
        noise_model.add_all_qubit_quantum_error(error_2q, ["cp", "cx", "swap"])

    # Readout / Measurement Error
    if p_readout > 0:
        p0_given_1 = p_readout
        p1_given_0 = p_readout
        readout_err = ReadoutError([
            [1.0 - p1_given_0, p1_given_0],
            [p0_given_1, 1.0 - p0_given_1]
        ])
        noise_model.add_all_qubit_readout_error(readout_err)

    return noise_model


def create_thermal_noise_model(
    t1_ns: float = 50000.0,
    t2_ns: float = 70000.0,
    time_1q_ns: float = 50.0,
    time_2q_ns: float = 300.0,
    p_readout: float = 0.02
) -> NoiseModel:
    """
    Creates a realistic thermal relaxation noise model (T1 relaxation and T2 dephasing).

    Parameters:
        t1_ns: Qubit relaxation time T1 in nanoseconds.
        t2_ns: Qubit dephasing time T2 in nanoseconds (must be <= 2 * T1).
        time_1q_ns: Duration of single-qubit gates in nanoseconds.
        time_2q_ns: Duration of two-qubit gates in nanoseconds.
        p_readout: Readout error probability.

    Returns:
        NoiseModel: Thermal relaxation noise model.
    """
    # Enforce physical constraint T2 <= 2 * T1
    if t2_ns > 2 * t1_ns:
        t2_ns = 2 * t1_ns

    noise_model = NoiseModel()

    # 1-qubit thermal relaxation error
    error_1q = thermal_relaxation_error(t1_ns, t2_ns, time_1q_ns)
    noise_model.add_all_qubit_quantum_error(error_1q, ["u", "p", "h", "x"])

    # 2-qubit thermal relaxation error (applied to each qubit during the gate)
    error_2q_single = thermal_relaxation_error(t1_ns, t2_ns, time_2q_ns)
    error_2q = error_2q_single.tensor(error_2q_single)
    noise_model.add_all_qubit_quantum_error(error_2q, ["cp", "cx", "swap"])

    if p_readout > 0:
        readout_err = ReadoutError([
            [1.0 - p_readout, p_readout],
            [p_readout, 1.0 - p_readout]
        ])
        noise_model.add_all_qubit_readout_error(readout_err)

    return noise_model


# Standard Presets for Academic Demos
NOISE_PRESETS: Dict[str, Dict[str, Any]] = {
    "Low Noise (Modern Superconducting)": {
        "p_1q": 0.001,
        "p_2q": 0.008,
        "p_readout": 0.01,
        "description": "Representative of recent IBM Heron / Eagle superconducting chips."
    },
    "Medium Noise (Standard NISQ)": {
        "p_1q": 0.008,
        "p_2q": 0.03,
        "p_readout": 0.03,
        "description": "Representative of typical NISQ quantum hardware."
    },
    "High Noise (Educational Stress Test)": {
        "p_1q": 0.025,
        "p_2q": 0.08,
        "p_readout": 0.06,
        "description": "Exaggerated noise profile to clearly show decoherence and peak flattening."
    }
}


def get_preset_noise_model(preset_name: str) -> NoiseModel:
    """Retrieves a configured NoiseModel from one of the standard presets."""
    if preset_name not in NOISE_PRESETS:
        preset_name = "Medium Noise (Standard NISQ)"
    config = NOISE_PRESETS[preset_name]
    return create_depolarizing_noise_model(
        p_1q=config["p_1q"],
        p_2q=config["p_2q"],
        p_readout=config["p_readout"]
    )
