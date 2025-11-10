import streamlit as st
import pandas as pd

def display():
    st.header("🧱 Beam-Column Moment Welded Connection (NSCP 2015)")

    st.markdown(r"""
    This app calculates and checks a **moment-resisting welded beam-column connection**
    based on **NSCP 2015 Section 422**.  
    All calculations are approximate and for educational/reference use only.
    """)

    # --- INPUT SECTION ---
    st.header("🔹 Input Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        Mu = st.number_input("Factored Moment Mu (kN·m)", value=250.0, step=10.0, key="welded_mu")
        Vu = st.number_input("Factored Shear Vu (kN)", value=150.0, step=10.0, key="welded_vu")
        Fy = st.number_input("Yield Strength Fy (MPa)", value=345.0, key="welded_fy")
    with col2:
        Fu = st.number_input("Ultimate Strength Fu (MPa)", value=450.0, key="welded_fu")
        FEXX = st.number_input("Electrode Strength FEXX (MPa)", value=490.0, key="welded_fexx")
        phi = st.number_input("Strength Reduction Factor φ", value=0.75, key="welded_phi")
    with col3:
        d = st.number_input("Beam Depth d (mm)", value=550.0, key="welded_d")
        tf = st.number_input("Flange Thickness tf (mm)", value=25.0, key="welded_tf")
        Lf = st.number_input("Flange Weld Length (mm)", value=200.0, key="welded_lf")

    st.divider()

    # --- CALCULATIONS ---
    Mu_Nmm = Mu * 1e6  # Convert kN·m to N·mm
    T = Mu_Nmm / (d - tf)  # Flange force in N
    tw = T / (2 * phi * 0.707 * Lf * FEXX)  # Required weld throat thickness in mm
    weld_size = tw / 0.707  # Convert throat to weld leg size (mm)
    V_N = Vu * 1e3  # kN to N
    web_weld_shear = V_N / (Lf * 2)  # N/mm (approximate)
    Vp = 0.6 * Fy * (Lf * tf)  # Panel zone nominal shear (simplified)
    Vn = phi * Vp

    # --- SUMMARY TABLE ---
    data = {
        "Step": [
            "1. Factored Moment",
            "2. Flange Force (T)",
            "3. Required Weld Throat Thickness (tw)",
            "4. Equivalent Fillet Weld Size (w)",
            "5. Web Weld Shear per mm",
            "6. Panel Zone Shear Strength (φVn)",
            "7. Check Panel Zone Shear",
        ],
        "Formula / Reference": [
            "Mu = φMn (NSCP 422.3)",
            "T = Mu / (d - tf)",
            "tw = T / (2 × φ × 0.707 × Lf × FEXX)",
            "w = tw / 0.707",
            "V/mm = Vu / (2 × Lf)",
            "φVn = 0.6FyA_pzφ",
            "Vu ≤ φVn ?"
        ],
        "Result": [
            f"{Mu:.2f} kN·m",
            f"{T/1e3:.2f} kN",
            f"{tw:.2f} mm",
            f"{weld_size:.2f} mm",
            f"{web_weld_shear:.2f} N/mm",
            f"{Vn/1e3:.2f} kN",
            "OK" if V_N <= Vn else "NG"
        ]
    }
    
    # -------------------------------------------------
    # RESULTS TABLE
    # -------------------------------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    df = pd.DataFrame(data)
    st.table(df)

    # --- RESULTS ---
    st.divider()
    st.subheader("✅ Design Summary")

    st.markdown(f"""
    - **Flange Force (T):** {T/1e3:.2f} kN  
    - **Required Weld Throat Thickness (tw):** {tw:.2f} mm  
    - **Recommended Fillet Weld Size (w):** {weld_size:.2f} mm  
    - **Web Weld Shear Intensity:** {web_weld_shear:.2f} N/mm  
    - **Panel Zone Shear Strength:** {Vn/1e3:.2f} kN  
    - **Status:** {"🟩 SAFE" if V_N <= Vn else "🟥 NG – Increase weld or flange"}
    """)

    st.divider()
    st.caption("According to NSCP 2015 Section 422 — Structural Steel Connections, Welded Joints, and Moment-Resisting Connections.")
