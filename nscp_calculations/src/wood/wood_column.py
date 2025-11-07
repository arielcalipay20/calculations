import streamlit as st
import pandas as pd
import math

def display():
    st.header("🌲 Wood Post Design (NSCP 2015 Section 613)")

    st.markdown(r"""
    This module calculates **axial capacity, slenderness, and bending interaction**  
    for **wood columns** based on **NSCP 2015 Section 613**, referencing  
    NDS-2015 for design values and adjustment factors.
    """)

    # ----------------------------
    # INPUT PARAMETERS
    # ----------------------------
    st.subheader("Input Parameters")

    col1, col2, col3 = st.columns(3)
    with col1:
        height = st.number_input("Column Height (m)", min_value=1.0, value=3.0, step=0.1, key="wood_col_height")
        width = st.number_input("Column Width (mm)", min_value=75.0, value=150.0, step=5.0, key="wood_col_width")
        depth = st.number_input("Column Depth (mm)", min_value=75.0, value=150.0, step=5.0, key="wood_col_depth")
    with col2:
        Fc = st.number_input("Allowable Axial Stress Fc (MPa)", min_value=3.0, value=10.0, step=0.5, key="wood_col_Fc")
        Fb = st.number_input("Allowable Bending Stress Fb (MPa)", min_value=3.0, value=8.0, step=0.5, key="wood_col_Fb")
        E = st.number_input("Modulus of Elasticity E (MPa)", min_value=5000.0, value=10000.0, step=100.0, key="wood_col_E")
    with col3:
        axial_load = st.number_input("Axial Load (kN)", min_value=0.0, value=100.0, step=5.0, key="wood_col_P")
        moment = st.number_input("Bending Moment (kN·m)", min_value=0.0, value=5.0, step=0.1, key="wood_col_M")
        K = st.number_input("Effective Length Factor (K)", min_value=0.5, value=1.0, step=0.1, key="wood_col_K")

    # ----------------------------
    # CALCULATIONS
    # ----------------------------
    # st.subheader("Design Calculations")

    # Convert units
    b = width / 1000  # m
    d = depth / 1000  # m
    L = height  # m

    A = b * d  # cross-sectional area, m²
    Imin = (min(b, d) * (max(b, d)**3)) / 12  # m⁴, about minor axis
    r = math.sqrt(Imin / A)  # radius of gyration (m)

    # Convert to consistent units (N, mm)
    P = axial_load * 1e3
    M = moment * 1e6

    # Slenderness ratio
    slenderness = (K * L * 1000) / (r * 1000)

    # Critical buckling stress (Euler’s formula)
    Fe = (math.pi**2 * E) / ((K * L / r)**2)

    # Column stability factor Cp (approximation)
    FcE = 0.822 * E / ((K * L / r)**2)
    Cp = min(1.0, math.sqrt(1 / (1 + Fc / FcE))) if FcE > 0 else 1.0

    # Adjusted compressive stress
    Fc_adj = Fc * Cp

    # Actual stresses
    fc_actual = (P / (A * 1e6))  # MPa
    fb_actual = (M / (1e6 * (b * (d**2) / 6)))  # MPa

    # Combined stress check per NDS interaction
    interaction = (fc_actual / Fc_adj) + (fb_actual / Fb)

    # ----------------------------
    # RESULTS TABLE
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")

    df = pd.DataFrame({
        "Parameter": [
            "Column Height (m)",
            "Width (mm)",
            "Depth (mm)",
            "Area (mm²)",
            "Radius of Gyration (mm)",
            "Slenderness Ratio (KL/r)",
            "Critical Stress Fe (MPa)",
            "Stability Factor Cp",
            "Adjusted Fc' (MPa)",
            "Actual Axial Stress (MPa)",
            "Actual Bending Stress (MPa)",
            "Interaction Ratio (fc/Fc' + fb/Fb)"
        ],
        "Value": [
            f"{height:.2f}", f"{width:.0f}", f"{depth:.0f}",
            f"{A*1e6:.0f}", f"{r*1000:.2f}", f"{slenderness:.1f}",
            f"{Fe:.2f}", f"{Cp:.3f}", f"{Fc_adj:.2f}",
            f"{fc_actual:.3f}", f"{fb_actual:.3f}", f"{interaction:.3f}"
        ]
    })
    st.table(df.set_index("Parameter"))

    # ----------------------------
    # STATUS CHECKS
    # ----------------------------
    st.markdown("### Performance Checks")

    if fc_actual <= Fc_adj:
        st.success(f"Axial Compression OK — {fc_actual:.2f} ≤ {Fc_adj:.2f} MPa")
    else:
        st.error(f"Axial Compression NG — {fc_actual:.2f} > {Fc_adj:.2f} MPa")

    if interaction <= 1.0:
        st.success(f"Combined Stress OK — Interaction = {interaction:.3f} ≤ 1.0")
    else:
        st.error(f"Combined Stress NG — Interaction = {interaction:.3f} > 1.0")

    # ----------------------------
    # REFERENCES
    # ----------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 References (Section 613)")
    st.markdown(r"""
    - **Axial stress:** \( f_c = \frac{P}{A} \leq F'_c \)
    - **Bending stress:** \( f_b = \frac{M}{S} \leq F_b \)
    - **Combined stress:** \( \frac{f_c}{F'_c} + \frac{f_b}{F_b} \leq 1.0 \)
    - **Stability factor:** \( C_P = \sqrt{\frac{1}{1 + F_c / F_{cE}}} \)
    - **Slenderness check:** \( \frac{KL}{r} \leq 50 \) (typical for wood columns)
    """)
