import streamlit as st
import pandas as pd
import math

def display():
    st.header("🛠️ Structural Steel Beam — NSCP 2015 (flexure & shear checks)")

    st.markdown(r"""
    Quick LRFD-style checks for steel beams following NSCP 2015 Chapter on Structural Steel.
    - Design flexural strength: Φ_b M_n (Φ_b = 0.90 for LRFD)
    - Nominal Mn from plastic/yielding (M_p = F_y · Z_x) — lateral–torsional buckling may control for long unbraced lengths.
    - Shear strength (nominal): V_n ≈ 0.6 F_y A_w (AISC/NSCP consistent).
    **Note:** This tool does NOT perform a full LTB (M_cr) analysis. If Lb (unbraced) is large, provide a reduced Mn or add bracing.
    """)

    st.markdown("### Section / material inputs")

    col1, col2, col3 = st.columns(3)
    with col1:
        section_name = st.text_input("Section name (optional)", value="W250x33", key="ss_section")
        Zx = st.number_input("Plastic section modulus Zx (mm³)", min_value=0.0, value=60000.0, step=100.0, key="ss_Zx")
        Sx = st.number_input("Elastic section modulus Sx (mm³) (optional)", min_value=0.0, value=50000.0, step=100.0, key="ss_Sx")
    with col2:
        Ix = st.number_input("Moment of inertia Ix (mm⁴)", min_value=0.0, value=1.2e7, step=1000.0, key="ss_Ix")
        Aw = st.number_input("Shear area A_w (mm²) (web shear area)", min_value=0.0, value=3000.0, step=10.0, key="ss_Aw")
    with col3:
        Fy = st.number_input("Yield strength F_y (MPa)", min_value=200.0, value=250.0, step=5.0, key="ss_Fy")
        E = st.number_input("Elastic modulus E (MPa)", min_value=100000.0, value=200000.0, step=1000.0, key="ss_E")
        Lb = st.number_input("Unbraced length L_b (mm)", min_value=0.0, value=3000.0, step=100.0, key="ss_Lb")

    st.markdown("---")
    st.markdown("### Applied actions (factored)")

    col4, col5 = st.columns(2)
    with col4:
        Mu = st.number_input("Applied design moment M_u (kN·m)", min_value=0.0, value=50.0, step=1.0, key="ss_Mu")
    with col5:
        Vu = st.number_input("Applied design shear V_u (kN)", min_value=0.0, value=60.0, step=1.0, key="ss_Vu")

    st.markdown("---")
    # ----------------------------
    # Calculations
    # ----------------------------
    # Plastic moment Mp (N·mm) = F_y (N/mm²) * Zx (mm³)
    Mp_Nmm = Fy * 1e6 / 1e6 * Zx  # Fy in N/mm2 times Zx mm3 -> N·mm  (kept simple)
    # (The expression above is algebraically Mp_Nmm = Fy (N/mm2) * Zx (mm3) -> N·mm)
    # Convert to kN·m:
    Mp_kNm = Mp_Nmm / 1e6

    # Nominal Mn (basic yielding/plastic) (kN·m)
    Mn_yield_kNm = Mp_kNm

    # LRFD phi for flexure (NSCP LRFD) — use 0.90
    phi_b = 0.90
    design_flex_capacity_kNm = phi_b * Mn_yield_kNm

    # Shear nominal capacity: Vn = 0.6 * Fy * Aw  (N)
    Vn_N = 0.6 * Fy * Aw  # N (since Fy in N/mm2, Aw in mm2 -> N)
    Vn_kN = Vn_N / 1000.0
    # Adopt phi for shear conservatively = 0.90 (LRFD flexure/shear grouping)
    phi_v = 0.90
    design_shear_capacity_kN = phi_v * Vn_kN

    # Lateral-torsional buckling note:
    # NSCP (AISC-style) requires LTB check. This helper does NOT calculate M_cr.
    # We'll warn if unbraced length Lb exceeds a typical compact-section threshold.
    Lb_mm = Lb
    # conservative heuristic threshold: if Lb > 3000 mm, warn user LTB may govern
    ltb_warning = Lb_mm > 3000.0

    # Basic utilization ratios
    util_flex = Mu / design_flex_capacity_kNm if design_flex_capacity_kNm > 0 else float("inf")
    util_shear = Vu / design_shear_capacity_kN if design_shear_capacity_kN > 0 else float("inf")

    # ----------------------------
    # Output (stringified to avoid dtype issues)
    # ----------------------------
    results = {
        "Parameter": [
            "Section",
            "Zx (mm³)",
            "Sx (mm³)",
            "Mp (kN·m)",
            "Nominal Mn (kN·m) [yield-based]",
            "Φ_b (flexure, LRFD)",
            "Design flexural capacity ΦMn (kN·m)",
            "Shear area A_w (mm²)",
            "Nominal shear Vn (kN) (≈0.6 Fy Aw)",
            "Design shear capacity ΦVn (kN)",
            "Unbraced length Lb (mm)",
            "Applied M_u (kN·m)",
            "Applied V_u (kN)",
            "Flexure utilization (Mu / ΦMn)",
            "Shear utilization (Vu / ΦVn)"
        ],
        "Value": [
            str(section_name),
            f"{Zx:,.0f}",
            f"{Sx:,.0f}",
            f"{Mp_kNm:.3f}",
            f"{Mn_yield_kNm:.3f}",
            f"{phi_b:.2f}",
            f"{design_flex_capacity_kNm:.3f}",
            f"{Aw:,.0f}",
            f"{Vn_kN:.3f}",
            f"{design_shear_capacity_kN:.3f}",
            f"{Lb_mm:.0f}",
            f"{Mu:.3f}",
            f"{Vu:.3f}",
            f"{util_flex:.3f}",
            f"{util_shear:.3f}"
        ]
    }

    st.markdown("### 🧾 Results summary")
    st.table(pd.DataFrame(results).set_index("Parameter"))

    # Pass/fail messaging
    st.markdown("### Checks")
    if util_flex <= 1.0:
        st.success(f"Flexure OK — Mu = {Mu:.2f} kN·m ≤ ΦMn = {design_flex_capacity_kNm:.2f} kN·m")
    else:
        st.error(f"Flexure FAIL — Mu = {Mu:.2f} kN·m > ΦMn = {design_flex_capacity_kNm:.2f} kN·m")

    if util_shear <= 1.0:
        st.success(f"Shear OK — Vu = {Vu:.2f} kN ≤ ΦVn = {design_shear_capacity_kN:.2f} kN")
    else:
        st.error(f"Shear FAIL — Vu = {Vu:.2f} kN > ΦVn = {design_shear_capacity_kN:.2f} kN")

    if ltb_warning:
        st.warning("Unbraced length Lb is large — lateral–torsional buckling (LTB) may govern. Perform LTB (M_cr) check per NSCP/AISC or add lateral bracing.")
    else:
        st.info("Unbraced length looks moderate; still confirm LTB per code if Lb is near limiting values.")

    st.markdown("---")
    st.markdown("### Notes & references")
    st.markdown(r"""
    - NSCP/LRFD uses: \(\Phi_b = 0.90\) for flexure (LRFD). Nominal Mn may be the lower of yielding/plastic moment and LTB-limited resistance. :contentReference[oaicite:3]{index=3}  
    - Plastic moment (approx): \(M_p = F_y \, Z_x\). Use tabulated Zx for steel shapes (units: N·mm → convert to kN·m). :contentReference[oaicite:4]{index=4}  
    - Shear nominal strength commonly approximated by \(V_n \approx 0.6 F_y A_w\) (AISC/NSCP-compatible). Confirm with NSCP shear clauses and section compactness checks. :contentReference[oaicite:5]{index=5}
    - This helper **does not** compute lateral–torsional buckling capacity (M_cr) — for long unbraced lengths, compute M_cr (or use NSCP/AISC procedures) and take ΦMn = Φ·min(M_p, M_LTB).
    """)