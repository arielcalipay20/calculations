import streamlit as st
import pandas as pd
import math

def display():
    st.header("🟦 Base Plate Moment Connection Design (NSCP 2015)")

    st.markdown(r"""
    ### Overview  
    This calculator follows the **NSCP 2015 Section 421 & 425** provisions for base plate design  
    under **axial load + bending moment**.  
    The base plate must be checked for bearing pressure and bending capacity.
    """)

    # --- Input Section ---
    st.subheader("Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        Pu = st.number_input("Factored Axial Load, Pu (kN)", value=800.0, key="pu")
        Mu = st.number_input("Factored Moment, Mu (kN·m)", value=120.0, key="mu")
        fy = st.number_input("Steel Yield Strength Fy (MPa)", value=248.0, key="baseplate_fy")
        fc_prime = st.number_input("Concrete Compressive Strength f'c (MPa)", value=21.0, key="fc_prime")
        B = st.number_input("Base Plate Width, B (mm)", value=400.0, key="bp_width")
    
    with col2:
        N = st.number_input("Base Plate Length, N (mm)", value=400.0, key="bp_length")
        Col_w = st.number_input("Column Width, bc (mm)", value=250.0, key="col_width")
        Col_t = st.number_input("Column Thickness, tc (mm)", value=250.0, key="col_thick")
        phi = st.number_input("Resistance Factor φ", value=0.9, key="phi_bp")

    # --- Derived Parameters ---
    # Concrete bearing strength (NSCP 425.2)
    q_allow = 0.85 * fc_prime

    # Area of base plate and column
    Abp = B * N
    Ac = Col_w * Col_t

    # Eccentricity
    e = Mu * 1e6 / (Pu * 1e3) if Pu > 0 else 0  # in mm

    # Compute bearing pressure distribution
    if e <= (N / 6):
        # full bearing (rectangular distribution)
        q_max = Pu * 1e3 / Abp * (1 + 6 * e / N)
        q_min = Pu * 1e3 / Abp * (1 - 6 * e / N)
    else:
        # partial bearing (triangular distribution)
        a = N - 2 * e
        q_max = 2 * Pu * 1e3 / (a * B)
        q_min = 0

    # Plate bending check (assume cantilever projection beyond column)
    m = (B - Col_w) / 2  # mm
    q_u = q_max  # worst-case pressure on projection
    M_req = q_u * m**2 / 2 / 1e6  # kN·m per mm width

    # Required thickness (mm)
    t_req = math.sqrt((6 * M_req * 1e6) / (fy * 1e6))

    # Check status
    safe_bearing = q_max <= q_allow * 1e3
    safe_status = "✅ Safe" if safe_bearing else "⚠️ Overstressed (Reduce load or increase plate size)"

    # --- Display Results ---
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    # --- Output Table ---
    results = {
        "Parameter": [
            "Factored Axial Load Pu (kN)",
            "Factored Moment Mu (kN·m)",
            "Base Plate Width B (mm)",
            "Base Plate Length N (mm)",
            "Eccentricity e (mm)",
            "Max Bearing Pressure qmax (MPa)",
            "Min Bearing Pressure qmin (MPa)",
            "Allowable Concrete Bearing (MPa)",
            "Required Plate Thickness (mm)",
            "Safety Status"
        ],
        "Value": [
            f"{Pu:.2f}",
            f"{Mu:.2f}",
            f"{B:.2f}",
            f"{N:.2f}",
            f"{e:.2f}",
            f"{q_max/1e6:.3f}",
            f"{q_min/1e6:.3f}",
            f"{q_allow:.3f}",
            f"{t_req:.2f}",
            safe_status
        ]
    }
    st.table(pd.DataFrame(results))

    st.info(f"**Required Plate Thickness:** {t_req:.2f} mm\n\n**Maximum Bearing Pressure:** {q_max/1e6:.3f} MPa\n\n{safe_status}")
