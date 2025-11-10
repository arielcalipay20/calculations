import streamlit as st
import pandas as pd
import math

def display():
    st.header("🏗️ Structural Steel Purlin Design (NSCP-style)")

    st.markdown(r"""
    Purlin check (LRFD-style): bending, shear, deflection.  
    You may supply section properties (cold-formed or hot-rolled). The tool warns about lateral-torsional buckling (LTB) when unbraced length is large — purlins commonly rely on roof sheeting or bracing.
    """)

    # ----------------------------
    # Inputs: geometry, loads, section
    # ----------------------------
    st.markdown("### Inputs — Geometry, Loads & Section Properties")

    c1, c2, c3 = st.columns(3)
    with c1:
        span = st.number_input("Purlin span L (m)", min_value=0.5, value=4.0, step=0.1, key="purlin_L")
        spacing = st.number_input("Purlin spacing (m) — tributary width", min_value=0.2, value=1.2, step=0.05, key="purlin_spacing")
        roof_dead = st.number_input("Roof dead load (kN/m²)", min_value=0.0, value=0.25, step=0.05, key="purlin_dead")
    with c2:
        roof_live = st.number_input("Roof live/snow load (kN/m²)", min_value=0.0, value=0.5, step=0.05, key="purlin_live")
        additional_load = st.number_input("Additional line loads (kN/m) (wind/cladding etc.)", min_value=0.0, value=0.0, step=0.1, key="purlin_line")
        deflection_limit_choice = st.selectbox("Deflection limit", ["L/120", "L/180", "L/240"], index=1, key="purlin_def")
    with c3:
        section_name = st.text_input("Section name (optional)", value="C150x50", key="purlin_name")
        Sx = st.number_input("Elastic section modulus Sx (mm³)", min_value=0.0, value=20000.0, step=100.0, key="purlin_Sx")
        Zx = st.number_input("Plastic section modulus Zx (mm³) (optional)", min_value=0.0, value=22000.0, step=100.0, key="purlin_Zx")

    st.markdown("### Material & bracing")
    c4, c5 = st.columns(2)
    with c4:
        Fy = st.number_input("Yield strength F_y (MPa)", min_value=200.0, value=250.0, step=5.0, key="purlin_Fy")
        E = st.number_input("Elastic modulus E (MPa)", min_value=100000.0, value=200000.0, step=1000.0, key="purlin_E")
    with c5:
        Aw = st.number_input("Shear area A_w (mm²) (web shear area)", min_value=0.0, value=1500.0, step=10.0, key="purlin_Aw")
        Lb = st.number_input("Unbraced length L_b (mm) between lateral supports", min_value=0.0, value=1200.0, step=50.0, key="purlin_Lb")

    st.markdown("---")

    # ----------------------------
    # Derived loads on purlin (per unit length)
    # ----------------------------
    # include self-weight of purlin? user may add; we won't assume steel self-weight automatically.
    w_area = roof_dead + roof_live  # kN/m² ultimate will be factored later
    # Use common factored combo 1.2D + 1.6L (user can adapt)
    wu_area = 1.2 * roof_dead + 1.6 * roof_live  # kN/m²
    # tributary load per purlin (uniform) in kN/m
    w_uniform = wu_area * spacing + additional_load  # kN/m

    # ----------------------------
    # Bending & shear (simply supported)
    # ----------------------------
    M_max = (w_uniform * span**2) / 8.0   # kN·m
    V_max = (w_uniform * span) / 2.0      # kN

    # Nominal/plastic moment capacities
    # Use Mp = Fy * Zx (N·mm) -> convert to kN·m
    Mp_Nmm = Fy * Zx  # Fy in N/mm² and Zx in mm³ -> N·mm
    Mp_kNm = Mp_Nmm / 1e6
    # Use elastic-based Mn = Fy * Sx as alternative (conservative if Sx provided)
    Mn_elastic_kNm = (Fy * Sx) / 1e6  # kN·m

    # Choose governing nominal Mn as min(plastic, elastic) -- conservative
    Mn_nom_kNm = min(Mp_kNm if Zx > 0 else float("inf"), Mn_elastic_kNm if Sx > 0 else float("inf"))

    # LRFD phi for flexure
    phi_b = 0.90
    phiMn_kNm = phi_b * Mn_nom_kNm

    # Shear nominal: Vn = 0.6 * Fy * Aw (N) -> kN
    Vn_N = 0.6 * Fy * Aw
    Vn_kN = Vn_N / 1000.0
    phi_v = 0.90
    phiVn_kN = phi_v * Vn_kN

    # ----------------------------
    # Deflection
    # ----------------------------
    # need moment of inertia to compute deflection. approximate from Sx & section depth if I not provided.
    # If Sx and a guessed neutral axis depth z are given, I = Sx * z. We avoid guessing: ask user to provide I (optional)
    I_input = st.number_input("Moment of inertia Ix (mm⁴) (optional, 0 to skip)", min_value=0.0, value=0.0, step=1000.0, key="purlin_Ix")
    if I_input > 0:
        I_m4 = I_input / 1e12  # mm4 -> m4
    else:
        # fallback: estimate I from Sx assuming z ≈ 0.9*d_eff where d_eff estimated from Sx/Zx relation if both exist
        # if both Sx and Zx available, estimate depth ~ Zx/Sx
        if Sx > 0 and Zx > 0:
            depth_est_mm = Zx / Sx  # mm (approximate)
            z_mm = 0.9 * depth_est_mm
            I_m4 = (Sx * 1e-9) * (z_mm / 1000.0)  # Sx mm3 -> m3, times z (m) gives I (m4) approx
        else:
            I_m4 = None

    if I_m4 is None:
        deflection_mm = None
        deflection_ok = None
    else:
        # deflection formula for uniform load on simply supported: delta = 5 w L^4 / (384 E I)
        w_N_per_m = w_uniform * 1000.0
        E_N_per_m2 = E * 1e6
        delta_m = (5.0 * w_N_per_m * span**4) / (384.0 * E_N_per_m2 * I_m4)
        deflection_mm = delta_m * 1000.0
        # parse deflection limit
        if deflection_limit_choice == "L/120":
            limit_mm = (span * 1000.0) / 120.0
        elif deflection_limit_choice == "L/180":
            limit_mm = (span * 1000.0) / 180.0
        else:
            limit_mm = (span * 1000.0) / 240.0
        deflection_ok = deflection_mm <= limit_mm

    # ----------------------------
    # Lateral-torsional buckling (LTB) advisory
    # ----------------------------
    ltb_warn = Lb > 3000.0  # conservative threshold (mm). Purlins often braced by roof sheeting.

    # ----------------------------
    # Utilizations & pass/fail
    # ----------------------------
    util_flex = M_max / phiMn_kNm if phiMn_kNm > 0 else float("inf")
    util_shear = V_max / phiVn_kN if phiVn_kN > 0 else float("inf")

    bending_ok = util_flex <= 1.0
    shear_ok = util_shear <= 1.0

    # ----------------------------
    # Results table (string values)
    # ----------------------------
    st.markdown("### 🧾 Results Summary")

    results = {
        "Parameter": [
            "Section", "Span L (m)", "Tributary width (m)", "Uniform factored load w (kN/m)",
            "Max moment M_max (kN·m)", "Max shear V_max (kN)",
            "Selected Mn (kN·m)", "ΦMn (kN·m)",
            "Nominal shear Vn (kN)", "ΦVn (kN)",
            "Flexure utilization (M_u / ΦMn)", "Shear utilization (V_u / ΦVn)",
            "Deflection (mm)", "Deflection limit (mm)", "Deflection OK?",
            "Unbraced length Lb (mm)", "LTB advisory"
        ],
        "Value": [
            str(section_name),
            f"{span:.2f}",
            f"{spacing:.3f}",
            f"{w_uniform:.3f}",
            f"{M_max:.3f}",
            f"{V_max:.3f}",
            f"{Mn_nom_kNm:.3f}",
            f"{phiMn_kNm:.3f}",
            f"{Vn_kN:.3f}",
            f"{phiVn_kN:.3f}",
            f"{util_flex:.3f}",
            f"{util_shear:.3f}",
            f"{deflection_mm:.2f}" if deflection_mm is not None else "N/A",
            f"{limit_mm:.2f}" if I_m4 is not None else "N/A",
            "PASS" if deflection_ok else ("FAIL" if deflection_ok is False else "N/A"),
            f"{Lb:.0f}",
            "Check LTB" if ltb_warn else "OK (but verify bracing)"
        ]
    }
    st.table(pd.DataFrame(results).set_index("Parameter"))

    # ----------------------------
    # Checks / messages
    # ----------------------------
    st.markdown("### Checks")
    if bending_ok:
        st.success(f"Flexure OK — M_max = {M_max:.2f} kN·m ≤ ΦMn = {phiMn_kNm:.2f} kN·m (util {util_flex:.2f})")
    else:
        st.error(f"Flexure FAIL — M_max = {M_max:.2f} kN·m > ΦMn = {phiMn_kNm:.2f} kN·m (util {util_flex:.2f})")

    if shear_ok:
        st.success(f"Shear OK — V_max = {V_max:.2f} kN ≤ ΦVn = {phiVn_kN:.2f} kN (util {util_shear:.2f})")
    else:
        st.error(f"Shear FAIL — V_max = {V_max:.2f} kN > ΦVn = {phiVn_kN:.2f} kN (util {util_shear:.2f})")

    if deflection_mm is not None:
        if deflection_ok:
            st.success(f"Deflection OK — Δ = {deflection_mm:.2f} mm ≤ limit {limit_mm:.2f} mm")
        else:
            st.error(f"Deflection FAIL — Δ = {deflection_mm:.2f} mm > limit {limit_mm:.2f} mm")
    else:
        st.info("Deflection not computed (provide Ix to enable deflection check).")

    if ltb_warn:
        st.warning("Unbraced length Lb exceeds conservative threshold — perform LTB check per NSCP/AISC or provide additional bracing.")
    else:
        st.info("Unbraced length looks modest; still confirm LTB per code if in doubt.")

    st.markdown("---")
    st.markdown("### Notes & references")
    st.markdown(r"""
    - This module uses a conservative approach: chosen Mn = min(F_y·Z_x, F_y·S_x). Use LTB calculations for long unbraced lengths.  
    - LRFD φ for flexure and shear taken as 0.90. Confirm with NSCP clauses for exact φ values and buckling provisions.  
    - Provide accurate section properties (Sx, Zx, I) where possible for reliable checks.  
    - Purlins are typically supported by sheeting and bracing; ensure adequate lateral restraint to avoid LTB.
    """)
