import streamlit as st
import pandas as pd

def display():
    st.header("🛠️ Structural Steel Tension Member Design (NSCP 2015)")

    st.markdown(r"""
    ### Overview  
    This tool calculates the **design strength of a steel tension member** per NSCP 2015, Section 423 —  
    considering both **gross yielding** and **net fracture** limit states.
    """)

    st.subheader("Input Parameters")

    col1, col2, col3 = st.columns(3)
    with col1:
        fy = st.number_input("Yield Strength Fy (MPa)", value=248.0, key="fy")
    with col2:
        fu = st.number_input("Ultimate Strength Fu (MPa)", value=400.0, key="fu")
    with col3:
        ag = st.number_input("Gross Area Ag (mm²)", value=2000.0, key="ag")
    col4, col5 = st.columns(2)
    with col4:
        an = st.number_input("Net Area An (mm²)", value=1600.0, key="an")
    with col5:
        u = st.number_input("Shear Lag Factor U", value=0.9, key="u")
    col6, col7 = st.columns(2)
    with col6:
        phi = st.number_input("Resistance Factor φ", value=0.9, key="phi")
    with col7:
        applied_tension = st.number_input("Applied Tension Load (kN)", value=200.0, key="t_applied")

    # --- Calculations ---
    # Convert MPa × mm² = N → kN
    phiPn_yield = phi * fy * ag / 1000
    phiPn_fracture = phi * fu * an * u / 1000

    design_strength = min(phiPn_yield, phiPn_fracture)
    governing = "Gross Yielding" if phiPn_yield < phiPn_fracture else "Net Fracture"

    safety_factor = design_strength / applied_tension if applied_tension > 0 else 0
    status = "✅ Safe" if safety_factor >= 1 else "⚠️ NG (Overstressed)"

    # --- Display Results ---
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    data = {
        "Parameter": [
            "Yield Strength Fy (MPa)",
            "Ultimate Strength Fu (MPa)",
            "Gross Area Ag (mm²)",
            "Net Area An (mm²)",
            "Shear Lag Factor U",
            "Resistance Factor φ",
            "Design Strength (Yielding) φPn = φFyAg",
            "Design Strength (Fracture) φPn = φFuAnU",
            "Governing Limit State",
            "Applied Tension Load (kN)",
            "Safety Ratio (φPn / P)",
            "Status"
        ],
        "Value": [
            f"{fy:.2f}",
            f"{fu:.2f}",
            f"{ag:.2f}",
            f"{an:.2f}",
            f"{u:.2f}",
            f"{phi:.2f}",
            f"{phiPn_yield:.2f}",
            f"{phiPn_fracture:.2f}",
            governing,
            f"{applied_tension:.2f}",
            f"{safety_factor:.2f}",
            status
        ]
    }

    st.table(pd.DataFrame(data))

    st.info(f"**Governing Limit State:** {governing}\n\n**Design Strength:** {design_strength:.2f} kN")
