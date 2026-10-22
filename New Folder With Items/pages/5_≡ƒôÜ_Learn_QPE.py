"""
Page 5: Learn QPE - Comprehensive Educational Guide & Worked Examples
M.Tech CSE Academic Project
"""

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("QISKIT_AER_PARALLEL_THREADS", "1")

import matplotlib
matplotlib.use("Agg")
import streamlit as st
from qpe.ui_helper import apply_custom_css

st.set_page_config(page_title="Learn QPE | M.Tech CSE", page_icon="📚", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="qpe-hero">
        <h1>📚 Complete Guide to Quantum Phase Estimation (QPE)</h1>
        <p>A step-by-step textbook tutorial covering quantum phase kickback, inverse Fourier transforms, mathematical derivations, and worked examples.</p>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🧩 Step-by-Step Algorithm",
    "📐 Mathematical Derivation",
    "✏️ Worked Examples",
    "🌍 Real-World Applications"
])

with tab1:
    st.markdown("### The 6 Core Steps of Quantum Phase Estimation")

    st.markdown(
        r"""
        #### Step 1: System Definition & Eigenstate Setup
        We are given an unknown unitary operator $U$ and one of its eigenstates $|\psi\rangle$.
        Any unitary operator has eigenvalues on the complex unit circle:
        $$U |\psi\rangle = e^{2\pi i \theta} |\psi\rangle, \quad \theta \in [0, 1)$$
        Our goal is to determine the unknown phase $\theta$ to $t$ bits of precision.
        We initialize:
        - A **counting register** of $t$ qubits initialized to $|0\rangle^{\otimes t}$.
        - A **target register** prepared in the eigenstate $|\psi\rangle$ (e.g., via a Pauli-$X$ gate for $P(\lambda)$).

        #### Step 2: Equal Superposition
        Apply a Hadamard ($H$) gate to every counting qubit:
        $$|0\rangle^{\otimes t} |\psi\rangle \xrightarrow{H^{\otimes t}} \left( \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} |k\rangle \right) |\psi\rangle$$
        All $2^t$ computational basis states are now in equal superposition with zero relative phase.

        #### Step 3: Phase Kickback via Controlled-$U^{2^j}$
        For each counting qubit $j \in \{0, 1, \dots, t-1\}$, we apply a controlled-$U^{2^j}$ operation targeting $|\psi\rangle$.
        Since $U^{2^j} |\psi\rangle = e^{2\pi i 2^j \theta} |\psi\rangle$, the eigenvalue phase is kicked back into the control qubit:
        $$\frac{|0\rangle + |1\rangle}{\sqrt{2}} |\psi\rangle \xrightarrow{\text{Controlled-}U^{2^j}} \frac{|0\rangle + e^{2\pi i 2^j \theta} |1\rangle}{\sqrt{2}} |\psi\rangle$$
        After applying this across all $t$ qubits, the combined state becomes:
        $$|\Psi_3\rangle = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i \theta k} |k\rangle |\psi\rangle$$
        Notice that the target state $|\psi\rangle$ remains completely unentangled and unchanged! The phase information is entirely encoded in the counting register.

        #### Step 4: Inverse Quantum Fourier Transform ($QFT^\dagger$)
        The state of the counting register is exactly the discrete Fourier transform of the binary fraction representation of $\theta$.
        Applying the **Inverse QFT** ($QFT^\dagger$) converts the relative phase encoding back into computational basis states:
        $$|\Psi_4\rangle = QFT^\dagger \left( \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i \theta k} |k\rangle \right) |\psi\rangle = |\tilde{\theta}\rangle |\psi\rangle$$

        #### Step 5: Quantum Measurement
        We measure the $t$ counting qubits in the computational standard basis $\{|0\rangle, |1\rangle\}$.
        The quantum state collapses to a binary bitstring $b = b_{t-1} b_{t-2} \dots b_0$.

        #### Step 6: Binary-to-Decimal Phase Extraction
        Convert the measured binary integer $x = \text{int}(b, 2)$ to decimal phase:
        $$\tilde{\theta} = \frac{x}{2^t} = \frac{b_{t-1} 2^{t-1} + \dots + b_0 2^0}{2^t}$$
        """
    )

with tab2:
    st.markdown("### Deep Mathematical Formulation")
    
    st.markdown("#### 1. Why Phase Kickback Happens")
    st.write(
        r"""
        Consider a 2-qubit state where the control is in superposition $\frac{|0\rangle + |1\rangle}{\sqrt{2}}$ 
        and the target is an eigenstate $|\psi\rangle$ of $U$ with eigenvalue $e^{i\phi}$:
        """
    )
    st.latex(r"|\psi_{\text{in}}\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} \otimes |\psi\rangle = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{1}{\sqrt{2}} |1\rangle |\psi\rangle")
    st.write("Applying controlled-$U$:")
    st.latex(r"CU |\psi_{\text{in}}\rangle = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{1}{\sqrt{2}} |1\rangle (U |\psi\rangle) = \frac{1}{\sqrt{2}} |0\rangle |\psi\rangle + \frac{1}{\sqrt{2}} e^{i\phi} |1\rangle |\psi\rangle")
    st.write("Factoring out $|\psi\rangle$:")
    st.latex(r"= \left( \frac{|0\rangle + e^{i\phi} |1\rangle}{\sqrt{2}} \right) |\psi\rangle")
    st.info("The eigenvalue phase $e^{i\phi}$ has shifted completely into the relative phase of the control qubit. This is the **Phase Kickback Principle**.")

    st.markdown("#### 2. The Inverse QFT Action")
    st.write(
        """
        The standard QFT operator is defined as:
        """
    )
    st.latex(r"QFT |j\rangle = \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i j k / 2^t} |k\rangle")
    st.write("Its Hermitian adjoint (Inverse QFT) is:")
    st.latex(r"QFT^\dagger |k\rangle = \frac{1}{\sqrt{2^t}} \sum_{j=0}^{2^t - 1} e^{-2\pi i j k / 2^t} |j\rangle")
    st.write(
        """
        If $\\theta$ is an exact dyadic rational, $\\theta = \\frac{m}{2^t}$, then:
        """
    )
    st.latex(r"QFT^\dagger \left( \frac{1}{\sqrt{2^t}} \sum_{k=0}^{2^t - 1} e^{2\pi i (m/2^t) k} |k\rangle \right) = |m\rangle")
    st.write("All interference cancels perfectly except for basis state $|m\\rangle$, giving $P(m) = 1.0$.")

with tab3:
    st.markdown("### Step-by-Step Worked Examples")

    st.markdown(
        """
        <div class="qpe-concept-box">
            <b>Worked Example 1: Exact Phase θ = 1/4 with t = 2 Counting Qubits</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write(
        r"""
        Let unitary $U = S$ gate:
        $$S = \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}, \quad S|1\rangle = i|1\rangle = e^{i \pi/2} |1\rangle = e^{2\pi i (0.25)} |1\rangle$$
        Here, $\theta = 0.25 = 1/4$.
        With $t=2$ counting qubits, $2^t \cdot \theta = 4 \cdot (0.25) = 1$.
        In binary, $1 = 01_2$.

        1. **Initial state:** $|00\rangle |1\rangle$
        2. **After Hadamards on counting qubits:**
           $$\frac{1}{2} (|00\rangle + |01\rangle + |10\rangle + |11\rangle) |1\rangle$$
        3. **Controlled-$U^{2^0} = U^1 = S$ on qubit 0:**
           - Kicks back phase $e^{2\pi i (0.25) \cdot 1} = e^{i\pi/2} = i$.
        4. **Controlled-$U^{2^1} = U^2 = S^2 = Z$ on qubit 1:**
           - Kicks back phase $e^{2\pi i (0.25) \cdot 2} = e^{i\pi} = -1$.
        5. **State before IQFT:**
           $$\frac{1}{2} (|0\rangle - |1\rangle) \otimes (|0\rangle + i|1\rangle) |1\rangle$$
        6. **After Inverse QFT:**
           The state collapses strictly into $|01\rangle |1\rangle$!
        7. **Measurement:**
           Measured bitstring = `01` $\implies x = 1$.
           $$\tilde{\theta} = \frac{1}{2^2} = \frac{1}{4} = 0.25 \quad (\text{Error } = 0)$$
        """
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="qpe-concept-box">
            <b>Worked Example 2: Non-Dyadic Phase θ = 1/3 with t = 3 Counting Qubits</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write(
        r"""
        Let $\theta = 1/3 \approx 0.333333$.
        With $t=3$ counting qubits, $2^3 \cdot \theta = 8 \cdot (1/3) = 8/3 \approx 2.6667$.
        Notice that $2.6667$ is not an integer! It lies between:
        - $m = 2$ (`010`), corresponding to estimated phase $2/8 = 0.2500$.
        - $m = 3$ (`011`), corresponding to estimated phase $3/8 = 0.3750$.

        Using Nielsen & Chuang Eq. (5.26):
        $$P(m=3) = \frac{1}{64} \frac{\sin^2(\pi(8/3 - 3))}{\sin^2(\pi(1/3 - 3/8))} = \frac{1}{64} \frac{\sin^2(-\pi/3)}{\sin^2(-\pi/24)} \approx 0.688 \quad (68.8\%)$$
        $$P(m=2) = \frac{1}{64} \frac{\sin^2(\pi(8/3 - 2))}{\sin^2(\pi(1/3 - 2/8))} = \frac{1}{64} \frac{\sin^2(2\pi/3)}{\sin^2(\pi/12)} \approx 0.198 \quad (19.8\%)$$
        The remaining $\approx 11.4\%$ is spread over the other 6 states.
        The algorithm selects $|011\rangle$ with the highest probability, yielding $\tilde{\theta} = 0.3750$, with absolute error $|1/3 - 0.3750| = 0.0417 \leq \frac{1}{8} = 0.1250$.
        """
    )

with tab4:
    st.markdown("### Practical Applications of QPE in Modern Quantum Computing")

    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        st.markdown(
            """
            <div class="qpe-metric-card" style="text-align: left; height: 100%;">
                <div style="font-weight: 700; color: #38BDF8; font-size: 1.1rem; margin-bottom: 8px;">🔐 Shor's Algorithm</div>
                <p style="font-size: 0.9rem; color: #94A3B8;">
                    Shor's polynomial-time integer factorization algorithm reduces factoring $N = p \cdot q$ 
                    to order-finding of the modular multiplication operator $U_a |y\rangle = |a y \pmod N\rangle$.
                    QPE estimates the phase $s/r$, revealing the hidden period $r$ via continued fraction expansion.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_a2:
        st.markdown(
            """
            <div class="qpe-metric-card" style="text-align: left; height: 100%;">
                <div style="font-weight: 700; color: #34D399; font-size: 1.1rem; margin-bottom: 8px;">🧪 Quantum Chemistry</div>
                <p style="font-size: 0.9rem; color: #94A3B8;">
                    Computing the ground state and excited energy levels of molecular Hamiltonians $H$.
                    By simulating the time evolution operator $U = e^{-iHt}$, QPE directly yields the energy eigenvalue 
                    $E_0 = -\frac{2\pi \theta}{t}$ with chemical accuracy for drug discovery and battery materials.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_a3:
        st.markdown(
            """
            <div class="qpe-metric-card" style="text-align: left; height: 100%;">
                <div style="font-weight: 700; color: #FBBF24; font-size: 1.1rem; margin-bottom: 8px;">📈 HHL Linear Systems</div>
                <p style="font-size: 0.9rem; color: #94A3B8;">
                    The Harrow-Hassidim-Lloyd (HHL) algorithm solves $A \vec{x} = \vec{b}$ with an exponential speedup 
                    $O(\log(N) s^2 \kappa^2 / \epsilon)$. It decomposes vector $|b\rangle$ into the eigenbasis of $A$ 
                    using QPE, inverts the eigenvalues via controlled rotations, and uncomputes QPE.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
