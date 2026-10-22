"""
Implementation of Quantum Phase Estimation (QPE) Algorithm for Different Cases
M.Tech Computer Science & Engineering Academic Project

Main Application Landing Page (Home)
"""

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("QISKIT_AER_PARALLEL_THREADS", "1")

import matplotlib
matplotlib.use("Agg")  # Thread-safe headless backend for macOS Apple Silicon
import streamlit as st

# Pre-initialize Qiskit Rust allocator (mimalloc) and Aer on main thread to prevent worker thread SIGSEGV
import qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import qpe

try:
    _qc_warm = QuantumCircuit(1)
    _qc_warm.x(0)
    _sim_warm = AerSimulator(max_parallel_threads=1)
    _sim_warm.run(_qc_warm, shots=1)
except Exception:
    pass

from qpe.ui_helper import apply_custom_css, initialize_session_history

# Page configuration
st.set_page_config(
    page_title="Quantum Phase Estimation (QPE) | M.Tech CSE",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom dark-mode styling and typography
apply_custom_css()
initialize_session_history()

# Hero Header
st.markdown(
    """
    <div class="qpe-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <span class="qpe-badge-exact" style="margin-bottom: 8px;">M.Tech CSE Capstone Project</span>
                <h1>Implementation of Quantum Phase Estimation (QPE)</h1>
                <p>A rigorous investigation of quantum phase estimation across exact dyadic, non-dyadic, ideal, and noisy regimes.</p>
            </div>
            <div style="text-align: right; margin-top: 8px;">
                <span style="color: #94A3B8; font-size: 0.85rem;">Platform: <b>macOS Apple Silicon</b></span><br>
                <span style="color: #94A3B8; font-size: 0.85rem;">Engine: <b>Qiskit 2.x & Qiskit Aer</b></span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Overview columns
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 🎯 Executive Abstract & Objective")
    st.write(
        """
        The **Quantum Phase Estimation (QPE)** algorithm is one of the most foundational subroutines in quantum computation.
        Given a unitary operator $U$ and an eigenstate $|\\psi\\rangle$ satisfying:
        """
    )
    st.latex(r"U |\psi\rangle = e^{2\pi i \theta} |\psi\rangle, \quad \theta \in [0, 1)")
    st.write(
        """
        The primary objective of this project is to construct, simulate, and analyze the QPE algorithm using **Qiskit** and **Qiskit Aer**
        to estimate the unknown phase $\\theta$ across diverse experimental configurations:
        """
    )
    
    st.markdown(
        """
        - **Counting Register Superposition:** Using Hadamard transformations on $t$ counting qubits.
        - **Phase Kickback:** Harnessing controlled unitary powers $U^{2^j}$ to encode binary phase fractions into relative phase amplitudes.
        - **Inverse Quantum Fourier Transform ($QFT^\\dagger$):** Synthesizing gate-level rotations and SWAPs to convert phase amplitudes back to the computational basis.
        - **Multi-Case Investigation:** Evaluating exact dyadic phases ($\\theta = 1/2, 1/4, 1/8, 3/8$) vs. non-dyadic approximations ($\\theta = 1/3, 1/5$).
        - **Precision & Error Scaling:** Characterizing exponential error bounds $\\leq 1/2^t$ for $t \\in [2, 8]$.
        - **Realistic NISQ Noise Modeling:** Analyzing depolarizing channel degradation and readout errors.
        """
    )

    st.markdown("### 📐 Core Mathematical Principle")
    st.markdown(
        """
        <div class="qpe-concept-box">
            <b>The Phase Kickback Mechanism:</b><br>
            When a controlled-$U$ gate is applied with control qubit in state $\\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$ 
            and target in eigenstate $|\\psi\\rangle$, the eigenvalue $e^{2\\pi i \\theta}$ is "kicked back" into the phase of the control qubit:
        </div>
        """,
        unsafe_allow_html=True
    )
    st.latex(r"\frac{|0\rangle + |1\rangle}{\sqrt{2}} |\psi\rangle \xrightarrow{\text{Controlled-}U^{2^j}} \frac{|0\rangle + e^{2\pi i 2^j \theta} |1\rangle}{\sqrt{2}} |\psi\rangle")
    st.write(
        """
        Applying this successively for $j = 0, 1, \\dots, t-1$ prepares the counting register in the state:
        """
    )
    st.latex(r"|\tilde{\phi}\rangle = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i \theta k} |k\rangle")
    st.write(
        """
        The **Inverse QFT** directly inverts this discrete Fourier transform, projecting the state onto the closest integer $|2^t \\theta\\rangle$.
        """
    )

with col_right:
    st.markdown("### 🚀 Module Navigation")
    
    st.markdown(
        """
        <div class="qpe-metric-card" style="text-align: left; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #F8FAFC;">🎮 1. QPE Simulator</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Run live quantum circuits with customizable phases, counting qubits (2–8), and shot counts. Inspect gate diagrams and measurement distributions.</div>
        </div>
        
        <div class="qpe-metric-card" style="text-align: left; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #F8FAFC;">📊 2. Different Cases Benchmark</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Direct comparative study of θ = 1/2, 1/4, 1/8, 3/8, 1/3, 1/5 and custom inputs. Benchmarking exact dyadic vs. continuous spectral leakage.</div>
        </div>

        <div class="qpe-metric-card" style="text-align: left; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #F8FAFC;">📈 3. Precision Scaling Analysis</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Empirical scaling curves showing exponential error decrease (1/2^t) and success probability convergence as qubits scale from 2 to 8.</div>
        </div>

        <div class="qpe-metric-card" style="text-align: left; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #F8FAFC;">🔬 4. Ideal vs. Noisy Simulation</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Side-by-side NISQ device simulation with depolarizing error, readout bit-flips, and Shannon entropy analysis.</div>
        </div>

        <div class="qpe-metric-card" style="text-align: left; margin-bottom: 12px;">
            <div style="font-weight: 600; color: #F8FAFC;">📚 5. Learn QPE (Interactive Tutorial)</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Complete pedagogical walkthrough with circuit step-by-step breakdowns, manual calculations, and applications in Shor's and HHL algorithms.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🌐 Key Quantum Applications")
    st.info(
        """
        - **Shor's Factoring Algorithm:** Uses QPE for period finding to break RSA cryptography in polynomial time $O((\\log N)^3)$.
        - **Quantum Chemistry & Materials:** Estimates ground-state energies and molecular Hamiltonians ($U = e^{-iHt}$).
        - **HHL Linear Systems Algorithm:** Estimates eigenvalues of Hermitian matrices for exponential matrix inversion speedups.
        """
    )

    st.markdown("### 📄 Project Reports & Presentation Guide")
    import os
    pdf_report_path = "Quantum_Phase_Estimation_MTech_Report.pdf"
    if os.path.exists(pdf_report_path):
        with open(pdf_report_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📥 Download Academic Report (PDF)",
            data=pdf_bytes,
            file_name="Quantum_Phase_Estimation_MTech_Report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    viva_guide_path = "QPE_Execution_and_Viva_Guide.pdf"
    if os.path.exists(viva_guide_path):
        with open(viva_guide_path, "rb") as f:
            viva_bytes = f.read()
        st.download_button(
            label="🎯 Download Viva Presentation Guide (PDF)",
            data=viva_bytes,
            file_name="QPE_Execution_and_Viva_Guide.pdf",
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )

# Footer
st.divider()
st.caption("M.Tech CSE Project — Quantum Phase Estimation Implementation & Analysis | macOS Apple Silicon | Powered by Qiskit & Streamlit")
