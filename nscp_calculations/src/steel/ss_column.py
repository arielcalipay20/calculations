import streamlit as st
import pandas as pd
import math

def display():
    st.header("🏗️ Structural Steel Column — NSCP 2015 (Axial & Combined Checks)")

    st.markdown(r"""
    Quick LRFD-style check for steel columns per NSCP 2015 (Section 223 → AISC 360).
    - **Axial compression:** φ·P<sub>n</sub> = φ·F<sub>cr</sub>·A<sub>g</sub>  
    - **Flexure + Axial:** simplified interaction check  
      \( \dfrac{P_u}{\phi P_n} + \dfrac{M_u}{\phi M_n} \le 1.0 \)
    """)

    st.header("Section / Material Inputs")
    c1, c2, c3 = st.columns(3)
    with c1:
        section = st.text_input("Section name (optional)", "W250x33", key="col_section")
        Ag = st.number_input("Gross area A_g (mm²)", 0.0, 100000.0, 4200.0, 10.0, key="col_Ag")
        r_x = st.number_input("Radius of gyration r_x (mm)", 0.0, 500.0, 70.0, 1.0, key="col_rx")
    with c2:
        r_y = st.number_input("Radius of gyration r_y (mm)", 0.0, 500.0, 40.0, 1.0, key="col_ry")
        Fy = st.number_input("Yield strength F_y (MPa)", 200.0, 600.0, 250.0, 5.0, key="col_Fy")
        E = st.number_input("Elastic modulus E (MPa)", 100000.0, 220000.0, 200000.0, 1000.0, key="col_E")
    with c3:
        Kx = st.number_input("Effective length factor Kx", 0.1, 3.0, 1.0, 0.05, key="col_Kx")
        Ky = st.number_input("Effective length factor Ky", 0.1, 3.0, 1.0, 0.05, key="col_Ky")
        L = st.number_input("Unbraced length L (mm)", 0.0, 12000.0, 3000.0, 100.0, key="col_L")

    st.header("Applied Loads")
    c4, c5 = st.columns(2)
    with c4:
        Pu = st.number_input("Factored axial load P_u (kN)", 0.0, 5000.0, 900.0, 10.0, key="col_Pu")
    with c5:
        Mu = st.number_input("Factored moment M_u (kN·m)", 0.0, 1000.0, 60.0, 1.0, key="col_Mu")

    # --- Calculations ---
    # slenderness ratios
    KLx = Kx * L
    KLy = Ky * L
    slender_x = KLx / r_x
    slender_y = KLy / r_y
    slender = max(slender_x, slender_y)

    # Euler elastic buckling stress Fe (MPa)
    Fe = (math.pi ** 2 * E) / (slender ** 2)

    # critical stress Fcr (MPa)
    Fy_val = Fy
    if (Fy_val / Fe) <= 2.25:
        Fcr = (0.658 ** (Fy_val / Fe)) * Fy_val
    else:
        Fcr = 0.877 * Fe

    # nominal and design axial capacities
    Pn_N = Fcr * Ag            # N
    phi_c = 0.85
    phiPn_kN = phi_c * Pn_N / 1000.0

    # design flexural capacity (reuse beam phiMn)
    Zx = st.number_input("Plastic modulus Zx (mm³)", 0.0, 1e6, 60000.0, 100.0, key="col_Zx")
    phi_b = 0.90
    phiMn_kNm = phi_b * (Fy_val * Zx / 1e6)   # kN·m

    # interaction check
    ratio_axial = Pu / phiPn_kN if phiPn_kN > 0 else float("inf")
    ratio_flex  = Mu / phiMn_kNm if phiMn_kNm > 0 else float("inf")
    interaction = ratio_axial + ratio_flex

    # --- Results table ---
    data = {
        "Parameter": [
            "Section", "A_g (mm²)", "r_x (mm)", "r_y (mm)",
            "Kx·L/r_x", "Ky·L/r_y", "Critical Fe (MPa)", "F_cr (MPa)",
            "φ_c", "φP_n (kN)", "Φ_bM_n (kN·m)",
            "P_u (kN)", "M_u (kN·m)",
            "P_u/ΦP_n", "M_u/ΦM_n", "Interaction Σ"
        ],
        "Value": [
            section, f"{Ag:,.0f}", f"{r_x:.1f}", f"{r_y:.1f}",
            f"{slender_x:.1f}", f"{slender_y:.1f}", f"{Fe:.2f}", f"{Fcr:.2f}",
            f"{phi_c:.2f}", f"{phiPn_kN:.2f}", f"{phiMn_kNm:.2f}",
            f"{Pu:.2f}", f"{Mu:.2f}",
            f"{ratio_axial:.3f}", f"{ratio_flex:.3f}", f"{interaction:.3f}"
        ]
    }
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    st.table(pd.DataFrame(data).set_index("Parameter"))

    # --- Checks ---
    if ratio_axial <= 1.0:
        st.success(f"Axial OK (Pu {Pu:.1f} ≤ φPn {phiPn_kN:.1f} kN)")
    else:
        st.error(f"Axial FAIL (Pu {Pu:.1f} > φPn {phiPn_kN:.1f} kN)")

    if interaction <= 1.0:
        st.success(f"Combined OK → Σ = {interaction:.3f} ≤ 1.0")
    else:
        st.error(f"Combined FAIL → Σ = {interaction:.3f} > 1.0")

    st.info(f"Slenderness max (KL/r) = {slender:.1f}. Check NSCP λ limits (usually ≤ 200).")

    st.markdown("---")
    st.markdown(r"""
    **Reference notes**  
    - NSCP 2015 Sec. 223 → AISC 360 Chap. E for compression.  
      \( F_{cr} = 0.658^{F_y/F_e} F_y \) if \( F_y/F_e ≤ 2.25 \), else \( 0.877 F_e \).  
    - \( φ_c = 0.85 \) for compression, \( φ_b = 0.90 \) for flexure (LRFD).  
    - Interaction eqn: \( P_u/(φP_n) + M_u/(φM_n) ≤ 1.0 \) (simple case).  
    - Units: mm, MPa, kN, kN·m.
    """)