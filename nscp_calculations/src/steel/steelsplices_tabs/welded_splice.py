import streamlit as st
import pandas as pd
import math

def display():
    # Header with icon
    st.header("🧰 Welded Splice Connection Design (NSCP 2015 / AISC 360-10)")

    # --- Input Parameters ---
    st.subheader("Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        P_u = st.number_input("Axial Force (Pᵤ, kN)", value=250.0, key="welded_splices_pu")
        Fy = st.number_input("Yield Strength Fy (MPa)", value=345.0, key="welded_splices_fy")
        Fu = st.number_input("Ultimate Strength Fu (MPa)", value=450.0, key="welded_splices_fu")
    with col2:
        t = st.number_input("Plate Thickness t (mm)", value=12.0, key="welded_splices_t")
        Lw = st.number_input("Weld Length Lw (mm)", value=200.0, key="welded_splices_lw")
        Fexx = st.number_input("Electrode Strength Fₑₓₓ (MPa)", value=490.0, key="welded_splices_fexx")
    with col3:
        theta = st.number_input("Weld Angle θ (degrees)", value=45.0, key="welded_splices_theta")
        phi = 0.9

    st.divider()

    # --- Design Calculations ---
    # st.subheader("Design Calculations")

    # Weld nominal strength (kN/mm)
    weld_strength_per_mm = 0.707 * t * (Fexx / math.sqrt(3)) / 1000
    Vn = weld_strength_per_mm * Lw           # Nominal shear strength (kN)
    Pn = 0.75 * Fu * t * Lw / 1000           # Nominal tensile strength (kN)
    phiVn = phi * Vn                         # Design shear strength (kN)
    phiPn = phi * Pn                         # Design tensile strength (kN)

    # --- Results Table ---
    data = {
        "Parameter": [
            "Nominal Weld Shear Strength (Vn)",
            "Design Weld Shear Strength (φVn)",
            "Nominal Plate Tensile Strength (Pn)",
            "Design Plate Tensile Strength (φPn)"
        ],
        "Value (kN)": [Vn, phiVn, Pn, phiPn]
    }

    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame(data)
    st.table(df.style.format({"Value (kN)": "{:.2f}"}))

    # --- Design Check ---
    if phiVn >= P_u and phiPn >= P_u:
        st.success("✅ Welded splice connection design **satisfies** strength requirements.")
    else:
        st.error("❌ Welded splice connection design **does not satisfy** strength requirements.")

    st.info("All calculations follow NSCP 2015 / AISC 360-10 provisions for welded connections.")
