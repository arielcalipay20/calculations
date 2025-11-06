import streamlit as st
import pandas as pd
import math

def display():
    st.header("🌲 Wood Beam Design (NSCP 2015 Section 611)")

    st.markdown("""
    This tool computes **bending, shear, and deflection checks** for wood beams 
    based on **NSCP 2015 – Section 611 (Design of Wood Structures)**, 
    referencing NDS provisions for allowable stresses and serviceability limits.
    """)

    # ----------------------------
    # INPUT PARAMETERS
    # ----------------------------
    st.subheader("Input Parameters")

    col1, col2, col3 = st.columns(3)
    with col1:
        span = st.number_input("Beam Span (m)", min_value=1.0, value=4.0, step=0.1, key="wood_span")
        spacing = st.number_input("Beam Spacing (m)", min_value=0.3, value=0.6, step=0.05, key="wood_spacing")
        load_dead = st.number_input("Dead Load (kN/m²)", min_value=0.0, value=1.0, step=0.1, key="wood_DL")
    with col2:
        load_live = st.number_input("Live Load (kN/m²)", min_value=0.0, value=2.0, step=0.1, key="wood_LL")
        width = st.number_input("Beam Width (mm)", min_value=50.0, value=100.0, step=5.0, key="wood_b")
        depth = st.number_input("Beam Depth (mm)", min_value=100.0, value=300.0, step=5.0, key="wood_d")
    with col3:
        Fb = st.number_input("Allowable Bending Stress Fb (MPa)", min_value=5.0, value=10.0, step=0.5, key="wood_Fb")
        Fv = st.number_input("Allowable Shear Stress Fv (MPa)", min_value=0.5, value=1.0, step=0.1, key="wood_Fv")
        E = st.number_input("Modulus of Elasticity E (MPa)", min_value=5000.0, value=10000.0, step=100.0, key="wood_E")

    # ----------------------------
    # CALCULATIONS
    # ----------------------------
    # st.subheader("Design Calculations")

    # Load per meter of beam
    w_total = (load_dead + load_live) * spacing  # kN/m

    # Maximum moment and shear (simply supported beam, uniform load)
    M_max = (w_total * span**2) / 8  # kN·m
    V_max = (w_total * span) / 2     # kN

    # Section properties
    b = width / 1000  # convert mm to m
    d = depth / 1000  # convert mm to m
    S = (b * d**2) / 6  # section modulus (m³)
    I = (b * d**3) / 12 # moment of inertia (m⁴)

    # Stress calculations
    Fb_actual = (M_max * 1e6) / (S * 1e6) / 1000  # MPa
    Fv_actual = (1.5 * V_max * 1e3) / (b * d * 1e6) * 1000  # MPa

    # Deflection (max for uniform load: 5wL⁴ / 384EI)
    Δ = (5 * (w_total * 1e3) * (span**4)) / (384 * E * I * 1e9)  # meters
    Δ_mm = Δ * 1000

    # Allowable deflection (L/240 typical)
    Δ_allow = span * 1000 / 240
    deflection_ok = Δ_mm <= Δ_allow

    # Check results
    ratio_M = Fb_actual / Fb
    ratio_V = Fv_actual / Fv
    ratio_D = Δ_mm / Δ_allow

    # ----------------------------
    # RESULTS TABLE
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "Span (m)",
            "Spacing (m)",
            "Dead Load (kN/m²)",
            "Live Load (kN/m²)",
            "Total Load (kN/m)",
            "Max Moment (kN·m)",
            "Max Shear (kN)",
            "Actual Bending Stress (MPa)",
            "Allowable Bending Stress (MPa)",
            "Actual Shear Stress (MPa)",
            "Allowable Shear Stress (MPa)",
            "Deflection (mm)",
            "Allowable Deflection (mm)",
            "Deflection Ratio (Δ / Δ_allow)"
        ],
        "Value": [
            f"{span:.2f}", f"{spacing:.2f}", f"{load_dead:.2f}", f"{load_live:.2f}",
            f"{w_total:.2f}", f"{M_max:.2f}", f"{V_max:.2f}",
            f"{Fb_actual:.2f}", f"{Fb:.2f}", f"{Fv_actual:.2f}", f"{Fv:.2f}",
            f"{Δ_mm:.2f}", f"{Δ_allow:.2f}", f"{ratio_D:.3f}"
        ]
    })
    st.table(df.set_index("Parameter"))

    # ----------------------------
    # STATUS MESSAGES
    # ----------------------------
    st.markdown("### Performance Checks")

    if ratio_M <= 1:
        st.success(f"Bending OK — Utilization: {ratio_M:.2f}")
    else:
        st.error(f"Bending NG — Utilization: {ratio_M:.2f}")

    if ratio_V <= 1:
        st.success(f"Shear OK — Utilization: {ratio_V:.2f}")
    else:
        st.error(f"Shear NG — Utilization: {ratio_V:.2f}")

    if deflection_ok:
        st.success(f"Deflection OK — {Δ_mm:.2f} mm ≤ {Δ_allow:.2f} mm")
    else:
        st.error(f"Deflection NG — {Δ_mm:.2f} mm > {Δ_allow:.2f} mm")

    # ----------------------------
    # REFERENCES
    # ----------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 References (Section 611)")
    st.markdown(r"""
    - **Bending:** \( f_b = \frac{M}{S} \leq F_b \)  
    - **Shear:** \( f_v = \frac{1.5V}{b d} \leq F_v \)  
    - **Deflection:** \( \Delta = \frac{5wL^4}{384EI} \leq L/240 \) (typical)  
    - Based on NSCP 2015 §611 (Wood Design) and NDS-2015.
    """)
