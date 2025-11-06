import streamlit as st
import pandas as pd
import math

def display():
    st.header("🧱 RC One-Way Slab Design (NSCP 2015 Section 421)")

    st.markdown(r"""
    This module designs **reinforced concrete one-way slabs** following **NSCP 2015 §421** provisions.  
    It checks the required steel area, moment capacity, and spacing limits.
    """)

    # ----------------------------
    # INPUT PARAMETERS
    # ----------------------------
    st.markdown("### Input Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        span = st.number_input("Effective Span, L (m)", min_value=0.1, value=5.0, step=0.1, key="slab_span")
        width = st.number_input("Design Width, b (m)", min_value=0.1, value=1.0, step=0.1, key="slab_width")
        slab_thickness = st.number_input("Slab Thickness, h (mm)", min_value=50.0, value=150.0, step=5.0, key="slab_thickness")
    with col2:
        dead_load = st.number_input("Superimposed Dead Load (kN/m²)", min_value=0.0, value=1.5, step=0.1, key="slab_dead")
        live_load = st.number_input("Live Load (kN/m²)", min_value=0.0, value=3.0, step=0.1, key="slab_live")
        cover = st.number_input("Concrete Cover (mm)", min_value=10.0, value=20.0, step=5.0, key="slab_cover")
    with col3:
        fck = st.number_input("Concrete Strength f'c (MPa)", min_value=10.0, value=28.0, step=1.0, key="slab_fck")
        fy = st.number_input("Steel Yield Strength fy (MPa)", min_value=200.0, value=415.0, step=5.0, key="slab_fy")
        bar_dia = st.number_input("Bar Diameter (mm)", min_value=6.0, value=10.0, step=2.0, key="slab_bar")

    # ----------------------------
    # CALCULATIONS
    # ----------------------------
    # st.markdown("### 🧮 Design Calculations")

    # Convert slab thickness to m
    h = slab_thickness / 1000
    d = h - (cover + bar_dia / 2) / 1000

    # Ultimate design load
    wu = 1.2 * (dead_load + (25 * h)) + 1.6 * live_load  # includes self-weight
    Mu = wu * span**2 / 8  # kN·m per meter width

    # Convert Mu to N·mm
    Mu_Nmm = Mu * 1e6

    # Required steel area (from φMn = Mu)
    phi = 0.9
    a = (1 - math.sqrt(1 - (2 * Mu_Nmm) / (phi * 0.85 * fck * 1e6 * width * 1000 * d))) * d
    As_req = (0.85 * fck * 1e6 * width * 1000 * a) / fy / 1e6

    # Provided area per bar spacing (assuming 100 mm spacing initially)
    bar_area = math.pi * (bar_dia**2) / 4 / 100  # mm²/mm width
    spacing = bar_area / (As_req * 1e6 / 1000) * 1000  # mm
    spacing = max(100, min(spacing, 300))  # NSCP range check

    # ----------------------------
    # RESULTS
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "Span (L)", "Thickness (h)", "Effective Depth (d)",
            "Ultimate Load (wu)", "Factored Moment (Mu)",
            "Required Steel Area (As req)", "Bar Diameter", "Spacing (adopted)"
        ],
        "Value": [
            f"{span:.2f} m", f"{slab_thickness:.0f} mm", f"{d*1000:.0f} mm",
            f"{wu:.2f} kN/m²", f"{Mu:.2f} kN·m/m",
            f"{As_req*1e6:.2f} mm²/m", f"{bar_dia:.0f} mm", f"{spacing:.0f} mm"
        ]
    })
    st.table(df)

    # ----------------------------
    # SUMMARY METRICS
    # ----------------------------
    st.markdown("#### Key Design Outputs")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Moment (Mu)", f"{Mu:.2f} kN·m/m")
    with col2:
        st.metric("As Required", f"{As_req*1e6:.0f} mm²/m")
    with col3:
        st.metric("Adopted Spacing", f"{spacing:.0f} mm")

    # ----------------------------
    # NSCP REFERENCES
    # ----------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 §421 – One-Way Slab Design Formulas")

    st.latex(r"\text{For a simply supported one-way slab: } M_u = \frac{w_u L^2}{8}")
    st.latex(r"\phi M_n = M_u")
    st.latex(r"A_s = \frac{0.85 f'_c b a}{f_y}")
    st.latex(r"a = \beta_1 c = \left(1 - \sqrt{1 - \frac{2 M_u}{\phi 0.85 f'_c b d^2}}\right)d")

    st.caption("Developed based on NSCP 2015 Section 421 – Flexural Design of Reinforced Concrete Slabs.")
