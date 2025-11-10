import streamlit as st
from src.calculations.simple_maths import multiply, divide

# --- NSCP Reference Unit Weights (approximate typical values) ---
NSCP_UNIT_WEIGHTS = {
    "Reinforced Concrete": 24.0,     # kN/m³
    "Plain Concrete": 23.5,
    "Structural Steel": 77.0,
    "Brickwork": 19.0,
    "Concrete Hollow Block (CHB)": 12.0,
    "Plaster Finish": 20.0,
    "Timber/Wood": 7.0,
    "Roofing Sheet (GI/Aluminum)": 0.10,
    "Floor Finish (Tiles)": 22.0,
    "Ceiling (Gypsum Board)": 8.0,
}

def display():
    st.header("🧱 Dead Load Calculator (Based on NSCP)")
    st.markdown("""
    This calculator estimates **dead loads** in accordance with the *National Structural Code of the Philippines (NSCP)*.
    It computes the surface load in **kN/m²** and total load in **kN** for the given area and material properties.
    """)

    # --- INPUTS ---
    st.subheader("Input Parameters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        material = st.selectbox("Material", list(NSCP_UNIT_WEIGHTS.keys()))

    with col2:
        thickness_mm = st.number_input("Thickness (mm)", min_value=0.0, step=10.0, value=150.0)

    with col3:
        area = st.number_input("Area (m²)", min_value=0.0, step=1.0, value=10.0)

    with col4:
        # auto-filled from NSCP data but user can override
        unit_weight = st.number_input(
            "Unit Weight (kN/m³)",
            min_value=0.0,
            step=0.1,
            value=NSCP_UNIT_WEIGHTS[material],
        )

    st.divider()

    # --- CALCULATION ---
    thickness_m = divide(thickness_mm, 1000)  # convert to meters
    dead_load_surface = multiply(unit_weight, thickness_m)  # kN/m²
    total_dead_load = multiply(dead_load_surface, area)  # kN

    st.subheader("Calculation Results")

    st.write(f"**Dead Load (kN/m²):** {dead_load_surface:.3f}")
    st.write(f"**Total Dead Load (kN):** {total_dead_load:.3f}")

    # --- FORMULA DISPLAY ---
    with st.expander("📘 Show Calculation Formula"):
        st.latex(r"q_d = \gamma \times t")
        st.latex(r"Q_d = q_d \times A")
        st.markdown(r"""
        Where:  
        - \( q_d \) = Dead load per unit area (kN/m²)  
        - \( \gamma \) = Unit weight of material (kN/m³)  
        - \( t \) = Thickness of material (m)  
        - \( A \) = Area (m²)  
        - \( Q_d \) = Total dead load (kN)
        """)

    # --- SUMMARY TABLE ---
    st.divider()
    st.markdown("### 🧾 Summary of Input and Results")

    st.table({
        "Parameter": ["Material", "Thickness (m)", "Unit Weight (kN/m³)", "Area (m²)", "Dead Load (kN/m²)", "Total Load (kN)"],
        "Value": [material, f"{thickness_m:.3f}", f"{unit_weight:.2f}", f"{area:.2f}", f"{dead_load_surface:.3f}", f"{total_dead_load:.3f}"]
    })