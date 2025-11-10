import streamlit as st
import pandas as pd

def display():
    st.header("🪛 Shear Tab Simple Connection (NSCP 2015 / AISC 360-10)")

    st.subheader("Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        V_u = st.number_input("Factored Shear Force, Vᵤ (kN)", value=120.0, step=10.0, key="shear_tab_vu")
        Fy = st.number_input("Yield Strength Fy (MPa)", value=250.0, step=10.0, key="shear_tab_fy")
        Fu = st.number_input("Ultimate Strength Fu (MPa)", value=400.0, step=10.0, key="shear_tab_fu")

    with col2:
        t = st.number_input("Shear Tab Thickness (mm)", value=10.0, step=1.0, key="shear_tab_t")
        h_tab = st.number_input("Shear Tab Height (mm)", value=200.0, step=5.0, key="shear_tab_tab")
        n_bolts = st.number_input("Number of Bolts", min_value=1, value=2, step=1, key="shear_tab_n_bolts")

    with col3:
        bolt_dia = st.number_input("Bolt Diameter (mm)", value=20.0, step=2.0, key="shear_tab_bolt_dia")
        edge_dist = st.number_input("Edge Distance (mm)", value=40.0, step=5.0, key="shear_tab_edge_dist")
        phi = 0.9  # strength reduction factor

    # st.subheader("🧮 Design Calculations")

    # --- 1. Bolt Shear Capacity ---
    Ab = 3.1416 * (bolt_dia ** 2) / 4  # mm²
    Rn_bolt = 0.6 * Fu * Ab / 1000     # kN per bolt
    phiRn_bolt = phi * Rn_bolt

    # --- 2. Bearing Capacity ---
    Rn_bearing = 2.4 * bolt_dia * t * Fu / 1000  # kN per bolt
    phiRn_bearing = phi * Rn_bearing

    # --- 3. Shear Capacity of Plate ---
    Aw = h_tab * t                        # mm²
    Vn_plate = 0.6 * Fy * Aw / 1000       # kN
    phiVn_plate = phi * Vn_plate

    # --- 4. Total Capacity ---
    Vn_total = min(phiRn_bolt * n_bolts, phiRn_bearing * n_bolts, phiVn_plate)
    ratio = V_u / Vn_total if Vn_total > 0 else 0

    # --- 5. Result Table ---
    df = pd.DataFrame({
        "Parameter": [
            "Bolt Shear Capacity per Bolt (φRn, kN)",
            "Bearing Capacity per Bolt (φRn, kN)",
            "Shear Tab Plate Capacity (φVn, kN)",
            "Total Connection Capacity (kN)",
            "Applied Shear (Vᵤ, kN)",
            "Utilization Ratio (Vᵤ / φVn_total)"
        ],
        "Value": [
            f"{phiRn_bolt:.2f}",
            f"{phiRn_bearing:.2f}",
            f"{phiVn_plate:.2f}",
            f"{Vn_total:.2f}",
            f"{V_u:.2f}",
            f"{ratio:.2f}"
        ]
    })

    st.markdown("### 🧾 Results Summary")
    st.table(df)

    # --- 6. Pass/Fail Check ---
    if Vn_total >= V_u:
        st.success("✅ Connection design is **adequate** per NSCP / AISC 360.")
    else:
        st.error("❌ Connection design is **not adequate**. Increase tab thickness, bolt size, or number of bolts.")

    # --- 7. References ---
    st.markdown("---")
    st.subheader("📘 NSCP / AISC Reference Formulas")
    st.latex(r"R_n (\text{bolt shear}) = 0.6 F_u A_b")
    st.latex(r"R_n (\text{bearing}) = 2.4 d t F_u")
    st.latex(r"V_n (\text{plate}) = 0.6 F_y A_w")
    st.caption("Based on NSCP 2015 §424 and AISC 360-10 (Shear Tab Connection Design).")
