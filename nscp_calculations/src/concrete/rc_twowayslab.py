import streamlit as st
import math
import pandas as pd

def display():
    st.header("🟦 RC Two-Way Slab Design (NSCP-style)")

    st.markdown(r"""
    This module computes bending demands and required reinforcement for **two-way slabs**.
    **Note:** Moment coefficients depend on aspect ratio and boundary conditions — use NSCP tables
    for exact project work. Defaults are typical recommended values for **continuous panels**.
    You can override coefficients manually.
    """)

    # ----------------------------
    # Geometry & material inputs
    # ----------------------------
    st.markdown("### Geometry & Materials")
    c1, c2, c3 = st.columns(3)
    with c1:
        Lx = st.number_input("Short span Lx (m)", min_value=0.5, value=4.0, step=0.1, key="twoway_Lx")
        Ly = st.number_input("Long span Ly (m)", min_value=0.5, value=5.0, step=0.1, key="twoway_Ly")
        thickness_mm = st.number_input("Slab thickness h (mm)", min_value=50.0, value=150.0, step=5.0, key="twoway_h")
    with c2:
        dead_su = st.number_input("Superimposed dead load (kN/m²)", min_value=0.0, value=1.5, step=0.1, key="twoway_dead")
        live_load = st.number_input("Live load (kN/m²)", min_value=0.0, value=3.0, step=0.1, key="twoway_live")
        cover_mm = st.number_input("Concrete cover (mm)", min_value=10.0, value=20.0, step=1.0, key="twoway_cover")
    with c3:
        fck = st.number_input("Concrete f'c (MPa)", min_value=10.0, value=28.0, step=1.0, key="twoway_fck")
        fy = st.number_input("Steel fy (MPa)", min_value=200.0, value=415.0, step=5.0, key="twoway_fy")
        bar_dia = st.number_input("Bar diameter chosen (mm)", min_value=6.0, value=10.0, step=1.0, key="twoway_bardia")

    # ----------------------------
    # Support condition & coefficients
    # ----------------------------
    st.markdown("### Support Condition & Moment Coefficients")
    support = st.selectbox("Support condition (choose closest)", 
                           ["All edges continuous (interior panel)",
                            "Two opposite edges continuous",
                            "One edge continuous (other edges simple)"],
                           index=0, key="twoway_support")

    st.markdown("**Moment coefficients (m) — defaults supplied. Overwrite if you have NSCP table values.**")
    st.info("Moment sign convention used here: negative = hogging at supports (columns), positive = sagging at mid-span.")

    # default coefficient suggestions (typical, conservative)
    # m = M/(w L^2) ; different coefficients for short (x) and long (y) directions
    # these are approximate typical values — replace with NSCP table values when available
    if support.startswith("All edges continuous"):
        default_mx_neg = 0.045  # negative at supports in x-dir
        default_mx_pos = 0.030  # positive midspan in x-dir
        default_my_neg = 0.045
        default_my_pos = 0.030
    elif support.startswith("Two opposite edges continuous"):
        default_mx_neg = 0.06
        default_mx_pos = 0.02
        default_my_neg = 0.04
        default_my_pos = 0.025
    else:  # one edge continuous
        default_mx_neg = 0.08
        default_mx_pos = 0.02
        default_my_neg = 0.05
        default_my_pos = 0.02

    colA, colB = st.columns(2)
    with colA:
        mx_neg = st.number_input("m_x (neg at support, x-dir)", value=float(default_mx_neg), format="%.4f", step=0.001, key="twoway_mxneg")
        mx_pos = st.number_input("m_x (pos at mid, x-dir)", value=float(default_mx_pos), format="%.4f", step=0.001, key="twoway_mxpos")
    with colB:
        my_neg = st.number_input("m_y (neg at support, y-dir)", value=float(default_my_neg), format="%.4f", step=0.001, key="twoway_myneg")
        my_pos = st.number_input("m_y (pos at mid, y-dir)", value=float(default_my_pos), format="%.4f", step=0.001, key="twoway_mypos")

    # ----------------------------
    # Loads and ultimate design load
    # ----------------------------
    st.markdown("### Loads & Ultimate Load")
    gamma_dead = 1.2
    gamma_live = 1.6
    h_m = thickness_mm / 1000.0
    self_weight = 25.0 * h_m  # kN/m² using concrete density ~25 kN/m3
    wu = gamma_dead * (dead_su + self_weight) + gamma_live * live_load  # kN/m² ultimate
    st.write(f"Ultimate uniformly distributed load w_u = {wu:.3f} kN/m² (includes self-weight)")

    # ----------------------------
    # Aspect ratio and span selection
    # ----------------------------
    AR = Ly / Lx if Lx > 0 else 1.0
    st.write(f"Aspect ratio Ly/Lx = {AR:.3f}")

    # choose span lengths for moment formula: in two-way design, use the shorter span L = Lx for x-dir moments, and Ly for y-dir
    # compute moments: M = m * w * L^2  (kN·m per meter width)
    Mx_neg = mx_neg * wu * (Lx ** 2)
    Mx_pos = mx_pos * wu * (Lx ** 2)
    My_neg = my_neg * wu * (Ly ** 2)
    My_pos = my_pos * wu * (Ly ** 2)

    # ----------------------------
    # Required steel (per meter width) for each moment
    # φMn = Mu  =>  As = Mu*1e6 / (φ * fy * z) ; assume z ≈ 0.9 d
    # d estimate:
    d_mm = thickness_mm - cover_mm - bar_dia / 2.0
    if d_mm <= 0:
        st.error("Effective depth d ≤ 0. Check slab thickness, cover, or bar diameter.")
        return
    d_m = d_mm / 1000.0
    phi = 0.9

    def As_req_for_M(M_kNm):
        # convert to N·mm
        Mu_Nmm = M_kNm * 1e6
        z = 0.9 * d_m * 1000.0  # mm (approx), but keep N·mm units consistent -> use mm
        # use mm units: Mu_Nmm (N·mm), fy in MPa (~N/mm2)
        # As (mm2) = Mu_Nmm / (phi * fy (N/mm2) * z(mm))
        return Mu_Nmm / (phi * fy * z)

    As_mx_neg = As_req_for_M(Mx_neg)  # mm2 per meter width (since M in kN·m per meter)
    As_mx_pos = As_req_for_M(Mx_pos)
    As_my_neg = As_req_for_M(My_neg)
    As_my_pos = As_req_for_M(My_pos)

    # Convert As per meter to nominal bar spacing for chosen bar diameter
    bar_area_mm2 = math.pi * (bar_dia ** 2) / 4.0
    # required spacing s = bar_area / (As_required per mm width)
    # As_required per mm width = As_required per 1000 mm (since As computed for 1 m width)
    def spacing_for_As(As_mm2_per_m):
        if As_mm2_per_m <= 0:
            return float("inf")
        # bar area per bar (mm2), spacing s (mm) = 1000 * bar_area / As_required (mm2/m)
        s_mm = 1000.0 * bar_area_mm2 / As_mm2_per_m
        return s_mm

    s_mx_neg = spacing_for_As(As_mx_neg)
    s_mx_pos = spacing_for_As(As_mx_pos)
    s_my_neg = spacing_for_As(As_my_neg)
    s_my_pos = spacing_for_As(As_my_pos)

    # Apply practical spacing limits per NSCP: spacing ≤ 3*d and ≤ 300 mm, and ≥ 75 mm (clear spacing)
    def enforce_spacing_limits(s_mm):
        if s_mm == float("inf"):
            return "N/A"
        s_limit = min(3 * d_mm, 300.0)
        s_min = 75.0
        s_used = max(min(s_mm, s_limit), s_min)
        return round(s_used, 1)

    s_mx_neg_used = enforce_spacing_limits(s_mx_neg)
    s_mx_pos_used = enforce_spacing_limits(s_mx_pos)
    s_my_neg_used = enforce_spacing_limits(s_my_neg)
    s_my_pos_used = enforce_spacing_limits(s_my_pos)

    # Minimum reinforcement per NSCP (typical): As_min = 0.0012 * b * h (for mild steel) or per code
    Ag_mm2_per_m = 1000.0 * thickness_mm  # mm2 per meter width
    As_min1 = 0.0012 * Ag_mm2_per_m
    As_min2 = 0.4 * math.sqrt(max(fck,1.0)) / fy * Ag_mm2_per_m  # alternative expression
    As_min_mm2_per_m = max(As_min1, As_min2)

    # check provided As vs required: assume user will provide bars at spacing s_used => As_provided = 1000 * bar_area / s_used
    def As_provided_from_spacing(s_mm):
        if isinstance(s_mm, str) or s_mm == "N/A":
            return 0.0
        return 1000.0 * bar_area_mm2 / s_mm

    As_prov_mx_neg = As_provided_from_spacing(s_mx_neg_used)
    As_prov_mx_pos = As_provided_from_spacing(s_mx_pos_used)
    As_prov_my_neg = As_provided_from_spacing(s_my_neg_used)
    As_prov_my_pos = As_provided_from_spacing(s_my_pos_used)

    # Determine pass/fail
    mx_neg_ok = As_prov_mx_neg >= max(As_mx_neg, As_min_mm2_per_m)
    mx_pos_ok = As_prov_mx_pos >= max(As_mx_pos, As_min_mm2_per_m)
    my_neg_ok = As_prov_my_neg >= max(As_my_neg, As_min_mm2_per_m)
    my_pos_ok = As_prov_my_pos >= max(As_my_pos, As_min_mm2_per_m)

    # ----------------------------
    # Output tables and metrics
    # ----------------------------
    st.markdown("### 🧾 Moments & Required Reinforcement (per 1 m width)")

    table1 = {
        "Parameter": [
            "Ultimate load w_u (kN/m²)",
            "Mx (neg) (kN·m/m)",
            "Mx (pos) (kN·m/m)",
            "My (neg) (kN·m/m)",
            "My (pos) (kN·m/m)",
            "Effective depth d (mm)",
            "Aspect ratio Ly/Lx"
        ],
        "Value": [
            f"{wu:.3f}",
            f"{Mx_neg:.3f}",
            f"{Mx_pos:.3f}",
            f"{My_neg:.3f}",
            f"{My_pos:.3f}",
            f"{d_mm:.1f}",
            f"{AR:.3f}"
        ]
    }
    st.table(table1)

    st.markdown("#### Required steel (As) and spacing suggestions")
    df_req = pd.DataFrame({
        "Location": ["Mx neg (x-support)", "Mx pos (x-mid)", "My neg (y-support)", "My pos (y-mid)"],
        "M (kN·m/m)": [round(Mx_neg,3), round(Mx_pos,3), round(My_neg,3), round(My_pos,3)],
        "As required (mm²/m)": [round(As_mx_neg,2), round(As_mx_pos,2), round(As_my_neg,2), round(As_my_pos,2)],
        "Suggested spacing (mm)": [s_mx_neg_used, s_mx_pos_used, s_my_neg_used, s_my_pos_used],
        "As provided at suggested spacing (mm²/m)": [round(As_prov_mx_neg,2), round(As_prov_mx_pos,2), round(As_prov_my_neg,2), round(As_prov_my_pos,2)],
        "Meets requirement?": ["PASS" if mx_neg_ok else "FAIL", "PASS" if mx_pos_ok else "FAIL",
                               "PASS" if my_neg_ok else "FAIL", "PASS" if my_pos_ok else "FAIL"]
    })
    st.dataframe(df_req, use_container_width=True, height=220)

    st.markdown("#### Minimum reinforcement check")
    st.table({
        "Parameter": ["As_min (mm²/m)", "Provided As (worst-case mm²/m)", "Meets min steel?"],
        "Value": [f"{As_min_mm2_per_m:.1f}", f"{min(As_prov_mx_neg, As_prov_mx_pos, As_prov_my_neg, As_prov_my_pos):.1f}",
                  "PASS" if min(As_prov_mx_neg, As_prov_mx_pos, As_prov_my_neg, As_prov_my_pos) >= As_min_mm2_per_m else "FAIL"]
    })

    st.markdown("---")
    st.subheader("Formulas & Notes")
    st.markdown(r"""
    - Design moments used: \(M = m \, w_u \, L^2\) where \(m\) = moment coefficient from NSCP tables (user-overridable).
    - \(w_u\) includes self-weight (assumed concrete density \(25 \,\text{kN/m}^3\)).
    - Required steel (per meter width) approximated by:  
      \[
      A_s \approx \frac{M \times 10^6}{\phi f_y z}
      \]
      with \(z \approx 0.9 d\).
    - Practical spacing limits enforced: \(s \le \min(3d, 300\,\text{mm})\) and \(s \ge 75\,\text{mm}\).
    - Minimum reinforcement: \(A_{s,\min} = \max(0.0012 A_g, \; 0.4\sqrt{f'_c}/f_y \times A_g)\) (per-meter width basis).
    """)
    st.caption("This is a design aid. Replace coefficients with exact NSCP table values for final designs and verify with a licensed structural engineer.")
