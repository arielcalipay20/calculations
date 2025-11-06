import streamlit as st
import math
import pandas as pd

def display():
    st.header("🧱 RC Isolated Footing Design (NSCP 2015 — Section 418)")

    st.subheader("Input Parameters")

    # Geometry
    col1, col2, col3 = st.columns(3)
    with col1:
        column_load = st.number_input("Column Load (kN)", min_value=0.0, value=1000.0, step=10.0, key="column_load")
    with col2:
        footing_width = st.number_input("Footing Width, B (m)", min_value=0.0, value=2.0, step=0.1, key="footing_width")
    with col3:
        footing_length = st.number_input("Footing Length, L (m)", min_value=0.0, value=2.0, step=0.1, key="footing_length")

    # Soil and Material Properties
    col4, col5, col6 = st.columns(3)
    with col4:
        allowable_soil_pressure = st.number_input("Allowable Soil Bearing Capacity (kN/m²)", min_value=0.0, value=200.0, step=5.0, key="soil_bearing")
    with col5:
        fck = st.number_input("Concrete Strength f'c (MPa)", min_value=0.0, value=28.0, step=1.0, key="fck")
    with col6:
        fy = st.number_input("Steel Yield Strength fy (MPa)", min_value=0.0, value=415.0, step=5.0, key="fy")

    # Column Dimensions
    col7, col8 = st.columns(2)
    with col7:
        column_width = st.number_input("Column Width (m)", min_value=0.0, value=0.4, step=0.05, key="col_w")
    with col8:
        column_length = st.number_input("Column Length (m)", min_value=0.0, value=0.4, step=0.05, key="footing_col_l")

    st.subheader("Design Calculation")

    # Factored load (1.5 DL + 1.5 LL)
    Pu = 1.5 * column_load

    # Area of footing
    A_footing = footing_width * footing_length

    # Net bearing pressure
    qnet = Pu / A_footing

    # Check bearing pressure
    bearing_ok = qnet <= allowable_soil_pressure

    # Effective depth (initial assumption)
    d = 0.45 * footing_width

    # Moment about short direction
    Mx = qnet * footing_length * (footing_length - column_length) / 8

    # Reinforcement design (Mu = φMn)
    phi = 0.9
    Mu = Mx / phi
    As_req = (Mu * 10**6) / (0.87 * fy * (d * 1000 - 0.42 * (Mu * 10**6 / (0.87 * fy * d * 1000)) / (footing_width * 1000)))
    As_req = max(As_req, 0)

    # Minimum reinforcement (NSCP 418.3.1)
    As_min = 0.0018 * footing_width * d * 1000
    As_provided = max(As_req, As_min)

    # Punching shear check
    perimeter = 2 * (column_width + column_length) * 1000
    Vu = (qnet * (footing_width * footing_length - column_width * column_length)) * 1000
    v_actual = Vu / (perimeter * d * 1000)
    v_allow = 0.17 * math.sqrt(fck)  # MPa

    punching_ok = v_actual <= v_allow

    # Summary Table
    results = {
        "Parameter": [
            "Factored Load Pu (kN)",
            "Net Bearing Pressure (kN/m²)",
            "Bearing Pressure Check",
            "Effective Depth, d (m)",
            "Factored Moment (kN·m)",
            "Required Steel Area, As (mm²)",
            "Minimum Steel Area, As_min (mm²)",
            "Provided Steel Area, As_provided (mm²)",
            "Punching Shear Stress (MPa)",
            "Allowable Shear Stress (MPa)",
            "Punching Shear Check"
        ],
        "Value": [
            f"{Pu:.2f}",
            f"{qnet:.2f}",
            "OK ✅" if bearing_ok else "NG ❌",
            f"{d:.3f}",
            f"{Mx:.2f}",
            f"{As_req:.2f}",
            f"{As_min:.2f}",
            f"{As_provided:.2f}",
            f"{v_actual:.3f}",
            f"{v_allow:.3f}",
            "OK ✅" if punching_ok else "NG ❌"
        ]
    }

    st.table(pd.DataFrame(results))

    if not bearing_ok:
        st.warning("⚠️ Increase footing area to reduce bearing pressure.")
    if not punching_ok:
        st.warning("⚠️ Increase footing thickness or add shear reinforcement.")

