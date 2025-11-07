import streamlit as st
import pandas as pd
import math

def display():
    st.header("🧱 Strength Design — Masonry (NSCP-style — simplified checks)")

    st.markdown(r"""
    This module provides **preliminary strength checks** for masonry walls/columns:
    - approximate **axial capacity** (φP_n),
    - **slenderness** (KL/r),
    - a conservative estimate of **flexural capacity** (φM_n),
    - a simple **axial+moment interaction** check.

    **Important:** this is a design *aid* only. The calculations below are simplified approximations.
    For final design use the NSCP 2015 masonry provisions, prism test values, relevant tables, and a licensed engineer.
    """)

    st.markdown("### Input parameters")

    col1, col2, col3 = st.columns(3)
    with col1:
        wall_length = st.number_input("Loaded wall length / width (m) — along load (L)", min_value=0.1, value=1.0, step=0.1, key="ms_length")
        wall_height = st.number_input("Wall height (m) (h)", min_value=0.1, value=3.0, step=0.1, key="ms_height")
        thickness = st.number_input("Wall thickness (mm) (t)", min_value=50.0, value=150.0, step=5.0, key="ms_thickness")
    with col2:
        fm = st.number_input("Masonry prism strength f_m (MPa) — use tested or tabulated", min_value=0.1, value=3.0, step=0.1, key="ms_fm")
        mortar_type = st.selectbox("Mortar / unit type (info only)", ["Concrete block - CMU", "Clay brick", "AAC / lightweight", "Other"], index=0, key="ms_unit")
        phi_axial = st.number_input("φ (axial) — design factor", min_value=0.5, max_value=1.0, value=0.65, step=0.01, key="ms_phip")
    with col3:
        K = st.number_input("Effective length factor K (for slenderness)", min_value=0.5, value=1.0, step=0.05, key="ms_K")
        Pu = st.number_input("Applied factored axial load, P_u (kN) (compressive >0)", min_value=0.0, value=200.0, step=1.0, key="ms_Pu")
        Mu = st.number_input("Applied factored moment, M_u (kN·m)", min_value=0.0, value=10.0, step=0.1, key="ms_Mu")

    st.markdown("---")
    st.markdown("### 🧾 Derived geometry & basic checks")

    # Convert units
    t_mm = thickness
    L_mm = wall_length * 1000.0
    h_mm = wall_height * 1000.0

    # Cross-sectional gross area (mm^2)
    Ag_mm2 = t_mm * L_mm  # thickness * loaded length

    # Approximate nominal axial capacity (N) — conservative simplified expression:
    #   Pn ≈ 0.45 * f_m * A_g  (where f_m in N/mm², A_g in mm²)  -> N
    # Many codes use prism strength and factors; this is an approximation for quick checks.
    Pn_N = 0.45 * fm * Ag_mm2  # N
    Pn_kN = Pn_N / 1000.0
    phiPn_kN = phi_axial * Pn_kN

    # ----------------------------
    # Slenderness (KL/r)
    # ----------------------------
    # Moment of inertia (about axis through centroid, bending about short axis — tall wall)
    # For rectangle: I = (b * h^3) / 12, where b = thickness (mm), h = wall height (mm)
    I_mm4 = (t_mm * (h_mm ** 3)) / 12.0
    # radius of gyration r = sqrt(I / Ag)
    r_mm = math.sqrt(I_mm4 / Ag_mm2) if Ag_mm2 > 0 else 0.0
    # Convert lengths to mm for KL/r
    KL_over_r = (K * wall_height * 1000.0) / r_mm if r_mm > 0 else float("inf")

    # ----------------------------
    # Approximate flexural capacity (very conservative estimate)
    # We estimate an approximate φM_n by assuming an equivalent compressive force 0.45*f_m*Ag
    # acts at an eccentricity of h/6 (i.e., lever arm ~ h/6). This is a simplification for quick checks.
    # ----------------------------
    lever_arm_mm = h_mm / 6.0
    Mn_Nmm = 0.45 * fm * Ag_mm2 * lever_arm_mm  # N·mm
    Mn_kNm = Mn_Nmm / 1e6
    phi_flex = st.number_input("φ (flexure) — design factor", min_value=0.5, max_value=1.0, value=0.9, step=0.01, key="ms_phim")
    phiMn_kNm = phi_flex * Mn_kNm

    # ----------------------------
    # Simple axial+moment interaction (linear conservative)
    #    interaction = (P_u / φP_n) + (M_u / φM_n)  -> OK if ≤ 1.0
    # ----------------------------
    interaction_ratio = 0.0
    if phiPn_kN > 0:
        interaction_ratio += Pu / phiPn_kN
    if phiMn_kNm > 0:
        interaction_ratio += Mu / phiMn_kNm

    # ----------------------------
    # Slenderness guidance (no automatic second-order amplification)
    # If KL/r > 20–30, slenderness may significantly reduce capacity — warn user.
    slender_warn = KL_over_r > 20.0

    # ----------------------------
    # Prepare display values (strings to avoid dtype issues)
    # ----------------------------
    results = {
        "Parameter": [
            "Loaded length L (m)",
            "Wall height h (m)",
            "Thickness t (mm)",
            "Gross area A_g (mm²)",
            "Masonry prism strength f_m (MPa)",
            "Approx. nominal axial capacity Pn (kN)",
            "Design axial capacity φP_n (kN)",
            "Effective KL/r",
            "Approx. nominal moment capacity M_n (kN·m)",
            "Design moment capacity φM_n (kN·m)",
            "Applied axial load P_u (kN)",
            "Applied moment M_u (kN·m)",
            "Axial+Moment interaction ratio (≤1 OK)"
        ],
        "Value": [
            f"{wall_length:.3f}",
            f"{wall_height:.3f}",
            f"{t_mm:.1f}",
            f"{Ag_mm2:,.0f}",
            f"{fm:.3f}",
            f"{Pn_kN:.2f}",
            f"{phiPn_kN:.2f}",
            f"{KL_over_r:.2f}",
            f"{Mn_kNm:.2f}",
            f"{phiMn_kNm:.2f}",
            f"{Pu:.2f}",
            f"{Mu:.2f}",
            f"{interaction_ratio:.3f}"
        ]
    }

    st.table(pd.DataFrame(results).set_index("Parameter"))

    # ----------------------------
    # PASS / FAIL messages
    # ----------------------------
    st.markdown("### Quick Checks")

    if Pu <= phiPn_kN:
        st.success(f"Axial OK — Applied P_u = {Pu:.2f} kN ≤ φP_n = {phiPn_kN:.2f} kN")
    else:
        st.error(f"Axial NG — Applied P_u = {Pu:.2f} kN > φP_n = {phiPn_kN:.2f} kN")

    if phiMn_kNm > 0:
        if Mu <= phiMn_kNm:
            st.success(f"Flexure OK (simple) — M_u = {Mu:.2f} kN·m ≤ φM_n = {phiMn_kNm:.2f} kN·m")
        else:
            st.warning(f"Flexure may be insufficient (simple) — M_u = {Mu:.2f} kN·m > φM_n = {phiMn_kNm:.2f} kN·m")

    if interaction_ratio <= 1.0:
        st.success(f"Interaction OK — ratio = {interaction_ratio:.3f} ≤ 1.0")
    else:
        st.error(f"Interaction NG — ratio = {interaction_ratio:.3f} > 1.0")

    if slender_warn:
        st.warning(
            f"KL/r = {KL_over_r:.2f} (high) — slenderness effects may reduce axial capacity. "
            "Consider slender wall provisions in NSCP (second-order effects, reduced P_n)."
        )

    st.markdown("---")
    st.subheader("Notes, limitations & references")
    st.markdown(r"""
    - The axial capacity formula used here (\(P_n \approx 0.45\,f_m\,A_g\)) is a **simplified** approximation for quick checks.
      NSCP uses prism strength, test data, and specific reduction factors — consult the code for final values.
    - The flexural capacity estimate is *very conservative*: we assumed an equivalent compressive force 0.45·f_m·A_g acting at h/6.
      Use the full block/strain-compatibility approach from NSCP for accurate φM_n.
    - Slenderness (KL/r) and second-order (P–Δ) effects are important for tall/narrow walls; this tool only warns when KL/r is large.
    - Always verify final designs using **NSCP 2015 masonry provisions**, manufacturer/lab prism tests, and a licensed structural engineer.
    """)
