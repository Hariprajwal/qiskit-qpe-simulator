# Quantum Phase Estimation (QPE) Project
## Work Division & Component Breakdown

---

## 1. What Components Does This Project Have?

The project is an end-to-end Quantum Computing application implementing the **Quantum Phase Estimation (QPE)** algorithm using **Qiskit 2.x**, **Qiskit Aer**, and an interactive **Streamlit** dashboard.

It consists of **4 Major Components**:

```
quantum-phase-estimation/
│
├── [Component 1] Core Quantum Backend (qpe/)
│   ├── circuit.py           -> Synthesizes QPE circuits, state prep (|ψ⟩), and controlled-U^(2^j) gates
│   ├── inverse_qft.py       -> Explicit gate-level Inverse Quantum Fourier Transform (QFT†) & SWAPs
│   ├── simulator.py         -> AerSimulator backend runner, bitstring sampling, and decimal phase decoding
│   ├── noise.py             -> NISQ noise modeling (depolarizing channels, readout error)
│   └── analysis.py          -> Error metrics, Shannon entropy, theoretical bound vs empirical scaling
│
├── [Component 2] Interactive Web Dashboard (app.py & pages/)
│   ├── app.py               -> Executive landing page & project architecture overview
│   ├── 1_🎮_QPE_Simulator   -> Live circuit builder, customizable phase/qubits, Plotly probability histogram
│   ├── 2_📊_Different_Cases -> Comparative benchmark across Dyadic (1/2, 1/4, 1/8, 3/8) & Non-Dyadic (1/3, 1/5)
│   ├── 3_📈_Precision_Analysis -> Scaling curve analysis (t = 2 to 8 qubits) vs theoretical error bound (≤ 1/2^t)
│   ├── 4_🔬_Noise_Analysis  -> Side-by-side Ideal vs Noisy NISQ hardware simulation
│   ├── 5_📚_Learn_QPE       -> Step-by-step interactive textbook tutorial with phase kickback proofs
│   └── ui_helper.py         -> Glassmorphic dark-mode CSS styling, Plotly chart configs, session state
│
├── [Component 3] Experimental Datasets & Benchmark Results (results/)
│   ├── benchmark_different_cases_t4.csv -> Dataset comparing dyadic vs non-dyadic phases across metrics
│   ├── precision_scaling_one_third.csv  -> Dataset recording error decay as counting qubits increase
│   └── Visual assets (circuit_qpe.png, precision_scaling.png, noise_comparison.png)
│
└── [Component 4] Verification Test Suite & PDF Academic Report
    ├── tests/test_qpe.py    -> 14 PyTest unit tests verifying mathematical correctness
    ├── generate_report_pdf.py -> Automated ReportLab script producing 12-page M.Tech academic report
    └── Quantum_Phase_Estimation_MTech_Report.pdf -> Final formatted academic publication/report
```

---

## 2. Team Work Division (Who Did What)

| Team Member | Official Role | Primary Modules & Responsibilities |
| :--- | :--- | :--- |
| **Bakkesh** | **System Architecture & Core Quantum Lead** | • Designed overall **System Architecture** and end-to-end simulation pipeline.<br>• Built the **Core Quantum Engine** (`circuit.py`, `inverse_qft.py`): implemented phase kickback circuits and gate-level $QFT^\dagger$.<br>• Developed **NISQ Noise Model** (`noise.py`) for depolarizing and readout errors.<br>• Configured the **Aer Simulator Engine** (`simulator.py`) with thread safety and mimalloc optimization. |
| **You (Me)** | **Dashboard Developer & Experimental Dataset Lead** | • Developed the **Interactive Multi-Page Streamlit Dashboard** (`app.py`, `pages/1..5`, `ui_helper.py`).<br>• Created reactive parameter controls (qubit sliders, phase dial, shots, noise levels) and interactive **Plotly histograms & scaling charts**.<br>• Conducted experimental simulations and compiled the **Benchmark Datasets** (`results/benchmark_different_cases_t4.csv` and `results/precision_scaling_one_third.csv`).<br>• Performed statistical data analysis: verifying empirical error vs theoretical bounds ($\leq 1/2^t$) and Shannon entropy. |
| **Janayath** | **QA Testing, Tutorial Support & Documentation** | • Executed and validated the **Automated Test Suite** (`tests/test_qpe.py` - 14 unit test cases).<br>• Assisted with the **Educational & Theory Module** (`pages/5_📚_Learn_QPE.py`), verifying mathematical walkthroughs and textbook examples.<br>• Supported academic documentation, literature review, and presentation slide preparation for the project defense. |

---

## 3. How to Speak About This in Your Presentation / Viva

### 🗣️ When Describing Bakkesh's Contribution:
> *"Bakkesh was responsible for the **System Architecture and Quantum Backend**. He designed the pipeline architecture and implemented the core quantum circuit synthesis in Qiskit, including the controlled unitary powers $U^{2^j}$, the explicit gate-level Inverse Quantum Fourier Transform ($QFT^\dagger$) with phase rotations and SWAP networks, and the NISQ noise simulation models."*

### 🗣️ When Describing Your Contribution (Me):
> *"I designed and built the **Interactive Multi-Page Web Dashboard** using Streamlit and Plotly, allowing users to run real-time phase estimations, adjust qubit counts, and visualize probability distributions. Additionally, I ran the simulation experiments to generate the **Benchmark Datasets** (`benchmark_different_cases_t4.csv` and `precision_scaling_one_third.csv`), analyzing the empirical error bounds and performance trade-offs between dyadic and continuous non-dyadic phases."*

### 🗣️ When Describing Janayath's Contribution:
> *"Janayath handled **Testing, Validation, and Documentation Support**. He managed the automated unit test suite (`pytest`) ensuring all 14 test cases passed, assisted in curating the mathematical content for the educational module, and assisted in preparing the academic report and presentation materials."*
