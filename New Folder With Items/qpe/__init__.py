import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("QISKIT_AER_PARALLEL_THREADS", "1")

import matplotlib
matplotlib.use("Agg")

from qpe.circuit import build_qpe_circuit, create_phase_unitary
from qpe.inverse_qft import create_inverse_qft
from qpe.simulator import run_qpe_simulation, estimate_phase_from_counts
from qpe.noise import create_depolarizing_noise_model, create_thermal_noise_model
from qpe.analysis import (
    calculate_qpe_metrics,
    analyze_precision_scaling,
    compare_cases,
    run_noise_comparison
)

__all__ = [
    "build_qpe_circuit",
    "create_phase_unitary",
    "create_inverse_qft",
    "run_qpe_simulation",
    "estimate_phase_from_counts",
    "create_depolarizing_noise_model",
    "create_thermal_noise_model",
    "calculate_qpe_metrics",
    "analyze_precision_scaling",
    "compare_cases",
    "run_noise_comparison",
]
