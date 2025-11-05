import streamlit as st
import pandas as pd
from src.calculations.wind.other_calculation import calculate_p_other, calculate_qz, get_Kz

# ----------------------------
# Streamlit display
# ----------------------------
def display():
    st.header("🌬️ Other Wind Loads / Appurtenances (NSCP 2015 §207D)")

    st.markdown("""
    This calculator addresses **wind loads on other structures, appurtenances, components and cladding** as outlined in Section 207D of NSCP 2015.
    """)

    st.markdown("### Input Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        V = st.number_input("Basic Wind Speed V (m/s)", min_value=0.0, value=60.0, step=1.0, key="other_V")
        Kd = st.number_input("Directionality Factor Kd", min_value=0.0, value=0.85, step=0.01, key="other_Kd")
        Kzt = st.number_input("Topographic Factor Kzt", min_value=0.0, value=1.0, step=0.01, key="other_Kzt")

    with col2:
        exposure = st.selectbox("Exposure Category", ["B", "C", "D"], index=1, key="other_exposure")
        I = st.number_input("Importance Factor I", min_value=0.0, value=1.0, step=0.05, key="other_I")
        G = st.number_input("Gust Effect Factor G", min_value=0.0, value=0.85, step=0.01, key="other_G")

    with col3:
        h = st.number_input("Reference Height, h (m)", min_value=0.0, value=10.0, step=0.5, key="other_h")
        A = st.number_input("Projected Area A (m²)", min_value=0.0, value=10.0, step=0.5, key="other_A")
        Cp = st.number_input("External Coefficient Cp", value=1.2, step=0.05, key="other_Cp")

    st.markdown("### Internal Pressure Coefficient / Other Data")
    GCpi = st.number_input("GCpi (Internal or Component-specific)", value=0.18, step=0.01, key="other_GCpi")

    # computation
    Kz = get_Kz(exposure, h)
    qz = calculate_qz(V, Kz, Kzt, Kd, I)
    p_pos, p_neg = calculate_p_other(qz, G, Cp, GCpi)
    F_pos = p_pos * A
    F_neg = p_neg * A

    st.markdown("### 🧾 Summary of Input and Results")

    data = [
        {
            "Parameter": "Exposure Coefficient Kz",
            "Value": round(Kz, 3)
        },
        {
            "Parameter": "Velocity Pressure qz (N/m²)",
            "Value": round(qz, 2)
        },
        {
            "Parameter": "Positive Design Pressure p+ (N/m²)",
            "Value": round(p_pos, 2)
        },
        {
            "Parameter": "Negative Design Pressure p- (N/m²)",
            "Value": round(p_neg, 2)
        },
        {
            "Parameter": "Resultant Force F+ (N)",
            "Value": round(F_pos, 2)
        },
        {
            "Parameter": "Resultant Force F- (N)",
            "Value": round(F_neg, 2)
        },
    ]
    df = pd.DataFrame(data)
    st.dataframe(df.set_index("Parameter"), use_container_width=True, height=300)

    st.markdown("#### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("qz (N/m²)", f"{qz:.2f}")
    with col2:
        st.metric("p+ (N/m²)", f"{p_pos:.2f}")
    with col3:
        st.metric("p- (N/m²)", f"{p_neg:.2f}")

    st.markdown("---")
    st.subheader("📘 NSCP 2015 §207D Reference Formulas")
    st.latex(r"q_z = 0.613 \times K_z \times K_{zt} \times K_d \times V^2 \times I")
    st.latex(r"p = q_z \,(G\, C_p \pm G\, C_{pi})")
    st.latex(r"F = p \times A")

    st.markdown(r"""
    **Where:**
    - \(V\): Basic wind speed (m/s)  
    - \(K_z\): Exposure coefficient  
    - \(K_{zt}\): Topographic factor  
    - \(K_d\): Directionality factor  
    - \(I\): Importance factor  
    - \(G\): Gust effect factor  
    - \(C_p\): External pressure coefficient (component or cladding)  
    - \(G C_{pi}\): Internal/component pressure coefficient  
    - \(A\): Projected area (m²) of the component or cladding  
    """)

    st.markdown("---")
    st.caption("Developed based on NSCP 2015 Section 207D – Other Wind Loads")
