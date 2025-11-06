import streamlit as st
import pandas as pd

def display():
    st.header("Reinforced Concrete Wall Design (NSCP Section 418)")

    st.markdown("### Input Parameters")

    # Geometry
    col1, col2, col3 = st.columns(3)
    with col1:
        wall_height = st.number_input("Wall Height (m)", min_value=1.0, step=0.1, value=3.0, key="wall_height")
    with col2:
        wall_length = st.number_input("Wall Length (m)", min_value=1.0, step=0.1, value=4.0, key="wall_length")
    with col3:
        wall_thickness = st.number_input("Wall Thickness (mm)", min_value=100.0, step=25.0, value=200.0, key="wall_thickness")

    # Material strengths
    col4, col5 = st.columns(2)
    with col4:
        fc = st.number_input("Concrete Strength f'c (MPa)", min_value=17.0, step=1.0, value=21.0, key="fc")
    with col5:
        fy = st.number_input("Steel Yield Strength fy (MPa)", min_value=275.0, step=10.0, value=415.0, key="walls_fy")

    # Loads
    col6, col7 = st.columns(2)
    with col6:
        Pu = st.number_input("Factored Axial Load, Pu (kN)", min_value=0.0, step=10.0, value=400.0, key="pu")
    with col7:
        Mu = st.number_input("Factored Moment, Mu (kN·m)", min_value=0.0, step=1.0, value=50.0, key="mu")

    st.markdown("---")
    st.markdown("### Calculations")

    # Convert units
    t = wall_thickness / 1000  # mm to m
    b = wall_length
    d = t - 0.05  # effective depth (approx.)
    phi = 0.65  # strength reduction factor (compression-controlled)

    # Nominal axial capacity (simplified)
    Pn0 = 0.85 * fc * 1000 * b * t  # in kN
    phiPn0 = phi * Pn0

    # Slenderness check (NSCP 418.6.2)
    slenderness_ratio = wall_height / t
    slenderness_ok = slenderness_ratio <= 25

    # Required reinforcement (simplified)
    Mu_Nmm = Mu * 1e6
    jd = 0.9 * d
    As_req = Mu_Nmm / (fy * jd * 1e6)
    rho = As_req / (b * t)

    st.markdown(f"**Slenderness Ratio (h/t):** {slenderness_ratio:.2f}")
    if slenderness_ok:
        st.success("✓ Wall is non-slender (OK per NSCP 418.6.2)")
    else:
        st.warning("⚠ Wall is slender — secondary effects must be considered (NSCP 418.6.2)")

    st.markdown("---")
    st.markdown("### 🧾 Results Summary")

    table = pd.DataFrame({
        "Parameter": [
            "Wall Height (m)",
            "Wall Length (m)",
            "Wall Thickness (mm)",
            "Concrete Strength f'c (MPa)",
            "Steel Yield Strength fy (MPa)",
            "Factored Axial Load Pu (kN)",
            "Factored Moment Mu (kN·m)",
            "Nominal Axial Capacity Pn0 (kN)",
            "Design Strength φPn (kN)",
            "Slenderness Ratio (h/t)",
            "Required Steel Ratio ρ"
        ],
        "Value": [
            f"{wall_height:.2f}",
            f"{wall_length:.2f}",
            f"{wall_thickness:.0f}",
            f"{fc:.1f}",
            f"{fy:.1f}",
            f"{Pu:.2f}",
            f"{Mu:.2f}",
            f"{Pn0:.2f}",
            f"{phiPn0:.2f}",
            f"{slenderness_ratio:.2f}",
            f"{rho*100:.3f}%"
        ]
    })

    st.table(table.set_index("Parameter"))

    if not slenderness_ok:
        st.warning("Wall exceeds slenderness limit — consider second-order effects (NSCP 418.6.2).")
