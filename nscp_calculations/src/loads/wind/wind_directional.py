import streamlit as st
import pandas as pd
from src.calculations.simple_maths import multiply
from src.calculations.wind.directional_calculation import get_Kz

def display():
    st.header("🌬️ Directional Procedure Wind Load (NSCP 2015 Section 207B)")
    st.markdown("""
    This calculator follows **NSCP 2015 Section 207B (Directional Procedure)**  
    for computing wind pressures on structures.  
    Modify any input and results update automatically.
    """)

    # ----------------------------
    # Input Parameters
    # ----------------------------
    st.markdown("### Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        V = st.number_input("Basic Wind Speed, V (m/s)", min_value=0.0, value=60.0, step=1.0)
        Kd = st.number_input("Directionality Factor, Kd", min_value=0.0, value=0.85, step=0.01)
        Kzt = st.number_input("Topographic Factor, Kzt", min_value=0.0, value=1.0, step=0.01)

    with col2:
        exposure = st.selectbox("Exposure Category", ["B", "C", "D"], index=1)
        G = st.number_input("Gust Effect Factor, G", min_value=0.0, value=0.85, step=0.01)
        Cp = st.number_input("External Pressure Coefficient, Cp", value=0.8, step=0.05)

    with col3:
        GCpi = st.number_input("Internal Pressure Coefficient, GCpi", value=0.18, step=0.01)
        area = st.number_input("Tributary Area, A (m²)", min_value=0.0, value=20.0, step=1.0)
        I = st.number_input("Importance Factor, I", min_value=0.0, value=1.0, step=0.05)

    # ----------------------------
    # Heights Input and Kz
    # ----------------------------
    st.markdown("### Heights for Evaluation")
    num_heights = st.slider("Number of Heights", 1, 10, 3)
    heights = []
    Kz_values = []

    st.info("Kz values are automatically computed based on Exposure Category and height, but can be manually adjusted.")

    for i in range(num_heights):
        cols = st.columns(2)
        with cols[0]:
            z = st.number_input(f"Height z{i+1} (m)", min_value=0.0, value=float((i + 1) * 5), step=0.5, key=f"h{i}")
        with cols[1]:
            auto_kz = get_Kz(exposure, z)
            kz = st.number_input(f"Kz @ z{i+1}", min_value=0.0, value=auto_kz, step=0.01, key=f"kz{i}")
        heights.append(z)
        Kz_values.append(kz)

    # ----------------------------
    # Computation (Dynamic)
    # ----------------------------
    data = []
    for z, Kz in zip(heights, Kz_values):
        # Velocity Pressure (NSCP Eq. 207B)
        qz = 0.613 * Kz * Kzt * Kd * (V ** 2) * I
        # Positive and negative design pressures
        p_pos = qz * (G * Cp - GCpi)
        p_neg = qz * (G * Cp + GCpi)
        # Forces
        F_pos = multiply(p_pos, area)
        F_neg = multiply(p_neg, area)
        data.append({
            "Height (m)": z,
            "Kz": round(Kz, 3),
            "qz (N/m²)": round(qz, 2),
            "p (+) (N/m²)": round(p_pos, 2),
            "p (−) (N/m²)": round(p_neg, 2),
            "F (+) (N)": round(F_pos, 2),
            "F (−) (N)": round(F_neg, 2)
        })

    df = pd.DataFrame(data)

    # ----------------------------
    # Output Display
    # ----------------------------
    st.markdown("### 🧾 Summary of Input and Results")

    st.dataframe(df, height=300)

    # Highlight average summary
    st.markdown("#### Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Velocity Pressure (qz)", f"{df['qz (N/m²)'].mean():.2f}")
    with col2:
        st.metric("Average Positive Pressure (p+)", f"{df['p (+) (N/m²)'].mean():.2f}")
    with col3:
        st.metric("Average Negative Pressure (p−)", f"{df['p (−) (N/m²)'].mean():.2f}")

    # ----------------------------
    # Reference and Notes
    # ----------------------------
    st.markdown("---")
    st.subheader("📘 NSCP 2015 §207B Formulas")
    st.latex(r"q_z = 0.613 \times K_z \times K_{zt} \times K_d \times V^2 \times I")
    st.latex(r"p = q_z (G C_p \pm G C_{pi})")
    st.latex(r"F = p \times A")

    st.markdown(r"""
    **Where:**
    - \(V\): Basic wind speed (m/s)  
    - \(K_z\): Exposure coefficient (depends on exposure & height)  
    - \(K_{zt}\): Topographic factor  
    - \(K_d\): Directionality factor  
    - \(I\): Importance factor  
    - \(G\): Gust effect factor  
    - \(C_p, G C_{pi}\): External & internal pressure coefficients  
    - \(A\): Tributary area (m²)  
    """)

    st.markdown("---")
    st.caption("Developed based on NSCP 2015, Section 207B – Directional Procedure for Wind Load Design")

