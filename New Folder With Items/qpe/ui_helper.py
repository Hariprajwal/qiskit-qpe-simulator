"""
UI and Visualization Helpers for the Streamlit Dashboard.

Provides:
- Custom responsive CSS styling (academic theme, glassmorphism cards, badges)
- Circuit rendering (Matplotlib circuit diagram and ASCII fallback)
- Interactive Plotly distribution plots with theoretical overlay
- CSV export generator
- Session history tracking
"""

from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")  # Enforce headless Agg backend to prevent macOS Cocoa GUI thread crash (SIGSEGV)
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional

from qiskit import QuantumCircuit
from qpe.simulator import QPEResult
from qpe.analysis import calculate_theoretical_probability


def apply_custom_css():
    """Injects custom CSS for modern, premium academic aesthetics."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Hero Banner */
        .qpe-hero {
            background: linear-gradient(135deg, rgba(24, 28, 47, 0.9) 0%, rgba(37, 43, 72, 0.85) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(8px);
        }

        .qpe-hero h1 {
            color: #F8FAFC;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .qpe-hero p {
            color: #94A3B8;
            font-size: 1.05rem;
            margin: 0;
            line-height: 1.5;
        }

        /* Stat/Metric Card */
        .qpe-metric-card {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            text-align: center;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .qpe-metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.4);
        }

        .qpe-metric-label {
            color: #94A3B8;
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }

        .qpe-metric-val {
            color: #38BDF8;
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }

        .qpe-metric-sub {
            color: #64748B;
            font-size: 0.8rem;
            margin-top: 4px;
        }

        /* Badge styles */
        .qpe-badge-exact {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 9999px;
            padding: 2px 10px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .qpe-badge-approx {
            background-color: rgba(245, 158, 11, 0.2);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 9999px;
            padding: 2px 10px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .qpe-badge-noisy {
            background-color: rgba(239, 68, 68, 0.2);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 9999px;
            padding: 2px 10px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Concept Card */
        .qpe-concept-box {
            background: rgba(15, 23, 42, 0.5);
            border-left: 4px solid #6366F1;
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_circuit_diagram(qc: QuantumCircuit, title: str = "Quantum Phase Estimation Circuit"):
    """
    Renders the Qiskit QuantumCircuit using Matplotlib, with an expandable ASCII fallback.
    """
    try:
        # Use Matplotlib drawer
        fig = qc.draw(output="mpl", style="iqp", scale=0.9, fold=-1)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        plt.close("all")
    except Exception as e:
        st.warning(f"Graphical circuit rendering notice: {e}. Displaying ASCII representation.")
        st.text(qc.draw(output="text"))

    with st.expander("📄 View Circuit ASCII Diagram & QASM / Details"):
        st.text(qc.draw(output="text"))
        st.markdown(f"**Circuit Depth:** {qc.depth()} | **Total Qubits:** {qc.num_qubits} | **Classical Bits:** {qc.num_clbits}")


def plot_counts_histogram(
    result: QPEResult,
    show_theoretical: bool = True,
    title: Optional[str] = None
) -> go.Figure:
    """
    Generates an interactive Plotly bar chart of the measurement distribution,
    optionally comparing empirical counts with theoretical Nielsen & Chuang probabilities.
    """
    states = sorted(result.all_states, key=lambda s: s.decimal_int)
    
    bitstrings = [s.binary_str for s in states]
    decimals = [s.decimal_int for s in states]
    empirical_probs = [s.probability for s in states]
    shots_counts = [s.shots for s in states]
    estimated_phases = [s.estimated_phase for s in states]

    # Calculate theoretical probabilities
    theoretical_probs = [
        calculate_theoretical_probability(result.actual_phase, result.num_counting_qubits, d)
        for d in decimals
    ]

    fig = go.Figure()

    # Empirical measurement bar chart
    colors = [
        "#10B981" if b == result.most_probable_bitstring else "#6366F1"
        for b in bitstrings
    ]

    fig.add_trace(go.Bar(
        x=bitstrings,
        y=empirical_probs,
        name=f"Empirical ({result.simulation_mode})",
        marker=dict(color=colors, line=dict(color="#312E81", width=1.5)),
        customdata=list(zip(shots_counts, estimated_phases)),
        hovertemplate="<b>State |%{x}⟩</b><br>" +
                      "Phase Estimate: %{customdata[1]:.4f}<br>" +
                      "Measured Shots: %{customdata[0]}<br>" +
                      "Empirical Probability: %{y:.4f}<extra></extra>"
    ))

    if show_theoretical and result.simulation_mode == "Ideal":
        fig.add_trace(go.Scatter(
            x=bitstrings,
            y=theoretical_probs,
            mode="lines+markers",
            name="Theoretical P(m)",
            line=dict(color="#F59E0B", width=2, dash="dash"),
            marker=dict(size=8, color="#FBBF24"),
            hovertemplate="Theoretical P(|%{x}⟩): %{y:.4f}<extra></extra>"
        ))

    default_title = (
        f"Measurement Probability Distribution (θ = {result.actual_phase:.4f}, "
        f"t = {result.num_counting_qubits} qubits, {result.total_shots} shots)"
    )

    fig.update_layout(
        title=title or default_title,
        xaxis_title="Counting Register State |m⟩ (Binary Bitstring)",
        yaxis_title="Probability P(m)",
        template="plotly_dark",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        margin=dict(l=40, r=40, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif")
    )

    return fig


def initialize_session_history():
    """Initializes experiment history in Streamlit session state."""
    if "experiment_history" not in st.session_state:
        st.session_state.experiment_history = []


def record_experiment_to_history(result: QPEResult, label: str = ""):
    """Adds a simulation result to the current session history."""
    initialize_session_history()
    st.session_state.experiment_history.append({
        "Label": label or f"Run #{len(st.session_state.experiment_history) + 1}",
        "Actual θ": round(result.actual_phase, 5),
        "Estimated θ": round(result.estimated_phase, 5),
        "Measured State": result.most_probable_bitstring,
        "Qubits (t)": result.num_counting_qubits,
        "Shots": result.total_shots,
        "Mode": result.simulation_mode,
        "Absolute Error": round(result.absolute_error, 6),
        "Success Prob": f"{result.success_probability * 100:.2f}%",
        "Exact Dyadic": "Yes" if result.is_exact_phase else "No",
    })


def get_history_dataframe() -> pd.DataFrame:
    """Returns the experiment history as a Pandas DataFrame."""
    initialize_session_history()
    return pd.DataFrame(st.session_state.experiment_history)


def render_metric_cards_row(result: QPEResult):
    """Renders a balanced row of 4 visual metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="qpe-metric-card">
                <div class="qpe-metric-label">Actual Phase θ</div>
                <div class="qpe-metric-val">{result.actual_phase:.5f}</div>
                <div class="qpe-metric-sub">Input Target</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="qpe-metric-card">
                <div class="qpe-metric-label">Estimated Phase θ̃</div>
                <div class="qpe-metric-val">{result.estimated_phase:.5f}</div>
                <div class="qpe-metric-sub">State |{result.most_probable_bitstring}⟩</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        color = "#10B981" if result.absolute_error == 0 else ("#38BDF8" if result.absolute_error < 0.05 else "#F59E0B")
        st.markdown(
            f"""
            <div class="qpe-metric-card">
                <div class="qpe-metric-label">Absolute Error |θ - θ̃|</div>
                <div class="qpe-metric-val" style="color: {color};">{result.absolute_error:.6f}</div>
                <div class="qpe-metric-sub">Bound: ≤ {1.0 / (2**result.num_counting_qubits):.5f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="qpe-metric-card">
                <div class="qpe-metric-label">Peak Probability</div>
                <div class="qpe-metric-val">{result.success_probability * 100:.1f}%</div>
                <div class="qpe-metric-sub">{result.raw_counts.get(result.most_probable_bitstring, 0)} / {result.total_shots} shots</div>
            </div>
            """,
            unsafe_allow_html=True
        )
