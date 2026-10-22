# Implementation of Quantum Phase Estimation (QPE) Algorithm for Different Cases

**M.Tech Computer Science and Engineering Academic Project**  
**Environment:** macOS (Apple Silicon / ARM64 & Intel compatible) | Python 3.11 | Qiskit 2.x & Qiskit Aer | Streamlit

---

## 📖 Executive Summary

The **Quantum Phase Estimation (QPE)** algorithm is a foundational subroutine in quantum computing. Given a unitary operator $U$ and an eigenstate $|\psi\rangle$ satisfying:

$$U |\psi\rangle = e^{2\pi i \theta} |\psi\rangle, \quad \theta \in [0, 1)$$

the algorithm estimates the unknown phase parameter $\theta$ with exponential precision using $t$ counting qubits.

This project implements an end-to-end quantum computing pipeline featuring:
1. **Parameterized Quantum Phase Circuits** with controlled unitary powers $U^{2^j}$.
2. **Explicit Gate-Level Inverse Quantum Fourier Transform ($QFT^\dagger$)** with phase rotations and SWAP operations.
3. **Multi-Case Empirical Benchmarks**:
   - Exact Dyadic phases: $\theta \in \{1/2, 1/4, 1/8, 3/8\}$ (100% ideal constructive interference)
   - Non-Dyadic continuous phases: $\theta \in \{1/3, 1/5\}$ (spectral broadening and leakage)
   - Custom user-defined phases.
4. **Exponential Precision Scaling** ($t = 2$ to $8$ qubits) with empirical vs. theoretical error bounds ($\leq 1/2^t$).
5. **Noisy Intermediate-Scale Quantum (NISQ) Simulation** via Qiskit Aer depolarizing channels and readout error models.
6. **Full-Featured Interactive Web Dashboard** built with Streamlit and Plotly.

---

## 🗂️ Project Directory Structure

```text
quantum-phase-estimation/
├── app.py                      # Main Streamlit Application (Page 1: Executive Home)
├── requirements.txt            # Python dependencies (Qiskit 2.x, Aer, Streamlit, etc.)
├── README.md                   # Comprehensive academic documentation and setup guide
├── qpe/                        # Core Quantum Phase Estimation package
│   ├── __init__.py             # Module exports
│   ├── circuit.py              # QPE circuit synthesizer with eigenstate prep & controlled-U
│   ├── inverse_qft.py          # Gate-level Inverse QFT and Forward QFT implementation
│   ├── simulator.py            # AerSimulator execution, decimal decoding, and metrics
│   ├── noise.py                # NISQ noise modeling (depolarizing, thermal, readout error)
│   ├── analysis.py             # Precision scaling, case benchmarking, and entropy metrics
│   └── ui_helper.py            # Streamlit styling, Plotly charts, and session management
├── pages/                      # Multi-Page Streamlit Dashboard
│   ├── 1_🎮_QPE_Simulator.py   # Page 2: Interactive circuit builder & histogram analyzer
│   ├── 2_📊_Different_Cases.py # Page 3: Comparison table across 6+ predefined cases
│   ├── 3_📈_Precision_Analysis.py # Page 4: Error scaling vs. counting qubits (t=2..8)
│   ├── 4_🔬_Noise_Analysis.py  # Page 5: Side-by-side Ideal vs. Noisy NISQ comparison
│   └── 5_📚_Learn_QPE.py       # Page 6: Step-by-step textbook tutorial with worked examples
├── tests/                      # Automated Verification Test Suite
│   ├── __init__.py
│   └── test_qpe.py             # 14 comprehensive unit tests (all passing)
└── results/                    # Exported CSV experiment data
    ├── benchmark_different_cases_t4.csv
    └── precision_scaling_one_third.csv
```

---

## 💻 macOS Quickstart & Setup Guide

### 1. Prerequisites
Ensure Homebrew and Python 3.11 are installed on your MacBook:
```bash
brew install python@3.11
```

### 2. Create and Activate Virtual Environment
```bash
cd /Users/bakkeshymr/Freelance/Project4
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Run Automated Unit Tests
Verify all 14 tests covering exact phases, non-dyadic scaling, inverse QFT unitary equivalence, and noise models:
```bash
pytest tests/test_qpe.py -v
```

### 5. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 🔬 Mathematical & Algorithmic Background

### 1. The Phase Kickback Principle
When a controlled-$U$ gate acts on a control qubit in superposition $\frac{|0\rangle + |1\rangle}{\sqrt{2}}$ and an eigenstate $|\psi\rangle$:

$$CU \left( \frac{|0\rangle + |1\rangle}{\sqrt{2}} |\psi\rangle \right) = \left( \frac{|0\rangle + e^{2\pi i \theta} |1\rangle}{\sqrt{2}} \right) |\psi\rangle$$

The target qubit remains unchanged, while the eigenvalue phase is transferred ("kicked back") into the control qubit.

### 2. Successive Controlled Powers
Applying $U^{2^j}$ for counting qubits $j \in \{0, 1, \dots, t-1\}$ transforms the register into:

$$|\Psi\rangle = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i \theta k} |k\rangle$$

### 3. Inverse Quantum Fourier Transform ($QFT^\dagger$)
The Inverse QFT inverts the discrete Fourier transform:

$$QFT^\dagger |k\rangle = \frac{1}{\sqrt{2^t}} \sum_{j=0}^{2^t - 1} e^{-2\pi i j k / 2^t} |j\rangle$$

### 4. Exact vs. Approximate Phases
- **Exact Dyadic Phase:** If $\theta = \frac{m}{2^t}$ ($m \in \mathbb{Z}$), destructive interference eliminates all orthogonal states, yielding $P(m) = 1.0$ (100% probability).
- **Approximate Phase:** If $2^t \theta \notin \mathbb{Z}$, the measurement probability distribution follows Nielsen & Chuang Eq. (5.26):

$$P(m) = \frac{1}{2^{2t}} \frac{\sin^2(\pi(2^t \theta - m))}{\sin^2(\pi(\theta - m / 2^t))}$$

The absolute error is strictly bounded by:
$$|\theta - \tilde{\theta}| \leq \frac{1}{2^t}$$

---

## 📊 Experimental Results Summary

| Case Name | Actual $\theta$ | Counting Qubits ($t$) | Measured State | Estimated $\tilde{\theta}$ | Absolute Error | Success Prob. | Dyadic Class |
|---|---|---|---|---|---|---|---|
| Phase $\theta = 1/2$ | 0.50000 | 4 | `|1000⟩` | 0.50000 | 0.000000 | 100.0% | Exact |
| Phase $\theta = 1/4$ | 0.25000 | 4 | `|0100⟩` | 0.25000 | 0.000000 | 100.0% | Exact |
| Phase $\theta = 1/8$ | 0.12500 | 4 | `|0010⟩` | 0.12500 | 0.000000 | 100.0% | Exact |
| Phase $\theta = 3/8$ | 0.37500 | 4 | `|0110⟩` | 0.37500 | 0.000000 | 100.0% | Exact |
| Phase $\theta = 1/3$ | 0.33333 | 4 | `|0101⟩` | 0.31250 | 0.020833 | 68.4% | Approximate |
| Phase $\theta = 1/5$ | 0.20000 | 4 | `|0011⟩` | 0.18750 | 0.012500 | 73.1% | Approximate |

---

## 🛠️ Technology Stack
- **Language:** Python 3.11 (macOS Apple Silicon)
- **Quantum Computing Framework:** Qiskit 2.5.2
- **Simulation Engine:** Qiskit Aer 0.17.2 (`AerSimulator`)
- **Web Application:** Streamlit 1.65.0
- **Data & Plotting:** NumPy 2.4.6, Pandas 3.0.6, Matplotlib 3.11.2, Plotly 7.1.0
- **Test Framework:** Pytest 9.1.1
