import streamlit as st
import pandas as pd
from src.calculations.wind.envelope_calculation import calculate_pressure, calculate_qz, get_Kz

def display():
    st.header("🌬️ Envelope Procedure Wind Load (NSCP 2015 Section 207C)")

    st.markdown("""
    This calculator estimates **wind pressures using the Envelope Procedure (NSCP 2015 §207C)**.  
    It’s applicable for **simple-shaped buildings** where detailed directional analysis isn’t required.
    """)

    st.markdown("### Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        V = st.number_input("Basic Wind Speed, V (m/s)", min_value=0.0, value=60.0, step=1.0, key="env_V")
        Kd = st.number_input("Directionality Factor, Kd", min_value=0.0, value=0.85, step=0.01, key="env_Kd")
        Kzt = st.number_input("Topographic Factor, Kzt", min_value=0.0, value=1.0, step=0.01, key="env_Kzt")

    with col2:
        exposure = st.selectbox("Exposure Category", ["B", "C", "D"], index=1, key="env_exposure")
        I = st.number_input("Importance Factor, I", min_value=0.0, value=1.0, step=0.05, key="env_I")
        G = st.number_input("Gust Effect Factor, G", min_value=0.0, value=0.85, step=0.01, key="env_G")

    with col3:
        h = st.number_input("Mean Roof Height, h (m)", min_value=0.0, value=10.0, step=1.0, key="env_h")
        width = st.number_input("Building Width, B (m)", min_value=0.0, value=20.0, step=1.0, key="env_width")
        depth = st.number_input("Building Depth, L (m)", min_value=0.0, value=15.0, step=1.0, key="env_depth")

    st.markdown("### Pressure Coefficients")
    colA, colB, colC = st.columns(3)

    with colA:
        Cp_windward = st.number_input("Cp (Windward Face)", value=0.8, step=0.05, key="env_Cp_windward")
    with colB:
        Cp_leeward = st.number_input("Cp (Leeward Face)", value=-0.5, step=0.05, key="env_Cp_leeward")
    with colC:
        GCpi = st.number_input("GCpi (Internal Pressure Coefficient)", value=0.18, step=0.01, key="env_GCpi")

    # ----------------------------
    # Computation
    # ----------------------------
    Kz = get_Kz(exposure, h)
    qh = calculate_qz(V, Kz, Kzt, Kd, I)

    p_wind_pos, p_wind_neg = calculate_pressure(qh, G, Cp_windward, GCpi)
    p_lee_pos, p_lee_neg = calculate_pressure(qh, G, Cp_leeward, GCpi)

    area_face = h * width
    F_wind_pos = p_wind_pos * area_face
    F_wind_neg = p_wind_neg * area_face
    F_lee_pos = p_lee_pos * area_face
    F_lee_neg = p_lee_neg * area_face

    st.markdown("### 🧾 Summary of Input and Results")

    data = [
        ["Windward Face", round(qh, 2), round(p_wind_pos, 2), round(p_wind_neg, 2),
         round(F_wind_pos, 2), round(F_wind_neg, 2)],
        ["Leeward Face", round(qh, 2), round(p_lee_pos, 2), round(p_lee_neg, 2),
         round(F_lee_pos, 2), round(F_lee_neg, 2)]
    ]
    df = pd.DataFrame(data, columns=["Surface", "qh (N/m²)", "p (+) (N/m²)", "p (−) (N/m²)", "F (+) (N)", "F (−) (N)"])
    st.dataframe(df, use_container_width=True, height=200)

    st.markdown("#### Key Results")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Velocity Pressure (qh)", f"{qh:.2f} N/m²")
    with col2:
        st.metric("Exposure Coefficient (Kz)", f"{Kz:.3f}")
    with col3:
        st.metric("Exposure Category", exposure)

    st.markdown("---")
    st.subheader("📘 NSCP 2015 §207C Formulas")

    st.latex(r"q_h = 0.613 \times K_z \times K_{zt} \times K_d \times V^2 \times I")
    st.latex(r"p = q_h (G C_p \pm G C_{pi})")
    st.latex(r"F = p \times A")

    st.markdown(r"""
    **Where:**
    - \(q_h\): Velocity pressure at mean roof height  
    - \(V\): Basic wind speed (m/s)  
    - \(K_z\): Exposure coefficient (depends on height & terrain)  
    - \(K_{zt}\): Topographic factor  
    - \(K_d\): Directionality factor  
    - \(I\): Importance factor  
    - \(G\): Gust factor  
    - \(C_p\): External pressure coefficient  
    - \(G C_{pi}\): Internal pressure coefficient  
    - \(A\): Projected area of surface (m²)
    """)

    st.caption("Developed based on NSCP 2015 Section 207C – Envelope Procedure for Wind Load Design")
