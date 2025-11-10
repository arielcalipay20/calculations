import streamlit as st
import pandas as pd
import math

def display():
    st.header("🧱 RC Beam Design (NSCP-style) — Quick Check")
    st.markdown("Automatic checks for **flexure**, **shear**, and **approx. development length**. Adjust inputs and results update immediately.")

    # ----------------------------
    # Inputs
    # ----------------------------
    st.markdown("### Section & Material")
    c1, c2, c3 = st.columns(3)
    with c1:
        b = st.number_input("Beam width, b (mm)", min_value=50.0, value=300.0, step=10.0, key="rc_b")
        h = st.number_input("Overall depth, h (mm)", min_value=100.0, value=500.0, step=10.0, key="rc_h")
        cover = st.number_input("Clear cover (mm)", min_value=5.0, value=25.0, step=1.0, key="rc_cover")
    with c2:
        n_bars = st.number_input("No. of tension bars (n)", min_value=1, value=3, step=1, key="rc_nbars")
        bar_dia = st.number_input("Tension bar dia (mm)", min_value=6.0, value=16.0, step=1.0, key="rc_bardia")
        top_bars = st.number_input("No. of top bars (if any) (n)", min_value=0, value=0, step=1, key="rc_topbars")
    with c3:
        fck = st.number_input("Concrete strength f'c (MPa)", min_value=10.0, value=25.0, step=1.0, key="rc_fck")
        fy = st.number_input("Steel yield fy (MPa)", min_value=200.0, value=420.0, step=10.0, key="rc_fy")
        phi_flex = st.number_input("φ (flexure)", min_value=0.5, max_value=1.0, value=0.9, step=0.01, key="rc_phif")

    st.markdown("### Loads / Design actions")
    c4, c5, c6 = st.columns(3)
    with c4:
        Mu_req = st.number_input("Factored moment required, M_u (kN·m)", min_value=0.0, value=150.0, step=1.0, key="rc_Mu")
    with c5:
        Vu_req = st.number_input("Factored shear required, V_u (kN)", min_value=0.0, value=120.0, step=1.0, key="rc_Vu")
    with c6:
        comb_note = st.text_input("Load combo note (e.g. 1.2D+1.6L)", value="1.2D + 1.6L", key="rc_note")

    # Additional choices / defaults
    st.markdown("### Design options / defaults")
    
    colStirrup, colLegs, colPhi = st.columns(3)
    with colStirrup:
        stirrup_dia = st.number_input("Stirrup bar dia (mm)", min_value=4.0, value=8.0, step=1.0, key="rc_st_dia")
    with colLegs:
        legs = st.number_input("Stirrup legs (n legs)", min_value=2, value=2, step=1, key="rc_st_legs")
    with colPhi:
        phi_shear = st.number_input("φ (shear)", min_value=0.5, max_value=1.0, value=0.75, step=0.01, key="rc_phis")

    # ----------------------------
    # Internal calculations
    # ----------------------------
    # Areas
    As_mm2 = n_bars * (math.pi * (bar_dia ** 2) / 4.0)
    As_top_mm2 = top_bars * (math.pi * (bar_dia ** 2) / 4.0)

    # Effective depth d (mm)
    # approximate: d = h - cover - stirrup_clearance - 0.5*bar_dia
    # assume one layer of stirrup, clear spacing ~ stirrup_dia + 2 mm
    d = h - cover - stirrup_dia - 0.5 * bar_dia
    if d <= 0:
        st.error("Computed effective depth d ≤ 0 mm — check geometry inputs.")
        return

    # Flexure design (rectangular stress block)
    # a = (As * fy) / (0.85 * f'c * b)
    a_mm = (As_mm2 * fy) / (0.85 * fck * b)
    # nominal moment capacity Mn (N·mm) = As * fy * (d - a/2)
    Mn_Nmm = As_mm2 * fy * (d - a_mm / 2.0)
    Mn_kNm = Mn_Nmm / 1e6  # convert N·mm -> kN·m
    phiMn_kNm = phi_flex * Mn_kNm

    # Percentage reinforcement (rho)
    rho = (As_mm2 / (b * d)) * 100.0  # percent

    # Shear capacity (approximate, ACI-like): Vc (N) = 0.17 * sqrt(f'c) * b * d
    Vc_N = 0.17 * math.sqrt(max(fck, 1.0)) * b * d
    Vc_kN = Vc_N / 1000.0
    # Available shear by stirrups: Vs = 0.87 * fy * (Av * d / s)
    # We'll compute required Av/s if Vu > phi*Vc
    # Let V_s_required_N = (Vu_req*1000 - phi_shear*Vc_N) (if positive)
    V_required_N = max(Vu_req * 1000.0 - phi_shear * Vc_N, 0.0)
    # For a single stirrup cross-section area:
    Av_single_mm2 = legs * (math.pi * (stirrup_dia ** 2) / 4.0)
    # Required spacing s (mm) = (0.87 * fy * Av_single_mm2 * d) / V_required_N
    if V_required_N > 0:
        s_req_mm = (0.87 * fy * Av_single_mm2 * d) / V_required_N
        # limit spacing to d/2 or 300 mm per common practice
        s_limit_mm = min(d / 2.0, 300.0)
        s_used_mm = min(s_req_mm, s_limit_mm)
        stirrup_required = True
    else:
        s_req_mm = float("inf")
        s_limit_mm = min(d / 2.0, 300.0)
        s_used_mm = s_limit_mm
        stirrup_required = False

    # Approximate development length (ACI-based rough estimate) in mm:
    # ld = (fy * db) / (4 * sqrt(f'c))  (simple, does not include coatings or epoxy)
    ld_mm = (fy * bar_dia) / (4.0 * math.sqrt(max(fck, 1.0)))

    # Interaction / checks
    flexure_ok = phiMn_kNm >= Mu_req
    shear_ok = (phi_shear * Vc_kN + (0.87 * fy * Av_single_mm2 * d / s_used_mm) / 1000.0) >= Vu_req if V_required_N > 0 else (phi_shear * Vc_kN) >= Vu_req

    # Safety factors/margins
    flex_margin = (phiMn_kNm / Mu_req) if Mu_req > 0 else float("inf")
    shear_margin = ((phi_shear * Vc_kN + (0 if not stirrup_required else (0.87 * fy * Av_single_mm2 * d / s_used_mm) / 1000.0)) / Vu_req) if Vu_req > 0 else float("inf")

    # ----------------------------
    # Outputs / Table
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Section & Reinforcement Summary")
    st.table({
        "Parameter": [
            "Section width b (mm)",
            "Overall depth h (mm)",
            "Effective depth d (mm)",
            "Tension reinforcement As (mm²)",
            "Top reinforcement As_top (mm²)",
            "Reinforcement ratio ρ (%)",
            "Concrete f'c (MPa)",
            "Steel fy (MPa)"
        ],
        "Value": [
            f"{b:.0f}",
            f"{h:.0f}",
            f"{d:.0f}",
            f"{As_mm2:.1f}",
            f"{As_top_mm2:.1f}",
            f"{rho:.3f}",
            f"{fck:.1f}",
            f"{fy:.0f}"
        ]
    })

    st.markdown("### 🔍 Capacity Checks")
    st.table({
        "Check": [
            "Nominal moment Mn (kN·m)",
            "Design moment capacity φMn (kN·m)",
            "Required moment Mu (kN·m)",
            "Flexure check (φMn ≥ Mu)?",
            "Nominal shear Vc (kN)",
            "φ·Vc (kN)",
            "Vu required (kN)",
            "Stirrups required?",
            "Stirrup spacing used (mm) (s ≤ d/2, ≤300)"
        ],
        "Value": [
            f"{Mn_kNm:.2f}",
            f"{phiMn_kNm:.2f}",
            f"{Mu_req:.2f}",
            "PASS" if flexure_ok else "FAIL",
            f"{Vc_kN:.2f}",
            f"{(phi_shear * Vc_kN):.2f}",
            f"{Vu_req:.2f}",
            "Yes" if stirrup_required else "No",
            f"{s_used_mm:.1f}"
        ]
    })

    st.markdown("### 🧾 Additional Results")
    st.table({
        "Parameter": [
            "Required shear res. spacing s_req (mm)",
            "Stirrup single-leg area Av (mm²)",
            "Approx development length ld (mm)",
            "Flexure margin (φMn / Mu)",
            "Shear margin (available / required)"
        ],
        "Value": [
            f"{s_req_mm:.1f}" if s_req_mm != float("inf") else "N/A",
            f"{Av_single_mm2:.2f}",
            f"{ld_mm:.1f}",
            f"{flex_margin:.3f}",
            f"{shear_margin:.3f}"
        ]
    })

    st.markdown("---")
    st.markdown("#### Formulas / Notes")
    st.markdown(r"""
    - **Flexure:**  
      \(a = \\dfrac{A_s f_y}{0.85 f'_c b}\\),  
      \(M_n = A_s f_y \left(d - \\dfrac{a}{2}\\right)\).  
      Design capacity = \(\\phi M_n\) (φ default = 0.9).
    - **Shear:** approximate \(V_c = 0.17 \\sqrt{f'_c} b d\) (N) → /1000 to convert to kN.  
      If \(V_u > \\phi V_c\) then required shear reinforcement \(V_s = V_u - \\phi V_c\).  
      Use \(A_v\) of stirrups and compute spacing \(s \\approx \\dfrac{0.87 f_y A_v d}{V_s}\\).
    - **Development length (approx.):** \(l_d \\approx \\dfrac{f_y d_b}{4 \\sqrt{f'_c}}\\) (mm) — ACI-style estimate.
    """)
    st.warning("This tool gives approximate checks. Use NSCP 2015 (Section 10x/20x) for exact expressions, and consult a licensed engineer for final design.")
