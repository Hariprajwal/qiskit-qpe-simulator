"""
Page 4: Ideal vs. Noisy Simulation Analysis
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

from qpe.analysis import run_noise_comparison
from qpe.noise import create_depolarizing_noise_model, NOISE_PRESETS
from qpe.ui_helper import apply_custom_css

st.set_page_config(page_title="Noise Analysis | M.Tech CSE", page_icon="🔬", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="qpe-hero">
        <h1>🔬 Ideal vs. Noisy Quantum Simulation Analysis</h1>
        <p>Evaluate the impact of physical hardware noise (depolarizing channels, gate infidelities, and readout errors) on phase estimation accuracy.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Simulation Settings")

phase_sel = st.sidebar.selectbox("Select Phase θ", ["0.25 (1/4 - Dyadic)", "0.50 (1/2 - Dyadic)", "0.125 (1/8 - Dyadic)", "0.3333 (1/3 - Non-dyadic)", "0.2000 (1/5 - Non-dyadic)"])
if "0.25" in phase_sel:
    theta = 0.25
elif "0.50" in phase_sel:
    theta = 0.5
elif "0.125" in phase_sel:
    theta = 0.125
elif "0.3333" in phase_sel:
    theta = 1.0 / 3.0
else:
    theta = 0.2

num_qubits = st.sidebar.slider("Counting Qubits (t)", 2, 5, 3)
shots = st.sidebar.select_slider("Shots", [512, 1024, 2048, 4096], value=2048)

st.sidebar.markdown("---")
st.sidebar.subheader("Noise Parameters")
noise_preset = st.sidebar.selectbox("Preset", list(NOISE_PRESETS.keys()), index=1)
preset_cfg = NOISE_PRESETS[noise_preset]

p_1q = st.sidebar.slider("1-Qubit Gate Error (p_1q)", 0.0, 0.05, preset_cfg["p_1q"], step=0.002, format="%.3f")
p_2q = st.sidebar.slider("2-Qubit Gate Error (p_2q)", 0.0, 0.10, preset_cfg["p_2q"], step=0.005, format="%.3f")
p_ro = st.sidebar.slider("Readout Error (p_ro)", 0.0, 0.10, preset_cfg["p_readout"], step=0.005, format="%.3f")

noise_model = create_depolarizing_noise_model(p_1q, p_2q, p_ro)

# Run comparative benchmark
with st.spinner("Executing parallel Ideal and Noisy quantum simulations..."):
    comp = run_noise_comparison(
        theta=theta,
        num_counting_qubits=num_qubits,
        shots=shots,
        noise_model=noise_model
    )

ideal_res = comp["ideal_result"]
noisy_res = comp["noisy_result"]
df_comp = comp["comparison_table"]

# Metric Cards Row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(
        f"""
        <div class="qpe-metric-card">
            <div class="qpe-metric-label">Ideal Peak Prob</div>
            <div class="qpe-metric-val" style="color: #10B981;">{ideal_res.success_probability * 100:.1f}%</div>
            <div class="qpe-metric-sub">State |{ideal_res.most_probable_bitstring}⟩</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_m2:
    st.markdown(
        f"""
        <div class="qpe-metric-card">
            <div class="qpe-metric-label">Noisy Peak Prob</div>
            <div class="qpe-metric-val" style="color: #F87171;">{noisy_res.success_probability * 100:.1f}%</div>
            <div class="qpe-metric-sub">State |{noisy_res.most_probable_bitstring}⟩</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_m3:
    drop = (ideal_res.success_probability - noisy_res.success_probability) * 100.0
    st.markdown(
        f"""
        <div class="qpe-metric-card">
            <div class="qpe-metric-label">Fidelity Drop</div>
            <div class="qpe-metric-val" style="color: #F59E0B;">-{drop:.1f}%</div>
            <div class="qpe-metric-sub">Hardware Attenuation</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_m4:
    st.markdown(
        f"""
        <div class="qpe-metric-card">
            <div class="qpe-metric-label">Noisy Estimated θ</div>
            <div class="qpe-metric-val">{noisy_res.estimated_phase:.4f}</div>
            <div class="qpe-metric-sub">Actual: {theta:.4f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Comparative Charts
col_ch1, col_ch2 = st.columns(2)

# Gather all states across both
all_keys = sorted(list(set(list(ideal_res.raw_counts.keys()) + list(noisy_res.raw_counts.keys()))))
ideal_probs = [ideal_res.probabilities.get(k, 0.0) for k in all_keys]
noisy_probs = [noisy_res.probabilities.get(k, 0.0) for k in all_keys]

with col_ch1:
    st.markdown("#### Side-by-Side Distribution Comparison")
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=all_keys,
        y=ideal_probs,
        name="Ideal Simulator",
        marker=dict(color="#10B981")
    ))
    fig_comp.add_trace(go.Bar(
        x=all_keys,
        y=noisy_probs,
        name="Noisy Simulator",
        marker=dict(color="#F43F5E")
    ))
    fig_comp.update_layout(
        template="plotly_dark",
        barmode="group",
        xaxis_title="Basis State |b⟩",
        yaxis_title="Probability",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

with col_ch2:
    st.markdown("#### Detailed Benchmark Comparison Table")
    st.dataframe(df_comp, use_container_width=True)
    
    csv_bytes = df_comp.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Ideal vs. Noisy Comparison (CSV)",
        data=csv_bytes,
        file_name=f"qpe_noise_benchmark_theta_{theta:.4f}_t{num_qubits}.csv",
        mime="text/csv"
    )

st.markdown("---")

# Academic Noise Discussion
st.markdown("### 🎓 Physical Interpretation of Noise Channels in QPE")

st.markdown(
    """
    <div class="qpe-concept-box">
        <b>Why Quantum Phase Estimation is Highly Sensitive to Hardware Noise:</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    1. **Exponential Depth of Controlled-$U$ Operations:**
       In QPE, counting qubit $j$ applies $U^{2^j}$. For $t$ qubits, the circuit requires $2^0 + 2^1 + \\dots + 2^{t-1} = 2^t - 1$ total unitary operations.
       As precision $t$ increases, circuit depth scales exponentially, compounding gate infidelity and decoherence.
    
    2. **Depolarizing Noise & State Mixing:**
       A depolarizing channel transforms a pure density operator $\\rho = |\\psi\\rangle\\langle\\psi|$ into a mixed state:
       $$\\mathcal{E}(\\rho) = (1 - p)\\rho + \\frac{p}{2} I$$
       This causes the sharp interference peaks to flatten and disperse uniform probability across all $2^t$ orthogonal states.
       This is quantitatively measured by the increase in **Shannon Entropy** ($H_{\\text{noisy}} > H_{\\text{ideal}}$).

    3. **Readout / Measurement Bit-Flips:**
       Even if the quantum state right before measurement is perfectly $|m\\rangle$, physical measurement resonators have a nonzero probability 
       $P(0|1)$ and $P(1|0)$ of misclassifying the superconducting state. For $t$ measured qubits, the probability of measuring all bits correctly 
       without error scales as $(1 - p_{\\text{ro}})^t$.

    4. **Quantum Error Mitigation (QEM):**
       In current NISQ computing, techniques such as Zero-Noise Extrapolation (ZNE), Readout Error Mitigation (M3/TREX), and dynamical decoupling 
       are essential for recovering clean phase peaks on real QPUs.
    """
)
