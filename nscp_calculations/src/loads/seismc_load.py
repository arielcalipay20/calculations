import streamlit as st
import pandas as pd
from src.calculations.seismic.seismic_calculation import get_seismic_coefficients, vertical_distribution

# ----------------------------
# Streamlit Display Function
# ----------------------------
def display():
    st.header("📐 Seismic Load Calculation (NSCP 2015 §208)")

    st.markdown("""
    Use the **static lateral-force procedure** for seismic loads as per NSCP 2015 Section 208.  
    Adjust the inputs and see the base shear and floor forces computed automatically.
    """)

    st.markdown("### Input Parameters")

    col1, col2, col3 = st.columns(3)
    with col1:
        Z = st.number_input("Seismic Zone Factor, Z", min_value=0.0, value=0.4, step=0.05, key="seq_z")
        Na = st.number_input("Near-Source Factor, Nₐ", min_value=0.0, value=1.0, step=0.05, key="seq_na")
        Nv = st.number_input("Near-Source Factor, Nᵥ", min_value=0.0, value=1.0, step=0.05, key="seq_nv")
        Ca = st.number_input("Seismic Response Coefficient, Cₐ", min_value=0.0, value=0.44, step=0.01, key="seq_ca")

    with col2:
        Cv = st.number_input("Seismic Response Coefficient, Cᵥ", min_value=0.0, value=0.64, step=0.01, key="seq_cv")
        I = st.number_input("Importance Factor, I", min_value=0.5, value=1.0, step=0.1, key="seq_i")
        R = st.number_input("Response Modification Factor, R", min_value=1.0, value=6.0, step=0.5, key="seq_r")

    with col3:
        W = st.number_input("Total Seismic Weight, W (kN)", min_value=0.0, value=10000.0, step=100.0, key="seq_w")
        T = st.number_input("Fundamental Period, T (s)", min_value=0.0, value=0.5, step=0.1, key="seq_t")

    st.markdown("---")
    st.markdown("### Floor Data (Wᵢ & hᵢ)")

    num_floors = st.slider("Number of Floors", 1, 20, 3, key="seq_numfloors")
    floors = []
    for i in range(num_floors):
        w_i = st.number_input(f"Floor {i+1} Weight Wᵢ (kN)", min_value=0.0, value=3000.0, step=100.0, key=f"seq_wf_{i}")
        h_i = st.number_input(f"Floor {i+1} Height hᵢ (m)", min_value=0.0, value=float((i+1)*3.0), step=0.5, key=f"seq_hf_{i}")
        floors.append((w_i, h_i))

    W_list = [w for w, _ in floors]
    h_list = [h for _, h in floors]

    # --- Computation ---
    V_design = get_seismic_coefficients(Z, Na, Nv, Ca, Cv, I, R, W, T)
    floor_forces = vertical_distribution(V_design, W_list, h_list)

    # --- Display Results ---
    st.markdown("### 🧾 Summary of Input and Results")

    st.metric("Design Base Shear, V (kN)", f"{V_design:.2f}")

    data = []
    for idx, (w_i, h_i) in enumerate(floors):
        data.append({
            "Floor": f"{idx+1}",
            "Wᵢ (kN)": round(w_i, 2),
            "hᵢ (m)": round(h_i, 2),
            "Fᵢ (kN)": round(floor_forces[idx], 2)
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=300)

    st.markdown("---")
    st.subheader("📘 NSCP 2015 §208-Key Formulas")
    st.latex(r"V = \min\left( \frac{C_v\,I}{R} \; W \;,\; 2.5\,C_a\,I\,W \right)")
    st.latex(r"F_i = V \times \frac{W_i\,h_i}{\sum_{j} W_j\,h_j}")

    st.markdown(r"""
    **Where:**  
    - \(Z\): Seismic zone factor  
    - \(N_a\), \(N_v\): Near-source factors  
    - \(C_a\), \(C_v\): Seismic response coefficients  
    - \(I\): Importance factor  
    - \(R\): Response modification factor  
    - \(W\): Total seismic weight of structure  
    - \(T\): Fundamental period of the structure  
    - \(W_i\): Weight at floor i  
    - \(h_i\): Height of floor i above base  
    """)

    st.markdown("---")
    st.caption("Based on NSCP 2015 §208 Earthquake Loads — use actual code tables for final design.")