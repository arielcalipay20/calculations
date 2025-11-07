import streamlit as st
import pandas as pd
import math

def display():
    st.header("🔩 Beam-Column Moment Bolted Connection Design (NSCP 2015 / AISC 360-10)")

    # -----------------------------
    # INPUT PARAMETERS
    # -----------------------------
    st.subheader("Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        M_u = st.number_input("Factored Moment (Mᵤ, kN·m)", value=120.0, key="m_u")
        V_u = st.number_input("Factored Shear (Vᵤ, kN)", value=80.0, key="v_u")
        bolt_dia = st.number_input("Bolt Diameter (mm)", value=20.0, key="bolt_dia")
        n_bolts = st.number_input("Number of Bolts", value=4, step=1, key="n_bolts")
    
    with col2:
        Fy = st.number_input("Yield Strength of Plate, Fy (MPa)", value=250.0, key="bolted_fy")
        Fu = st.number_input("Ultimate Strength of Bolt, Fu (MPa)", value=400.0, key="bolted_fu")
        edge_dist = st.number_input("Edge Distance (mm)", value=40.0, key="edge_dist")
        pitch = st.number_input("Bolt Pitch (mm)", value=80.0, key="bolted_pitch")

    with col3:
        plate_thk = st.number_input("End Plate Thickness (mm)", value=16.0, key="bolted_plate_thk")
        beam_depth = st.number_input("Beam Depth (mm)", value=400.0, key="bolted_beam_depth")
        phi = 0.9

    # -----------------------------
    # DESIGN CALCULATIONS
    # -----------------------------
    # st.subheader("Design Calculations")

    # Bolt group geometry
    lever_arm = (beam_depth - 2 * edge_dist) / 1000  # m
    T_per_bolt = (M_u * 1e6) / (n_bolts / 2 * lever_arm * 1000) / 1000  # kN per bolt in tension
    V_per_bolt = V_u / n_bolts  # kN

    # Bolt nominal tension and shear strength (AISC)
    Ab = math.pi * (bolt_dia ** 2) / 4 / 100  # mm² to cm²
    Rn_t = 0.75 * Fu * (math.pi * (bolt_dia**2) / 4) / 1000  # kN nominal tension
    Rn_v = 0.6 * Fu * (math.pi * (bolt_dia**2) / 4) / 1000  # kN nominal shear
    phiRn_t = phi * Rn_t
    phiRn_v = phi * Rn_v

    # Combined tension and shear per bolt (interaction)
    interaction_ratio = (T_per_bolt / phiRn_t) ** 2 + (V_per_bolt / phiRn_v) ** 2

    # Plate bending capacity check
    b_eff = pitch * (n_bolts / 2)
    Mn_plate = (Fy * b_eff * (plate_thk**2) / 4) / 1e6  # kN·m (approx)
    phiMn_plate = phi * Mn_plate

    # -------------------------------------------------
    # RESULTS TABLE
    # -------------------------------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame({
        "Parameter": [
            "Factored Moment (Mᵤ)",
            "Factored Shear (Vᵤ)",
            "Bolt Diameter",
            "No. of Bolts",
            "Bolt Ultimate Strength (Fu)",
            "Tension per Bolt (kN)",
            "Shear per Bolt (kN)",
            "Design Tension Capacity (φRnₜ, kN)",
            "Design Shear Capacity (φRnᵥ, kN)",
            "Interaction Ratio (T/φRnₜ)² + (V/φRnᵥ)²",
            "Plate Thickness (mm)",
            "Plate Design Moment Capacity (φMn, kN·m)"
        ],
        "Value": [
            f"{M_u:.2f} kN·m",
            f"{V_u:.2f} kN",
            f"{bolt_dia:.0f} mm",
            f"{n_bolts}",
            f"{Fu:.2f} MPa",
            f"{T_per_bolt:.2f}",
            f"{V_per_bolt:.2f}",
            f"{phiRn_t:.2f}",
            f"{phiRn_v:.2f}",
            f"{interaction_ratio:.2f}",
            f"{plate_thk:.2f}",
            f"{phiMn_plate:.2f}"
        ]
    })
    st.table(df)

    # -----------------------------
    # SUMMARY
    # -----------------------------
    if interaction_ratio <= 1.0 and M_u <= phiMn_plate:
        st.success("✅ Connection design satisfies NSCP / AISC strength requirements.")
    else:
        st.error("❌ Connection design does not satisfy NSCP / AISC strength requirements.")

    # -----------------------------
    # REFERENCES
    # -----------------------------
    st.markdown("---")
    st.caption(r"""
    **References:**
    - NSCP 2015 Section 505 & 507 (Structural Steel Design)
    - AISC 360-10, Chapter J & J3 (Bolted Moment Connections)
    - Design assumes double-row tension bolts and end plate bending per AISC provisions.
    """)
