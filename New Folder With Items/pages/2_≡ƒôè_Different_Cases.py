"""
Page 2: Different Experimental Cases Investigation
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
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qpe.analysis import PREDEFINED_CASES, compare_cases
from qpe.simulator import run_qpe_simulation
from qpe.ui_helper import apply_custom_css

st.set_page_config(page_title="Different Cases | M.Tech CSE", page_icon="📊", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="qpe-hero">
        <h1>📊 Different Experimental Cases Benchmark</h1>
        <p>Comparative study of exact dyadic phases vs. non-dyadic continuous phases to evaluate quantum state leakage and estimation fidelity.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Benchmark Settings")

num_qubits = st.sidebar.slider("Counting Qubits (t)", min_value=2, max_value=6, value=4)
shots = st.sidebar.select_slider("Shots per Experiment", options=[512, 1024, 2048, 4096], value=2048)

st.sidebar.markdown("---")
include_custom = st.sidebar.checkbox("Include Custom Phase", value=True)
custom_val = 0.15
if include_custom:
    custom_raw = st.sidebar.text_input("Custom Phase θ (e.g. 0.15, 5/12, 1/7):", value="0.15")
    try:
        if "/" in custom_raw:
            p = custom_raw.split("/")
            custom_val = float(p[0]) / float(p[1])
        else:
            custom_val = float(custom_raw)
        custom_val = custom_val % 1.0
    except Exception:
        custom_val = 0.15

if st.sidebar.button("🔄 Re-run All Cases", type="primary", use_container_width=True):
    st.session_state.pop("cases_df", None)

# Run benchmark
with st.spinner("Executing QPE across all target cases..."):
    df_cases = compare_cases(
        num_counting_qubits=num_qubits,
        shots=shots,
        custom_theta=custom_val if include_custom else None
    )

st.markdown("### 📋 Multi-Case Comparative Summary Table")
st.dataframe(df_cases, use_container_width=True)

# CSV Export
csv_data = df_cases.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Comparative Benchmark (CSV)",
    data=csv_data,
    file_name=f"qpe_different_cases_t{num_qubits}.csv",
    mime="text/csv"
)

st.markdown("---")

# Visual Multi-Plot of Distributions
st.markdown("### 📈 Measurement Probability Distributions Side-by-Side")

cases_to_plot = list(PREDEFINED_CASES)
if include_custom:
    cases_to_plot.append({
        "name": f"Custom θ = {custom_val:.4f}",
        "theta": custom_val,
        "category": "Custom",
    })

# Render 2-column comparative layout
col_left, col_right = st.columns(2)

for i, case in enumerate(cases_to_plot):
    target_col = col_left if (i % 2 == 0) else col_right
    theta = case["theta"]
    res = run_qpe_simulation(theta=theta, num_counting_qubits=num_qubits, shots=shots)

    states = sorted(res.all_states, key=lambda s: s.decimal_int)
    bitstrings = [s.binary_str for s in states]
    probs = [s.probability for s in states]
    colors = ["#10B981" if b == res.most_probable_bitstring else "#6366F1" for b in bitstrings]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bitstrings,
        y=probs,
        marker=dict(color=colors),
        name=case["name"]
    ))

    badge = "Exact Dyadic (100% Peak)" if res.is_exact_phase else "Approximate (Leakage Spread)"
    fig.update_layout(
        title=f"<b>{case['name']}</b> ({badge}) | Peak: |{res.most_probable_bitstring}⟩ = {res.estimated_phase:.4f}",
        xaxis_title="Basis State |m⟩",
        yaxis_title="Probability",
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=40, b=30),
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
    )

    with target_col:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Deep Theory: Exact vs Approximate
st.markdown("### 🎓 Academic Deep-Dive: Exactly Representable vs. Approximately Representable Phases")

col_th1, col_th2 = st.columns(2)

with col_th1:
    st.markdown(
        """
        <div class="qpe-concept-box">
            <b>1. Exactly Representable (Dyadic) Phases:</b><br>
            A phase $\\theta$ is exactly representable with $t$ counting qubits if and only if it is a <b>dyadic rational</b>:
            $$\\theta = \\frac{m}{2^t}, \\quad m \\in \\{0, 1, \\dots, 2^t - 1\\}$$
        </div>
        
        - **Examples:** $\\theta = 1/2$ (requires $t \\geq 1$), $\\theta = 1/4$ ($t \\geq 2$), $\\theta = 1/8$ ($t \\geq 3$), $\\theta = 3/8$ ($t \\geq 3$).
        - **Quantum Interference:** The Fourier phase accumulated across all $2^t$ terms undergoes <i>perfect constructive interference</i> on state $|m\\rangle$ and <i>perfect destructive interference</i> on all other $2^t - 1$ orthogonal states.
        - **Outcome:** The success probability is **exactly 1.0 (100%)** in the ideal simulator, with zero distribution entropy ($H = 0$).
        """,
        unsafe_allow_html=True
    )

with col_th2:
    st.markdown(
        """
        <div class="qpe-concept-box">
            <b>2. Approximately Representable (Non-Dyadic) Phases:</b><br>
            When $\\theta$ is not a dyadic fraction (e.g. $\\theta = 1/3 = 0.010101..._2$ or $\\theta = 1/5 = 0.00110011..._2$), $2^t \\theta$ is <i>never an exact integer</i>.
        </div>
        
        - **Spectral Leakage:** Because the true phase lies between two grid points $m/2^t$ and $(m+1)/2^t$, destructive interference is incomplete.
        - **Analytical Distribution:** The measurement probabilities follow Nielsen & Chuang Eq. (5.26):
          $$P(m) = \\frac{1}{2^{2t}} \\frac{\\sin^2(\\pi(2^t \\theta - m))}{\\sin^2(\\pi(\\theta - m / 2^t))}$$
        - **Outcome:** Probability peaks at the two closest integers to $2^t \\theta$, with neighboring states receiving nonzero probability. Success probability of the rounded peak is typically $\\approx 68\\% - 81\\%$.
        """,
        unsafe_allow_html=True
    )
