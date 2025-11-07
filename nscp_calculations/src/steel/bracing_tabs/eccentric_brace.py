import streamlit as st
import pandas as pd

def display():
    st.header("Eccentric Brace Connection Design (NSCP 2015 / AISC 360-10)")

    # -----------------------------
    # INPUT PARAMETERS
    # -----------------------------
    st.subheader("Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        P_u = st.number_input("Axial Force (Pᵤ, kN)", value=200.0)
        Fy = st.number_input("Yield Strength Fy (MPa)", value=345.0)
        Fu = st.number_input("Ultimate Strength Fu (MPa)", value=450.0)

    with col2:
        Vu = st.number_input("Shear Force (Vᵤ, kN)", value=150.0)
        M_u = st.number_input("Moment (Mᵤ, kN·m)", value=80.0)
        e = st.number_input("Eccentricity (mm)", value=300.0)

    with col3:
        Aw = st.number_input("Web Area Aw (mm²)", value=5000.0)
        Zx = st.number_input("Plastic Modulus Zx (mm³)", value=3.5e6)
        phi = 0.9

    # -----------------------------
    # DESIGN CALCULATIONS
    # -----------------------------
    # st.subheader("Design Calculations")

    Vn = 0.6 * Fy * Aw / 1000       # Nominal shear (kN)
    Mn = Fy * Zx / 1e6              # Nominal moment (kN·m)
    phiVn = phi * Vn
    phiMn = phi * Mn

    # Check conditions
    shear_ok = phiVn >= Vu
    moment_ok = phiMn >= M_u

    interaction_ratio = (Vu / phiVn) + (M_u / phiMn)
    # -------------------------------------------------
    # RESULTS TABLE
    # -------------------------------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "Axial Force, Pᵤ (kN)",
            "Shear Force, Vᵤ (kN)",
            "Moment, Mᵤ (kN·m)",
            "Eccentricity, e (mm)",
            "Yield Strength, Fy (MPa)",
            "Ultimate Strength, Fu (MPa)",
            "Web Area, Aw (mm²)",
            "Plastic Modulus, Zx (mm³)",
            "Nominal Shear Strength, Vn (kN)",
            "Nominal Moment Strength, Mn (kN·m)",
            "Design Shear Strength, φVn (kN)",
            "Design Moment Strength, φMn (kN·m)",
            "Interaction Ratio (Vu/φVn + Mu/φMn)"
        ],
        "Value": [
            f"{P_u:.2f}",
            f"{Vu:.2f}",
            f"{M_u:.2f}",
            f"{e:.2f}",
            f"{Fy:.2f}",
            f"{Fu:.2f}",
            f"{Aw:.2f}",
            f"{Zx:.2f}",
            f"{Vn:.2f}",
            f"{Mn:.2f}",
            f"{phiVn:.2f}",
            f"{phiMn:.2f}",
            f"{interaction_ratio:.2f}"
        ]
    })

    st.table(df)

    # -----------------------------
    # RESULT SUMMARY
    # -----------------------------
    if shear_ok and moment_ok:
        st.success("✅ Connection design satisfies strength requirements per NSCP 2015 / AISC 360-10.")
    else:
        st.error("❌ Connection design does not satisfy strength requirements.")

    st.caption("Reference: NSCP 2015 / AISC 360-10 — Section Eccentric Braced Frame Design Provisions")
