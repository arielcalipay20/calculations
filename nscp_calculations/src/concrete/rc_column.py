import streamlit as st
import math
import pandas as pd

def display():
    st.header("🏗️ RC Column Design (NSCP-style)")

    st.markdown("Quick checks for axial capacity, flexure and interaction (one-axis). Results update automatically.")

    # ----------------------------
    # Geometry & material
    # ----------------------------
    st.subheader("Geometry & Material")
    c1, c2, c3 = st.columns(3)
    with c1:
        b = st.number_input("Column width, b (mm)", value=350.0, min_value=100.0, step=10.0, key="col_b")
        h = st.number_input("Column depth, h (mm)", value=350.0, min_value=100.0, step=10.0, key="col_h")
        col_height = st.number_input("Clear height between bracing / story height, l (mm)", value=3000.0, min_value=200.0, step=50.0, key="col_l")
    with c2:
        cover = st.number_input("Clear cover to longitudinal bars (mm)", value=40.0, min_value=5.0, step=1.0, key="col_cover")
        fck = st.number_input("Concrete strength f'c (MPa)", value=25.0, min_value=5.0, step=1.0, key="col_fck")
        fy = st.number_input("Steel yield strength fy (MPa)", value=420.0, min_value=200.0, step=10.0, key="col_fy")
    with c3:
        n_bars = st.number_input("No. of longitudinal bars (n)", value=8, min_value=2, step=1, key="col_nbars")
        bar_dia = st.number_input("Longitudinal bar dia (mm)", value=20.0, min_value=6.0, step=1.0, key="col_bardia")
        tie_dia = st.number_input("Tie/stirrup dia (mm)", value=10.0, min_value=4.0, step=1.0, key="col_tiedia")

    # ----------------------------
    # Actions (factored)
    # ----------------------------
    st.subheader("Factored Actions (from frame analysis)")
    a1, a2 = st.columns(2)
    with a1:
        Pu = st.number_input("Axial factored load, P_u (kN) (compressive >0)", value=1200.0, min_value=0.0, step=10.0, key="col_Pu")
        Mu_x = st.number_input("Factored moment about strong axis M_x (kN·m)", value=60.0, step=1.0, key="col_Mx")
    with a2:
        Mu_y = st.number_input("Factored moment about weak axis M_y (kN·m) — optional", value=20.0, step=1.0, key="col_My")
        note = st.text_input("Note / load combo", "1.2D + 1.6L", key="col_note")

    # ----------------------------
    # Derived geometry & steel areas
    # ----------------------------
    Ag_mm2 = b * h
    As_single_mm2 = math.pi * (bar_dia ** 2) / 4.0
    As_total_mm2 = n_bars * As_single_mm2

    # effective depth for flexure estimate (about strong axis) — choose c from centroid of bars
    # approximate lever arm z ≈ 0.9 * (h - cover - tie_dia - 0.5*bar_dia)
    d_mm = h - cover - tie_dia - 0.5 * bar_dia
    z_mm = 0.9 * d_mm if d_mm > 0 else 0.85 * h

    # ----------------------------
    # Slenderness check KL/r
    # ----------------------------
    # Moment of inertia about strong axis (centroidal) for rectangular gross section: I = b*h^3 / 12 (mm^4)
    I_x = (b * (h ** 3)) / 12.0
    # radius of gyration r = sqrt(I/Ag)
    r_x = math.sqrt(I_x / Ag_mm2) if Ag_mm2 > 0 else 0.0
    # effective length factor K — conservative default 1.0 (pinned-pinned). Let user change if desired.
    K = st.number_input("Effective length factor K (default 1.0)", min_value=0.5, value=1.0, step=0.05, key="col_K")
    KL_over_r = (K * col_height) / r_x if r_x > 0 else float("inf")

    # ----------------------------
    # Axial capacity (tied column approx)
    # Pn = 0.85 f'c (Ag - As) + fy As  (units N)
    # convert to kN
    # Use typical φ_axial = 0.65..0.75; NSCP/ACI may have code φ for columns — use φ_axial input
    phi_axial = st.number_input("φ (axial) — use code value (typical 0.75)", min_value=0.5, max_value=1.0, value=0.75, step=0.01, key="col_phi_axial")
    Pn_N = 0.85 * fck * (Ag_mm2 - As_total_mm2) + fy * As_total_mm2
    Pn_kN = Pn_N / 1000.0
    phiPn_kN = phi_axial * Pn_kN

    # ----------------------------
    # Flexural capacity about strong axis (approx using rectangular stress block)
    # Approx: a = (As*fy) / (0.85 f'c b); Mn = As*fy*(d - a/2) (N·mm) -> kN·m
    a_mm = (As_total_mm2 * fy) / (0.85 * fck * b) if (0.85 * fck * b) != 0 else 0.0
    Mn_Nmm = As_total_mm2 * fy * max((d_mm - a_mm / 2.0), 0.0)
    Mn_kNm = Mn_Nmm / 1e6
    phi_flex = st.number_input("φ (flexure) — typical 0.9", min_value=0.5, max_value=1.0, value=0.9, step=0.01, key="col_phi_flex")
    phiMn_kNm = phi_flex * Mn_kNm

    # ----------------------------
    # Interaction check (axial + uni-axial moment about x)
    # Conservative linear interaction (NSCP/ACI curve more accurate, this is a quick check):
    # (P_u / (φP_n)) + (M_u / (φM_n)) <= 1.0  (units consistent: Pu in kN, φPn in kN; Mu and φMn in kN·m)
    interaction_ratio_x = 0.0
    if phiPn_kN > 0:
        interaction_ratio_x += Pu / phiPn_kN
    if phiMn_kNm > 0:
        interaction_ratio_x += Mu_x / phiMn_kNm

    # For bi-axial moment a simple conservative extension:
    # Add contribution of M_y normalized by φMn about y using same As (very conservative)
    # Estimate Mn about weak axis by swapping b and h (rough)
    # compute Mn_y
    a_y = (As_total_mm2 * fy) / (0.85 * fck * h) if (0.85 * fck * h) != 0 else 0.0
    d_y = b - cover - tie_dia - 0.5 * bar_dia
    Mn_y_Nmm = As_total_mm2 * fy * max((d_y - a_y / 2.0), 0.0)
    Mn_y_kNm = Mn_y_Nmm / 1e6
    phiMn_y_kNm = phi_flex * Mn_y_kNm if Mn_y_kNm > 0 else 0.0
    interaction_ratio_xy = interaction_ratio_x
    if phiMn_y_kNm > 0:
        interaction_ratio_xy += Mu_y / phiMn_y_kNm

    # ----------------------------
    # Minimum longitudinal reinforcement (NSCP-ish minimum)
    # typical min As >= 0.01 Ag or >= (0.4*sqrt(f'c)/fy)*Ag, choose max
    As_min1 = 0.01 * Ag_mm2
    As_min2 = (0.4 * math.sqrt(max(fck,1.0)) / fy) * Ag_mm2
    As_min_mm2 = max(As_min1, As_min2)
    As_ok = As_total_mm2 >= As_min_mm2

    # ----------------------------
    # Results presentation
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")
    st.table({
        "Parameter": [
            "Gross area A_g (mm²)",
            "Total long. steel A_s (mm²)",
            "Effective depth d (mm)",
            "Radius of gyration r_x (mm)",
            "KL/r (unitless)"
        ],
        "Value": [
            f"{Ag_mm2:.0f}",
            f"{As_total_mm2:.1f}",
            f"{d_mm:.1f}",
            f"{r_x:.2f}",
            f"{KL_over_r:.2f}"
        ]
    })

    st.markdown("#### Capacity Checks")
    st.table({
        "Check": [
            "Nominal axial capacity Pn (kN)",
            "Design axial capacity φPn (kN)",
            "Applied axial load Pu (kN)",
            "Axial check (Pu ≤ φPn)?",
            "Nominal moment capacity Mn about strong axis (kN·m)",
            "Design moment capacity φMn (kN·m)",
            "Applied moment Mx (kN·m)",
            "Flexure check (Mx ≤ φMn)?",
            "Axial+moment interaction (ratio ≤ 1?)",
            "Minimum reinforcement As_min (mm²)",
            "Provided As ≥ As_min?"
        ],
        "Value": [
            f"{Pn_kN:.2f}",
            f"{phiPn_kN:.2f}",
            f"{Pu:.2f}",
            "PASS" if Pu <= phiPn_kN else "FAIL",
            f"{Mn_kNm:.2f}",
            f"{phiMn_kNm:.2f}",
            f"{Mu_x:.2f}",
            "PASS" if Mu_x <= phiMn_kNm else "FAIL",
            f"{interaction_ratio_x:.3f}  (≤1 OK)",
            f"{As_min_mm2:.1f}",
            "PASS" if As_ok else "FAIL"
        ]
    })

    st.markdown("---")
    st.subheader("⚠️ Notes & Warnings")
    if KL_over_r > 12:
        st.warning("KL/r > 12 — column may be slender. Check slender-column provisions in NSCP (second-order effects, reduced capacities).")
    if Pu > phiPn_kN:
        st.error("Applied axial load Pu exceeds design axial capacity φPn — revise section or reinforcement.")
    if interaction_ratio_x > 1.0:
        st.error("Axial + moment interaction ratio > 1.0 — section not adequate under combined action (conservative linear check).")

    st.markdown(r"""
    **Formulas used (simplified / conservative):**
    - \(P_n = 0.85 f'_c (A_g - A_s) + f_y A_s\)  (N) → /1000 → kN  
    - \(M_n \\approx A_s f_y (d - a/2)\), where \(a = \\dfrac{A_s f_y}{0.85 f'_c b}\) (N·mm → kN·m)  
    - Interaction (conservative linear): \(\\dfrac{P_u}{\\phi P_n} + \\dfrac{M_u}{\\phi M_n} \\le 1\)
    - Radius of gyration: \(r = \\sqrt{I/A_g}\), \(I = b h^3 / 12\) for rectangular section (about strong axis)
    - Minimum steel: \(A_{s,min} = \\max(0.01 A_g, \\; 0.4 \\dfrac{\\sqrt{f'_c}}{f_y} A_g )\)
    """)

    st.caption("This is a simplified design aid. Use NSCP 2015 text, tables and a licensed engineer for final design checks.")
