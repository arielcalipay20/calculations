import streamlit as st
from src.calculations.simple_maths import multiply

# --- NSCP Reference Live Loads (Typical Values) ---
# NSCP Table 205-1 (2015 Edition) / Table 205-1 (2020 Edition)
NSCP_LIVE_LOADS = {
    "Residential (Private dwellings)": 1.92,
    "Office Building (General)": 2.40,
    "School Classrooms": 3.00,
    "Corridors, Lobbies, Stairs": 4.80,
    "Library Reading Rooms": 4.80,
    "Library Stack Rooms": 7.20,
    "Hospitals (Wards)": 2.40,
    "Hospitals (Operating Rooms)": 4.80,
    "Assembly Area (Fixed Seats)": 4.80,
    "Assembly Area (Movable Seats)": 7.20,
    "Gymnasium Floor": 4.80,
    "Light Storage": 2.40,
    "Heavy Storage": 7.20,
    "Mechanical Equipment Room": 7.20,
    "Roof (Ordinary, Accessible)": 0.96,
    "Roof (Ordinary, Inaccessible)": 0.57,
    "Roof Garden / Assembly": 4.80,
    "Balcony": 4.80,
    "Sidewalk": 5.00,
    "Garage / Driveway": 2.50,
}

def display():
    st.header("🏗️ Live Load Calculator (Based on NSCP)")
    
    st.markdown("""
    This calculator estimates **live loads** in accordance with the 
    *National Structural Code of the Philippines (NSCP)* — Section 205: Minimum Uniformly Distributed Live Loads.
    It computes the **surface load** and **total load** for the selected occupancy or use type.
    """)

    # --- INPUT PARAMETERS ---
    st.subheader("Input Parameters")

    col1, col2 = st.columns(2)

    with col1:
        occupancy_type = st.selectbox("Occupancy / Use", list(NSCP_LIVE_LOADS.keys()))
        area = st.number_input("Floor Area (m²)", min_value=0.0, step=1.0, value=50.0)

    with col2:
        live_load_value = st.number_input(
            "Live Load (kN/m²)",
            min_value=0.0,
            step=0.1,
            value=NSCP_LIVE_LOADS[occupancy_type],
            help="Default based on NSCP 205-1; you can override if needed."
        )

    st.divider()

    # --- CALCULATION ---
    total_live_load = multiply(live_load_value, area)  # kN

    st.subheader("Calculation Results")

    st.write(f"**Live Load (kN/m²):** {live_load_value:.2f}")
    st.write(f"**Total Live Load (kN):** {total_live_load:.2f}")

    # --- FORMULA ---
    with st.expander("📘 Show Calculation Formula"):
        st.latex(r"q_L = L")
        st.latex(r"Q_L = q_L \times A")
        st.markdown(r"""
        Where:  
        - \( q_L \) = Live load per unit area (kN/m²)  
        - \( L \) = Design live load intensity from NSCP Table 205-1  
        - \( A \) = Tributary area (m²)  
        - \( Q_L \) = Total live load (kN)
        """)

    # --- SUMMARY TABLE ---
    st.divider()
    st.markdown("### 🧾 Summary of Input and Results")

    st.table({
        "Parameter": ["Occupancy / Use", "Area (m²)", "Live Load (kN/m²)", "Total Load (kN)"],
        "Value": [occupancy_type, f"{area:.2f}", f"{live_load_value:.2f}", f"{total_live_load:.2f}"]
    })

    # --- REFERENCES ---
    with st.expander("📚 NSCP Reference"):
        st.markdown("""
        **Source:**  
        *National Structural Code of the Philippines (NSCP 2015 / 2020)*  
        **Table 205-1 — Minimum Uniformly Distributed Live Loads.**  
        These values are for guidance only. The structural engineer must verify load values based on occupancy and design category.
        """)