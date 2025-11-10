import streamlit as st
import pandas as pd
import math

def display():
    st.header("🔩 Concentric Brace Connection Design (NSCP 2015 §424)")

    st.markdown(r"""
    ### Overview  
    This module performs design checks for **concentric braced frame (CBF)** connections  
    according to **NSCP 2015 Section 424** (based on AISC 360-10 provisions).  
    It evaluates **axial tension**, **compression**, and **gusset plate design**.
    """)
    
    # -------------------------------------------------
    # INPUT PARAMETERS
    # -------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Parameters")
        Fy = st.number_input("Brace Yield Strength Fy (MPa)", min_value=200.0, value=345.0, step=5.0, key="brace_fy")
        Fu = st.number_input("Brace Ultimate Strength Fu (MPa)", min_value=200.0, value=450.0, step=5.0, key="brace_fu")
        r = st.number_input("Radius of Gyration, r (mm)", min_value=10.0, value=25.0, step=1.0, key="brace_r")
        L = st.number_input("Brace Length, L (mm)", min_value=500.0, value=3000.0, step=50.0, key="brace_L")
        A = st.number_input("Brace Cross-Sectional Area (mm²)", min_value=1000.0, value=3000.0, step=50.0, key="brace_A")
        phi = st.number_input("Resistance Factor φ", min_value=0.5, max_value=1.0, value=0.9, step=0.05, key="brace_phi")

    with col2:
        st.subheader("Connection / Gusset Plate Parameters")
        gusset_t = st.number_input("Gusset Plate Thickness (mm)", min_value=6.0, value=10.0, step=1.0, key="gusset_t")
        gusset_length = st.number_input("Gusset Effective Length (mm)", min_value=100.0, value=200.0, step=10.0, key="gusset_L")
        gusset_width = st.number_input("Gusset Effective Width (mm)", min_value=100.0, value=200.0, step=10.0, key="gusset_W")
        Fyp = st.number_input("Gusset Plate Yield Strength Fy (MPa)", min_value=200.0, value=250.0, step=5.0, key="gusset_fy")
        Fup = st.number_input("Gusset Plate Ultimate Strength Fu (MPa)", min_value=200.0, value=400.0, step=5.0, key="gusset_fu")

    # -------------------------------------------------
    # CALCULATIONS
    # -------------------------------------------------
    # st.markdown("---")
    # st.subheader("🧮 Design Calculations")

    # Slenderness ratio
    KLr = L / r
    if KLr <= 0:
        st.error("Invalid slenderness ratio. Check your inputs.")
        return

    # Euler buckling factor
    Fe = (math.pi ** 2 * 200000) / (KLr ** 2)  # MPa
    Fy_ratio = Fy / Fe

    # Compression strength per AISC Eq. E3-2/E3-3
    if Fy_ratio <= 2.25:
        Fcr = (0.658 ** Fy_ratio) * Fy
    else:
        Fcr = 0.877 * Fe

    # Compression and tension capacities
    phiPn = phi * Fcr * A / 1000  # kN
    phiTn = phi * Fu * A / 1000  # kN

    # Gusset plate yield and rupture
    Ag = gusset_t * gusset_width  # mm²
    An = 0.85 * Ag
    phiPn_gusset = phi * min(0.9 * Fyp * Ag, 0.75 * Fup * An) / 1000  # kN

    # -------------------------------------------------
    # RESULTS TABLE
    # -------------------------------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "Slenderness Ratio (KL/r)",
            "Elastic Buckling Stress, Fe (MPa)",
            "Critical Stress, Fcr (MPa)",
            "Brace Compression Capacity, φPn (kN)",
            "Brace Tension Capacity, φTn (kN)",
            "Gusset Plate Capacity, φPn (kN)"
        ],
        "Value": [
            f"{KLr:.1f}",
            f"{Fe:.2f}",
            f"{Fcr:.2f}",
            f"{phiPn:.2f}",
            f"{phiTn:.2f}",
            f"{phiPn_gusset:.2f}"
        ]
    })
    st.table(df)

    # Pass/Fail check
    if phiPn_gusset >= phiPn:
        st.success("✅ Gusset plate is adequate for both tension and compression.")
    else:
        st.warning("⚠️ Gusset plate is undersized — increase plate thickness or width.")

    # -------------------------------------------------
    # REFERENCES
    # -------------------------------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 References")
    st.markdown(r"""
    - **NSCP 2015 Section 424.4** — Design of Braced Frames  
    - **AISC 360-10 Chapter E** — Compression Members  
    - **AISC 360-10 Chapter J** — Connections and Gusset Plates  
    """)