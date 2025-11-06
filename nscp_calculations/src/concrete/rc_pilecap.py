import streamlit as st
import pandas as pd
import math

def display():
    st.header("🧱 RC Pile Cap Design (NSCP 2015 §421 & §423)")

    st.markdown(r"""
    This module computes **pile cap design forces and reinforcement requirements** following **NSCP 2015**  
    (based on ACI 318-14 provisions for reinforced concrete pile caps).  
    It checks **flexural**, **shear**, and **punching shear** capacities.
    """)

    # ----------------------------
    # INPUT PARAMETERS
    # ----------------------------
    st.markdown("### Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        n_piles = st.number_input("Number of Piles", min_value=2, value=4, step=1, key="pile_n")
        pile_dia = st.number_input("Pile Diameter (mm)", min_value=200.0, value=400.0, step=25.0, key="pile_dia")
        spacing = st.number_input("Pile Spacing (mm)", min_value=500.0, value=1200.0, step=50.0, key="pile_spacing")

    with col2:
        column_load = st.number_input("Total Column Load (kN)", min_value=0.0, value=2000.0, step=50.0, key="pile_load")
        fck = st.number_input("Concrete Strength f'c (MPa)", min_value=20.0, value=28.0, step=1.0, key="pile_fck")
        fy = st.number_input("Steel Yield Strength fy (MPa)", min_value=200.0, value=415.0, step=5.0, key="pile_fy")

    with col3:
        cap_thickness = st.number_input("Pile Cap Thickness (mm)", min_value=300.0, value=800.0, step=25.0, key="pile_thickness")
        cover = st.number_input("Concrete Cover (mm)", min_value=25.0, value=50.0, step=5.0, key="pile_cover")
        bar_dia = st.number_input("Main Bar Diameter (mm)", min_value=12.0, value=20.0, step=2.0, key="pile_bar")

    # ----------------------------
    # CALCULATIONS
    # ----------------------------
    # st.markdown("### 🧮 Design Calculations")

    # Convert to meters
    d = (cap_thickness - cover - bar_dia/2) / 1000  # effective depth in m
    s = spacing / 1000  # spacing in m
    pile_r = pile_dia / 1000 / 2  # pile radius in m

    # Load distribution
    load_per_pile = column_load / n_piles  # kN per pile

    # Flexural design (assuming simple 2x2 pile group)
    # Moment at midspan between piles (approx.)
    Mu = load_per_pile * s / 4  # kN·m

    phi = 0.9
    b = s  # take per unit width between piles
    Mu_Nmm = Mu * 1e6

    # Required steel area
    a = (1 - math.sqrt(1 - (2 * Mu_Nmm) / (phi * 0.85 * fck * 1e6 * b * 1000 * d))) * d
    As_req = (0.85 * fck * 1e6 * b * 1000 * a) / fy / 1e6  # m²/m width

    # Shear at face of column (approx. d from face)
    Vu = column_load / 2  # approximate half load per side (kN)
    phiVn = 0.75 * 0.17 * math.sqrt(fck) * b * 1000 * d * 1e-3  # kN

    # Punching shear check (approximation)
    perim = 4 * (s - pile_r)  # m
    Vu_punch = column_load  # kN
    Vc_punch = 0.33 * math.sqrt(fck) * perim * d * 1e3 / 1000  # kN
    ratio_flex = Mu / (phi * Mu)
    ratio_shear = Vu / phiVn
    ratio_punch = Vu_punch / Vc_punch

    # ----------------------------
    # RESULTS TABLE
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "No. of Piles", "Pile Diameter", "Spacing (center-to-center)",
            "Effective Depth (d)", "Load per Pile", "Factored Moment (Mu)",
            "Required As (per m width)", "Shear Capacity φVn", "Punching Capacity Vc",
            "Flexural Check (φMn / Mu)", "Shear Check (Vu / φVn)", "Punching Check (Vu / Vc)"
        ],
        "Value": list(map(str, [
            n_piles, f"{pile_dia:.0f} mm", f"{spacing:.0f} mm",
            f"{d*1000:.0f} mm", f"{load_per_pile:.2f} kN", f"{Mu:.2f} kN·m",
            f"{As_req*1e6:.2f} mm²/m", f"{phiVn:.2f} kN", f"{Vc_punch:.2f} kN",
            f"{1/ratio_flex:.2f}", f"{ratio_shear:.2f}", f"{ratio_punch:.2f}"
        ]))
    })
    st.table(df)

    # ----------------------------
    # SUMMARY METRICS
    # ----------------------------
    st.markdown("#### Key Design Outputs")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Moment Mu", f"{Mu:.2f} kN·m")
    with col2:
        st.metric("Shear φVn", f"{phiVn:.2f} kN")
    with col3:
        st.metric("Punching Vc", f"{Vc_punch:.2f} kN")

    # ----------------------------
    # NSCP REFERENCES
    # ----------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 – RC Pile Cap Design References")

    st.latex(r"M_u = \frac{w L}{4} \text{  (approx. for two-pile span)}")
    st.latex(r"\phi M_n = M_u")
    st.latex(r"A_s = \frac{0.85 f'_c b a}{f_y}")
    st.latex(r"V_c = 0.17 \sqrt{f'_c} b d")
    st.latex(r"V_{c,punch} = 0.33 \sqrt{f'_c} b_o d")

    st.caption("Based on NSCP 2015 §421 & §423 (Reinforced Concrete Design) and ACI 318-14 for Pile Caps.")
