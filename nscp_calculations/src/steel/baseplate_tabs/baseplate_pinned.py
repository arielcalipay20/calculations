import streamlit as st
import pandas as pd
import math

def display():
    st.header("🟩 Base Plate Pinned Connection Design (NSCP 2015)")

    st.markdown(r"""
    ### Overview  
    This tool designs a **pinned base plate** under **axial compression only** (no moment transfer),  
    following **NSCP 2015 Section 425** and **ACI 318 / AISC provisions**.  
    It checks **bearing pressure** under the plate and computes the **required plate thickness**.
    """)

    st.subheader("Input Parameters")

    # --- Two-column layout ---
    col1, col2 = st.columns(2)
    with col1:
        Pu = st.number_input("Factored Axial Load, Pu (kN)", value=1000.0, key="pu_bp_pinned")
        fy = st.number_input("Steel Yield Strength Fy (MPa)", value=248.0, key="fy_bp_pinned")
        fc_prime = st.number_input("Concrete Compressive Strength f'c (MPa)", value=21.0, key="fc_bp_pinned")
        phi = st.number_input("Resistance Factor φ", value=0.9, key="phi_bp_pinned")

    with col2:
        B = st.number_input("Base Plate Width, B (mm)", value=400.0, key="bp_width_pinned")
        N = st.number_input("Base Plate Length, N (mm)", value=400.0, key="bp_length_pinned")
        Col_w = st.number_input("Column Width, bc (mm)", value=250.0, key="col_width_pinned")
        Col_t = st.number_input("Column Thickness, tc (mm)", value=250.0, key="col_thick_pinned")

    # --- Bearing pressure check ---
    Abp = B * N  # mm²
    q_u = (Pu * 1e3) / Abp  # N/mm² = MPa
    q_allow = 0.85 * fc_prime  # MPa

    # --- Plate bending check (projection) ---
    m1 = (B - Col_w) / 2  # mm
    m2 = (N - Col_t) / 2  # mm

    # Use the larger projection for conservative thickness
    m = max(m1, m2)
    q = q_u * 1e6  # N/m²
    M_per_mm = q * m**2 / 2 / 1e6  # kN·m per mm width
    t_req = math.sqrt((6 * M_per_mm * 1e6) / (fy * 1e6))  # mm

    safe_bearing = q_u <= q_allow
    status = "✅ Safe" if safe_bearing else "⚠️ Overstressed"

    # --- Output Table ---
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
    
            "Axial Load Pu (kN)",
            "Bearing Pressure q (MPa)",
            "Allowable Bearing (MPa)",
            "Plate Projection m (mm)",
            "Required Thickness (mm)",
            "Status"
        ],
        "Value": [
            f"{Pu:.2f}",
            f"{q_u:.3f}",
            f"{q_allow:.3f}",
            f"{m:.1f}",
            f"{t_req:.2f}",
            status
        ]
    })

    st.table(df)
    st.info(f"**Required Plate Thickness:** {t_req:.2f} mm — {status}")

    # --- References ---
    st.markdown("---")
    st.subheader("📘 NSCP 2015 Reference")
    st.markdown(r"""
    - **NSCP 2015 §425.2** — Design of Base Plates for Axial Loads  
    - **ACI 318 §22.8.2** — Bearing on Concrete  
    - **AISC Design Guide 1** — Base Plate Design for Steel Columns  
    """)