"""
Page 3: Precision Scaling Analysis
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
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qpe.analysis import analyze_precision_scaling
from qpe.ui_helper import apply_custom_css

st.set_page_config(page_title="Precision Analysis | M.Tech CSE", page_icon="📈", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="qpe-hero">
        <h1>📈 Precision & Error Scaling Analysis</h1>
        <p>Investigate how the number of counting qubits (t = 2 to 8) exponentially contracts estimation error bounds and governs phase fidelity.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Scaling Configuration")

theta_choice = st.sidebar.selectbox(
    "Select Target Phase θ",
    ["1/3 (≈ 0.333333, Non-dyadic)", "1/5 (0.200000, Non-dyadic)", "1/8 (0.125000, Dyadic)", "3/8 (0.375000, Dyadic)", "Custom"]
)

if "1/3" in theta_choice:
    target_theta = 1.0 / 3.0
elif "1/5" in theta_choice:
    target_theta = 0.2
elif "1/8" in theta_choice:
    target_theta = 0.125
elif "3/8" in theta_choice:
    target_theta = 0.375
else:
    target_theta = st.sidebar.number_input("Custom Phase θ:", min_value=0.001, max_value=0.999, value=0.2857, step=0.01)

min_q = st.sidebar.slider("Minimum Qubits", 2, 4, 2)
max_q = st.sidebar.slider("Maximum Qubits", 5, 8, 7)
shots = st.sidebar.select_slider("Shots per Trial", [512, 1024, 2048, 4096], value=2048)

with st.spinner("Simulating QPE across precision spectrum..."):
    df_scaling = analyze_precision_scaling(
        theta=target_theta,
        min_qubits=min_q,
        max_qubits=max_q,
        shots=shots
    )

st.markdown("### 📊 Precision Scaling Data Table")
st.dataframe(df_scaling, width="stretch")

csv_scaling = df_scaling.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Precision Scaling Data (CSV)",
    data=csv_scaling,
    file_name=f"qpe_precision_scaling_theta_{target_theta:.4f}.csv",
    mime="text/csv"
)

st.markdown("---")

# Visual Graphs
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### 1. Estimation Error vs. Counting Qubits")
    fig_err = go.Figure()

    # Empirical absolute error
    fig_err.add_trace(go.Scatter(
        x=df_scaling["Counting Qubits (t)"],
        y=df_scaling["Absolute Error"],
        mode="lines+markers",
        name="Empirical Absolute Error |θ - θ̃|",
        line=dict(color="#38BDF8", width=3),
        marker=dict(size=10, symbol="circle")
    ))

    # Theoretical upper bound 1 / 2^t
    fig_err.add_trace(go.Scatter(
        x=df_scaling["Counting Qubits (t)"],
        y=df_scaling["Theoretical Error Bound (1/2^t)"],
        mode="lines+markers",
        name="Theoretical Bound (1/2^t)",
        line=dict(color="#F43F5E", width=2, dash="dash"),
        marker=dict(size=8, symbol="diamond")
    ))

    fig_err.update_layout(
        template="plotly_dark",
        xaxis_title="Counting Qubits (t)",
        yaxis_title="Error (Decimal)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_err, use_container_width=True)

with col_g2:
    st.markdown("#### 2. Success Probability vs. Counting Qubits")
    fig_prob = go.Figure()

    fig_prob.add_trace(go.Bar(
        x=df_scaling["Counting Qubits (t)"],
        y=df_scaling["Success Probability (%)"],
        name="Peak State Probability (%)",
        marker=dict(
            color=df_scaling["Success Probability (%)"],
            colorscale="Viridis",
            showscale=True
        ),
        text=[f"{p:.1f}%" for p in df_scaling["Success Probability (%)"]],
        textposition="auto"
    ))

    fig_prob.update_layout(
        template="plotly_dark",
        xaxis_title="Counting Qubits (t)",
        yaxis_title="Success Probability (%)",
        yaxis=dict(range=[0, 105]),
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)"
    )
    st.plotly_chart(fig_prob, use_container_width=True)

st.markdown("---")

# Probabilistic Fluctuation Explanation
st.markdown("### 🎲 Understanding Probabilistic Fluctuations in Quantum Phase Estimation")

st.markdown(
    """
    <div class="qpe-concept-box">
        <b>Why Does Empirical Error Sometimes Fluctuate?</b><br>
        In classical numerical methods (like Euler's or Simpson's rule), increasing grid resolution $N$ strictly decreases error monotonically.
        In <b>Quantum Phase Estimation</b>, students often notice that adding a qubit may occasionally produce a minor fluctuation in absolute error or peak probability.
        Here is why:
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    1. **Rounding to the Nearest Grid Point:**
       For $t$ counting qubits, the algorithm discretizes the continuous interval $[0, 1)$ into $2^t$ discrete points:
       $$x_k = \\frac{k}{2^t}, \\quad k \\in \\{0, 1, \\dots, 2^t - 1\\}$$
       The distance from $\\theta$ to the nearest integer grid point $\\delta_t = |\\theta - \\frac{\\text{round}(2^t \\theta)}{2^t}|$ 
       is strictly bounded by $\\frac{1}{2^{t+1}}$, but for specific values of $t$, the phase $\\theta$ might happen to land *almost directly on* a grid point for $t=3$ 
       (e.g., $1/3 \\approx 0.3333$, $3/8 = 0.375$, error $= 0.0416$) while at $t=4$ ($5/16 = 0.3125$, error $= 0.0208$).
    
    2. **Shot Noise (Poisson Measurement Variance):**
       Quantum computers measure samples (shots). For $S$ shots, the empirical frequency has a statistical variance of $\\sigma \\approx \\sqrt{\\frac{p(1-p)}{S}}$.
       With non-dyadic phases where two peaks have close probabilities (such as $1/3$ where $|011\\rangle$ gets $\\approx 68\\%$ and $|010\\rangle$ gets $\\approx 20\\%$),
       finite shot counts introduce statistical sampling noise.

    3. **Guaranteed Mathematical Upper Bound:**
       Regardless of minor fluctuations, the absolute error is **mathematically guaranteed** to obey:
       $$|\\theta - \\tilde{\\theta}| \\leq \\frac{1}{2^t}$$
       And by using $t = n + \\lceil \\log_2(2 + \\frac{1}{2\\epsilon}) \\rceil$ counting qubits, QPE achieves an approximation accurate to $n$ bits with success probability at least $1 - \\epsilon$!
    """
)
