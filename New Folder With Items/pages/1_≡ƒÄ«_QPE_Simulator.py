"""
Page 1: Interactive Quantum Phase Estimation Simulator
M.Tech CSE Academic Project
"""

import matplotlib
matplotlib.use("Agg")
import streamlit as st
import pandas as pd
import numpy as np

from qpe.circuit import build_qpe_circuit, get_circuit_metadata
from qpe.simulator import run_qpe_simulation, decimal_to_binary_fraction
from qpe.noise import create_depolarizing_noise_model, NOISE_PRESETS
from qpe.ui_helper import (
    apply_custom_css,
    render_circuit_diagram,
    plot_counts_histogram,
    record_experiment_to_history,
    render_metric_cards_row,
    get_history_dataframe
)

st.set_page_config(page_title="QPE Simulator | M.Tech CSE", page_icon="🎮", layout="wide")
apply_custom_css()

st.markdown(
    """
    <div class="qpe-hero">
        <h1>🎮 Interactive Quantum Phase Estimation Simulator</h1>
        <p>Configure arbitrary phase parameters, synthesize the underlying quantum circuit, and observe quantum measurement collapsing.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Configuration
st.sidebar.header("⚙️ Experiment Configuration")

# Quick Presets
st.sidebar.markdown("**Quick Phase Presets:**")
cols_preset = st.sidebar.columns(3)
if cols_preset[0].button("θ = 1/2"):
    st.session_state["phase_input"] = 0.5
if cols_preset[1].button("θ = 1/4"):
    st.session_state["phase_input"] = 0.25
if cols_preset[2].button("θ = 1/8"):
    st.session_state["phase_input"] = 0.125

cols_preset2 = st.sidebar.columns(3)
if cols_preset2[0].button("θ = 3/8"):
    st.session_state["phase_input"] = 0.375
if cols_preset2[1].button("θ = 1/3"):
    st.session_state["phase_input"] = round(1.0 / 3.0, 5)
if cols_preset2[2].button("θ = 1/5"):
    st.session_state["phase_input"] = 0.2

default_theta = st.session_state.get("phase_input", 0.25)

phase_mode = st.sidebar.radio("Phase Input Method", ["Slider", "Direct Decimal / Custom Fraction"], horizontal=True)

if phase_mode == "Slider":
    theta = st.sidebar.slider(
        "Target Phase θ ∈ [0, 1)",
        min_value=0.0,
        max_value=0.9999,
        value=float(default_theta),
        step=0.0125,
        format="%.4f"
    )
else:
    theta_raw = st.sidebar.text_input("Enter Phase θ (e.g., 0.25, 1/3, 3/8, 0.125):", value=str(default_theta))
    try:
        if "/" in theta_raw:
            parts = theta_raw.split("/")
            theta = float(parts[0]) / float(parts[1])
        else:
            theta = float(theta_raw)
        if not (0.0 <= theta < 1.0):
            st.sidebar.warning("Phase should be in [0, 1). Taking modulo 1.0.")
            theta = theta % 1.0
    except Exception:
        st.sidebar.error("Invalid number format. Defaulting to 0.25.")
        theta = 0.25

num_qubits = st.sidebar.slider(
    "Counting Qubits (Precision t)",
    min_value=2,
    max_value=8,
    value=3,
    help="Determines the number of bits in binary phase estimation and total basis states (2^t)."
)

sim_mode = st.sidebar.selectbox("Simulation Mode", ["Ideal (Statevector/Shot Sim)", "Noisy (NISQ Depolarizing)"])

noise_model = None
if sim_mode == "Noisy (NISQ Depolarizing)":
    noise_preset = st.sidebar.selectbox("Noise Preset", list(NOISE_PRESETS.keys()))
    preset_vals = NOISE_PRESETS[noise_preset]
    p_1q = st.sidebar.slider("1-Qubit Error Rate", 0.0, 0.05, preset_vals["p_1q"], step=0.001, format="%.3f")
    p_2q = st.sidebar.slider("2-Qubit Error Rate", 0.0, 0.10, preset_vals["p_2q"], step=0.005, format="%.3f")
    p_ro = st.sidebar.slider("Readout Error Rate", 0.0, 0.10, preset_vals["p_readout"], step=0.005, format="%.3f")
    noise_model = create_depolarizing_noise_model(p_1q, p_2q, p_ro)

shots = st.sidebar.select_slider(
    "Number of Shots",
    options=[256, 512, 1024, 2048, 4096, 8192],
    value=2048,
    help="Number of circuit executions for measurement sampling."
)

run_button = st.sidebar.button("🚀 Run QPE Simulation", type="primary", use_container_width=True)

# Main Execution Body
if run_button or "current_result" not in st.session_state:
    with st.spinner(f"Running Quantum Phase Estimation for θ = {theta:.5f} on {num_qubits} qubits ({shots} shots)..."):
        result = run_qpe_simulation(
            theta=theta,
            num_counting_qubits=num_qubits,
            shots=shots,
            noise_model=noise_model
        )
        st.session_state["current_result"] = result
        record_experiment_to_history(result, label=f"θ={theta:.4f}, t={num_qubits}, {sim_mode}")

result = st.session_state["current_result"]

# Status Badge Banner
col_b1, col_b2, col_b3 = st.columns([2, 2, 2])
with col_b1:
    if result.is_exact_phase:
        st.markdown('<span class="qpe-badge-exact">✓ Exact Dyadic Phase (2^t · θ is integer)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="qpe-badge-approx">~ Approximate Phase (Spectral Broadening)</span>', unsafe_allow_html=True)
with col_b2:
    if result.simulation_mode == "Ideal":
        st.markdown('<span class="qpe-badge-exact">Ideal Unitary Simulation</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="qpe-badge-noisy">⚠ Noisy NISQ Simulation Active</span>', unsafe_allow_html=True)
with col_b3:
    st.markdown(f"**Binary Fraction:** `{decimal_to_binary_fraction(result.actual_phase, num_qubits)}`")

st.markdown("<br>", unsafe_allow_html=True)

# 4 Key Metric Cards
render_metric_cards_row(result)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Organized Analysis
tab_hist, tab_circuit, tab_table, tab_history = st.tabs([
    "📊 Measurement Histogram",
    "⚡ Quantum Circuit",
    "📋 Measurement Data Table",
    "📜 Session History"
])

with tab_hist:
    fig_hist = plot_counts_histogram(
        result,
        show_theoretical=(result.simulation_mode == "Ideal"),
        title=f"Measurement Probability Distribution (θ = {result.actual_phase:.4f}, t = {num_qubits})"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        f"""
        **Mathematical Interpretation:**
        - **Most Probable Measured State:** `|{result.most_probable_bitstring}⟩` (Decimal $x = {int(result.most_probable_bitstring, 2)}$)
        - **Derived Phase Formula:** $\\tilde{{\\theta}} = \\frac{{x}}{{2^t}} = \\frac{{{int(result.most_probable_bitstring, 2)}}}{{{2**num_qubits}}} = {result.estimated_phase:.6f}$
        - **Empirical Measurement Probability:** {result.success_probability * 100:.2f}%
        - **Maximum Error Bound:** $|\\theta - \\tilde{{\\theta}}| \\leq \\frac{{1}}{{2^{{{num_qubits}}}}} = {1.0 / (2**num_qubits):.6f}$
        """
    )

with tab_circuit:
    st.markdown("### Quantum Phase Estimation Circuit Architecture")
    st.markdown(
        """
        - **Target Qubit (bottom):** Prepared in eigenstate $|1\\rangle$ using Pauli-$X$ gate.
        - **Counting Qubits (top):** Initialized in equal superposition using Hadamard ($H$) gates.
        - **Phase Kickback:** Controlled phase rotations $CP(2^j \\cdot 2\\pi\\theta)$.
        - **Inverse QFT ($QFT^\\dagger$):** Unrolls phase kickbacks into binary readout bits.
        """
    )
    render_circuit_diagram(result.circuit)

with tab_table:
    st.markdown("### Measured Basis States Breakdown")
    table_data = []
    for s in result.all_states:
        table_data.append({
            "Bitstring |b⟩": f"|{s.binary_str}⟩",
            "Decimal (x)": s.decimal_int,
            "Shots": s.shots,
            "Probability": f"{s.probability:.4f}",
            "Estimated Phase": f"{s.estimated_phase:.5f}",
            "Absolute Error": f"{s.absolute_error:.6f}"
        })
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True)

    # Download CSV
    csv_bytes = df_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Measurement Data (CSV)",
        data=csv_bytes,
        file_name=f"qpe_measurement_theta_{result.actual_phase:.4f}_t{num_qubits}.csv",
        mime="text/csv"
    )

with tab_history:
    st.markdown("### Current Session Experiment History")
    df_hist = get_history_dataframe()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
        csv_hist = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Session History (CSV)",
            data=csv_hist,
            file_name="qpe_session_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No experiment runs recorded in this session yet.")

    if st.button("🔄 Clear Session History"):
        st.session_state.experiment_history = []
        st.rerun()
