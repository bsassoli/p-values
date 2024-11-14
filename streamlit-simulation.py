import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_sample():
    # Generate one sample of size 54 (5+9+17+23 from original data)
    samples = []
    for _ in range(54):
        sex = np.random.choice(['M', 'F'])
        arm = np.random.choice(['Sx', 'Dx'])
        samples.append([sex, arm])
    
    # Count frequencies
    counts = {
        'M_Sx': 0, 'M_Dx': 0,
        'F_Sx': 0, 'F_Dx': 0
    }
    
    for sex, arm in samples:
        counts[f'{sex}_{arm}'] += 1
    
    # Calculate proportions
    male_dx = counts['M_Dx'] / (counts['M_Dx'] + counts['M_Sx'])
    female_dx = counts['F_Dx'] / (counts['F_Dx'] + counts['F_Sx'])
    
    return female_dx - male_dx

def create_histogram_figure(differences, observed_diff=0.06, show_p_value_area=True):
    fig = go.Figure()
    
    # Create histogram
    fig.add_trace(go.Histogram(
        x=differences,
        nbinsx=40,
        name='Samples',
        marker_color='rgba(147, 197, 253, 0.6)'  # Light blue with transparency
    ))
    
    # Add vertical lines for observed difference
    fig.add_vline(
        x=observed_diff,
        line=dict(color='red', width=2),
        annotation_text="Observed",
        annotation_position="top"
    )
    fig.add_vline(
        x=-observed_diff,
        line=dict(color='red', width=2)
    )
    
    # Add shaded p-value areas if requested
    if show_p_value_area:
        # Get the y-range for the shading
        max_y = max(fig.data[0].y) if fig.data[0].y is not None else 100
        
        # Add shaded areas
        fig.add_vrect(
            x0=observed_diff, x1=1,
            fillcolor="rgba(254, 202, 202, 0.3)",  # Light red with transparency
            layer="below", line_width=0,
        )
        fig.add_vrect(
            x0=-1, x1=-observed_diff,
            fillcolor="rgba(254, 202, 202, 0.3)",  # Light red with transparency
            layer="below", line_width=0,
        )
    
    # Update layout
    fig.update_layout(
        title=None,
        xaxis_title="Difference in proportions (Female - Male)",
        yaxis_title="Frequency",
        showlegend=False,
        plot_bgcolor='white',
        xaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(128, 128, 128, 0.1)',
            zerolinecolor='rgba(128, 128, 128, 0.2)'
        )
    )
    
    return fig

def main():
    st.set_page_config(page_title="P-Value Simulation", layout="wide")
    
    # Title and description
    st.title("Arm Crossing Preference Simulation")
    st.markdown(
        "Distribution of differences in right arm preference between females and males"
    )
    
    # Initialize session state
    if 'differences' not in st.session_state:
        st.session_state.differences = []
    if 'running' not in st.session_state:
        st.session_state.running = False
        
    # Controls in columns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button(
            "▶ Start" if not st.session_state.running else "■ Stop",
            type="primary" if not st.session_state.running else "secondary"
        ):
            st.session_state.running = not st.session_state.running
            
    with col2:
        if st.button("Reset"):
            st.session_state.differences = []
            st.session_state.running = False
            
    with col3:
        target_samples = st.selectbox(
            "Target samples:",
            options=[100, 500, 1000, 5000, 10000],
            index=2
        )
        
    with col4:
        show_p_value = st.checkbox("Show p-value region", value=True)
    
    # Progress and p-value statistics
    current_samples = len(st.session_state.differences)
    st.progress(min(1.0, current_samples / target_samples))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Samples", f"{current_samples} / {target_samples}")
    with col2:
        if current_samples > 0:
            observed_diff = 0.06
            p_value = sum(abs(d) >= abs(observed_diff) for d in st.session_state.differences) / current_samples
            st.metric("P-value", f"{p_value:.4f}")
    
    # Create and display the histogram
    fig = create_histogram_figure(
        st.session_state.differences,
        observed_diff=0.06,
        show_p_value_area=show_p_value
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Auto-update when running
    if st.session_state.running and current_samples < target_samples:
        st.session_state.differences.append(generate_sample())
        st.experimental_rerun()

if __name__ == "__main__":
    main()
