# ⚛️ Qiskit QPE Simulator: Interactive Quantum Phase Estimation Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.x%20%7C%20Aer-6929C4?style=for-the-badge&logo=qiskit&logoColor=white)](https://qiskit.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-14%20Passed-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_qpe.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-64748B?style=for-the-badge)](run.bat)

An end-to-end, publication-grade implementation of the **Quantum Phase Estimation (QPE)** algorithm built with **Qiskit**, **Qiskit Aer**, and an interactive multi-page **Streamlit** dashboard. Includes explicit gate-level Inverse Quantum Fourier Transform ($QFT^\dagger$) decomposition, dyadic vs. continuous non-dyadic case studies, exponential precision scaling, and realistic NISQ hardware noise simulations.

---

## 📸 Visual Snapshots & Demonstrations

### 1. Quantum Circuit Architecture ($t=3$ Counting Qubits, $\theta = 1/8$)
Synthesized gate-level circuit with superposition initialization, controlled unitary powers $U^{2^j}$ phase kickback, and explicit $QFT^\dagger$ unrolling with SWAP network.

![Quantum Phase Estimation Circuit Architecture](assets/circuit_qpe.png)

---

### 2. Exponential Precision Scaling ($t = 2 \dots 8$ Qubits for $\theta = 1/3$)
Empirical phase error decay compared against theoretical Heisenberg-limited upper bound $\epsilon \le \frac{1}{2^t}$.

![Precision Scaling Curve](assets/precision_scaling.png)

---

### 3. Ideal vs. Noisy NISQ Simulation (Depolarizing & Readout Noise)
Side-by-side probability distribution contrast under noisy quantum intermediate-scale hardware regimes.

![NISQ Noise Comparison](assets/noise_comparison.png)

---

## 📖 Executive Summary

The **Quantum Phase Estimation (QPE)** algorithm is a cornerstone subroutine in quantum computing, forming the computational core of **Shor's Factoring Algorithm**, **Quantum Phase-based Matrix Inversion (HHL)**, and **Quantum Molecular Chemistry Simulations**.

Given a unitary operator $U$ and an eigenstate $|\psi\rangle$ satisfying:

$$U |\psi\rangle = e^{2\pi i \theta} |\psi\rangle, \quad \theta \in [0, 1)$$

the algorithm estimates the phase parameter $\theta$ with exponential precision using a register of $t$ counting qubits.

### Key Highlights of This Implementation:
1. **Gate-Level $QFT^\dagger$ Decomposition**: Explicit implementation of controlled phase rotations ($R_k / CPHASE$) and qubit SWAP networks without black-box library wrappers.
2. **Empirical Benchmarks**:
   - **Exact Dyadic Phases**: $\theta \in \{1/2, 1/4, 1/8, 3/8\}$ exhibiting 100% constructive interference.
   - **Non-Dyadic Continuous Phases**: $\theta \in \{1/3, 1/5\}$ demonstrating spectral leakage and sinc-like probability distributions.
3. **NISQ Noise Simulation**: Realistic modeling of depolarizing gate errors ($p_{1q}, p_{2q}$) and measurement readout errors ($P(0|1), P(1|0)$).
4. **Interactive Multi-Page Web Dashboard**: Built with Streamlit and Plotly, providing live parameter control, real-time circuit drawing, and CSV dataset export.
5. **Automated Verification**: Comprehensive PyTest suite covering 14 unit tests across unitary properties, mathematical bounds, and noise models.

---

## 📊 Empirical Benchmark Results

Below are benchmark results produced using $t = 4$ counting qubits and 8,192 measurement shots:

| Case | Fraction | Category | Actual $\theta$ | Estimated $\theta$ | Bitstring | Absolute Error | Success Prob. | Dyadic Exact |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase $\theta = 1/2$** | $1/2$ | Exact (Dyadic) | $0.50000$ | $0.50000$ | `1000` | **$0.000000$** | **100.00%** | ✅ Yes |
| **Phase $\theta = 1/4$** | $1/4$ | Exact (Dyadic) | $0.25000$ | $0.25000$ | `0100` | **$0.000000$** | **100.00%** | ✅ Yes |
| **Phase $\theta = 1/8$** | $1/8$ | Exact (Dyadic) | $0.12500$ | $0.12500$ | `0010` | **$0.000000$** | **100.00%** | ✅ Yes |
| **Phase $\theta = 3/8$** | $3/8$ | Exact (Dyadic) | $0.37500$ | $0.37500$ | `0110` | **$0.000000$** | **100.00%** | ✅ Yes |
| **Phase $\theta = 1/3$** | $1/3$ | Non-Dyadic | $0.33333$ | $0.31250$ | `0101` | **$0.020833$** | **70.02%** | ❌ No |
| **Phase $\theta = 1/5$** | $1/5$ | Non-Dyadic | $0.20000$ | $0.18750$ | `0011` | **$0.012500$** | **89.01%** | ❌ No |

---

## 🗂️ Project Architecture

```text
qiskit-qpe-simulator/
│
├── run.bat                          # 1-Click Windows Batch Launcher
├── run.ps1                          # Native Windows PowerShell Launcher
├── run_tests.bat                    # 1-Click PyTest Suite Runner
├── requirements.txt                 # Pinned dependencies (Qiskit 2.x, Aer, Streamlit, etc.)
├── LICENSE                          # MIT License
├── README.md                        # Master Documentation & Academic Report
├── PROJECT_WORK_DIVISION.md         # Team Responsibilities & Viva Speaking Script
│
├── assets/                          # High-resolution benchmark plots and circuit diagrams
│   ├── circuit_qpe.png
│   ├── precision_scaling.png
│   └── noise_comparison.png
│
├── qpe/                             # Core Quantum Phase Estimation Engine
│   ├── __init__.py
│   ├── circuit.py                   # Quantum circuit synthesis & phase kickback
│   ├── inverse_qft.py               # Explicit gate-level Inverse QFT (QFT†) & SWAPs
│   ├── simulator.py                 # AerSimulator execution & decimal phase decoding
│   ├── noise.py                     # NISQ depolarizing & readout error modeling
│   ├── analysis.py                  # Error bounds, precision scaling & Shannon entropy
│   └── ui_helper.py                 # Streamlit styling, Plotly charts & session state
│
├── pages/                           # Interactive Multi-Page Streamlit App
│   ├── 1_QPE_Simulator.py           # Live circuit builder & measurement analyzer
│   ├── 2_Different_Cases.py         # Comparative dyadic vs. non-dyadic benchmark table
│   ├── 3_Precision_Analysis.py      # Precision scaling curve analyzer (t = 2..8)
│   ├── 4_Noise_Analysis.py          # Ideal vs. Noisy NISQ comparison
│   └── 5_Learn_QPE.py               # Educational textbook tutorial with worked examples
│
├── tests/                           # Verification Test Suite
│   ├── __init__.py
│   └── test_qpe.py                  # 14 comprehensive unit tests (all passing)
│
└── results/                         # Exported CSV Datasets & Reports
    ├── benchmark_different_cases_t4.csv
    ├── precision_scaling_one_third.csv
    └── Quantum_Phase_Estimation_MTech_Report.pdf
```

---

## 💻 Quickstart & Setup Guide

### 🚀 Option 1: Windows (1-Click Launch)
Simply double-click **`run.bat`** in File Explorer, or run in PowerShell:
```powershell
.\run.ps1
```
*The launcher automatically initializes the virtual environment, verifies dependencies, and launches the web dashboard at `http://localhost:8501`.*

---

### 🐧 Option 2: Cross-Platform / macOS / Linux

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Hariprajwal/qiskit-qpe-simulator.git
   cd qiskit-qpe-simulator
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate       # On macOS / Linux
   # .\venv\Scripts\activate      # On Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run Unit Tests (14 passing tests)**:
   ```bash
   pytest tests/test_qpe.py -v
   ```

5. **Start the Interactive Dashboard**:
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## 🔬 Mathematical Foundations

### 1. Phase Kickback Principle
When a controlled-$U$ gate acts on a control qubit in equal superposition $\frac{|0\rangle + |1\rangle}{\sqrt{2}}$ and an eigenstate $|\psi\rangle$:

$$CU \left( \frac{|0\rangle + |1\rangle}{\sqrt{2}} |\psi\rangle \right) = \left( \frac{|0\rangle + e^{2\pi i \theta} |1\rangle}{\sqrt{2}} \right) |\psi\rangle$$

Applying successive controlled operations $CU^{2^j}$ for $j = 0, \dots, t-1$ encodes the binary expansion of $\theta = 0.\theta_1 \theta_2 \dots \theta_t$ into the relative phases of the counting register:

$$|\widetilde{\psi}\rangle = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t-1} e^{2\pi i \theta k} |k\rangle$$

### 2. Inverse Quantum Fourier Transform ($QFT^\dagger$)
The $QFT^\dagger$ unrolls the relative phases into computational basis states:

$$QFT^\dagger |k\rangle = \frac{1}{\sqrt{2^t}} \sum_{j=0}^{2^t-1} e^{-2\pi i j k / 2^t} |j\rangle$$

When $\theta = \frac{m}{2^t}$ is an exact dyadic fraction, destructive interference cancels all non-target states, measuring $|m\rangle$ with **100% probability**. When $\theta$ is non-dyadic, the probability distribution peaks around $\lfloor 2^t \theta \rceil$ with an empirical upper bound:

$$|\theta - \hat{\theta}| \le \frac{1}{2^t}$$

---

## 👥 Contributors & Work Allocation

- **Hariprajwal ([@Hariprajwal](https://github.com/Hariprajwal))** — Interactive Web Dashboard Development, Plotly Data Visualizations, Experimental Benchmarking Datasets (`results/*.csv`), and Analytical Scaling Curves.
- **Bakkesh ([@bakkeshymr](https://github.com/bakkeshymr))** — System Architecture Design, Core Quantum Circuit Synthesizer (`circuit.py`, `inverse_qft.py`), Aer Simulator Integration, and NISQ Noise Channels.
- **Janayath** — Automated PyTest Verification Suite (`tests/test_qpe.py`), Educational Textbook Walkthroughs, and Documentation Support.

Detailed role descriptions and presentation viva points are documented in [PROJECT_WORK_DIVISION.md](PROJECT_WORK_DIVISION.md).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for complete details.
