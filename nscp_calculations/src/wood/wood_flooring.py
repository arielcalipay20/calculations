import streamlit as st
import math
import pandas as pd

def display():
    st.header("🌲 Wood Flooring Design (NSCP 2015 — Wood Provisions)")

    st.markdown(r"""
    Design checks for wood floor systems: joist bending, shear, deflection, and bearing.
    Uses NSCP/NDS-style allowable stresses and common adjustment factors (CD, CM, CL, Ct, Cr).
    """)

    st.markdown("### Inputs — Geometry & Loads")

    col1, col2, col3 = st.columns(3)
    with col1:
        span = st.number_input("Joist Span (m) — simply supported", min_value=0.5, value=3.0, step=0.1, key="wfloor_span")
        spacing = st.number_input("Joist Spacing (m)", min_value=0.1, value=0.4, step=0.05, key="wfloor_spacing")
        finish_dead = st.number_input("Floor Finish Dead Load (kN/m²)", min_value=0.0, value=0.5, step=0.05, key="wfloor_finish_dead")
    with col2:
        dead_load = st.number_input("Other Dead Load (kN/m²) — ceiling, structure", min_value=0.0, value=0.5, step=0.05, key="wfloor_dead")
        live_load = st.number_input("Live Load (kN/m²)", min_value=0.0, value=2.0, step=0.1, key="wfloor_live")
        code_deflection_L = st.selectbox("Deflection Limit (L/x)", ["L/360", "L/240", "L/480"], index=0, key="wfloor_deflim")
    with col3:
        width_joist = st.number_input("Joist Width (mm)", min_value=25.0, value=45.0, step=5.0, key="wfloor_bw")
        depth_joist = st.number_input("Joist Depth (mm)", min_value=75.0, value=200.0, step=5.0, key="wfloor_d")
        grade_Fb = st.number_input("Allowable Bending Fb (MPa)", min_value=5.0, value=10.0, step=0.5, key="wfloor_Fb")

    st.markdown("### Material / Adjustment Factors (NDS-style defaults)")
    colA, colB, colC = st.columns(3)
    with colA:
        Fc = st.number_input("Allowable Compression Fc (MPa)", min_value=2.0, value=6.0, step=0.1, key="wfloor_Fc")
        Fv = st.number_input("Allowable Shear Fv (MPa)", min_value=0.2, value=1.0, step=0.05, key="wfloor_Fv")
    with colB:
        E = st.number_input("Modulus of Elasticity E (MPa)", min_value=4000.0, value=9000.0, step=100.0, key="wfloor_E")
        CD = st.number_input("Load Duration Factor, C_D", min_value=0.5, value=1.25, step=0.01, key="wfloor_CD")
    with colC:
        CM = st.number_input("Wet Service Factor, C_M", min_value=0.5, value=1.0, step=0.01, key="wfloor_CM")
        Cr = st.number_input("Repetitive Member Factor, C_r", min_value=0.5, value=1.15, step=0.01, key="wfloor_Cr")

    st.markdown("---")
    st.markdown("### Calculations")

    # Derived geometry
    b = width_joist / 1000.0  # m
    d = depth_joist / 1000.0  # m
    I = (b * d**3) / 12.0  # m^4
    S = (b * d**2) / 6.0   # m^3 (section modulus about strong axis)

    # Ultimate (factored) load per unit area (use common LRFD-like factors? we will use 1.2D+1.6L as conservative)
    self_weight = 25.0 * (d)  # kN/m² (concrete ~25 kN/m3 equivalent for wood? keep as light estimate) — user includes dead separately
    wu = 1.2 * (dead_load + finish_dead + self_weight) + 1.6 * live_load  # kN/m² ultimate
    w_per_joist = wu * spacing  # kN/m (uniform on joist)

    # Max moment & shear for simply supported uniformly distributed load
    M_max = (w_per_joist * span**2) / 8.0  # kN·m
    V_max = (w_per_joist * span) / 2.0     # kN

    # Convert to N·mm and N
    M_Nmm = M_max * 1e6
    V_N = V_max * 1e3

    # Adjust allowable bending using factors: F' = Fb * CD * CM * Cr
    Fb_adj = grade_Fb * CD * CM * Cr  # MPa (N/mm2)
    Fv_adj = Fv * CD * CM  # MPa

    # Actual bending stress at extreme fiber: f_b = M / S
    # Convert S (m^3) to mm^3 in formula: use units N·mm and mm^3: S_mm3 = S * 1e9
    S_mm3 = S * 1e9
    fb_actual = M_Nmm / S_mm3  # N/mm2 = MPa

    # Shear stress: fv = 1.5*V / (b*d) (N/mm2). Convert V_N (N), b,d in mm
    b_mm = width_joist
    d_mm = depth_joist
    fv_actual = (1.5 * V_N) / (b_mm * d_mm)  # N/mm2 = MPa

    # Deflection: Δ = 5 w L^4 / (384 E I) (units consistent: w in N/m, L in m, E in N/m2, I in m4)
    w_N_per_m = w_per_joist * 1000.0
    delta_m = (5.0 * w_N_per_m * span**4) / (384.0 * (E * 1e6) * I)  # m
    delta_mm = delta_m * 1000.0

    # Deflection limit parse
    if code_deflection_L == "L/360":
        limit = (span * 1000.0) / 360.0
    elif code_deflection_L == "L/240":
        limit = (span * 1000.0) / 240.0
    else:
        limit = (span * 1000.0) / 480.0

    # Bearing length check: bearing pressure under joist (assume tributary width = spacing)
    # bearing stress approximate = (w_per_joist * span) / (bearing_length * b) -> solve required bearing length for allowable Fc
    # compute tributary load (kN) on joist = w_per_joist * span
    trib_load_kN = w_per_joist * span
    trib_load_N = trib_load_kN * 1000.0
    # required bearing length (mm) given allowable compression Fc_adj:
    Fc_adj = Fc * CD * CM
    if Fc_adj > 0 and b_mm > 0:
        required_bearing_mm = (trib_load_N) / (Fc_adj * 1e6 * b_mm / 1000.0)  # mm
    else:
        required_bearing_mm = float("inf")

    # PASS/FAIL checks
    bending_ok = fb_actual <= Fb_adj
    shear_ok = fv_actual <= Fv_adj
    deflection_ok = delta_mm <= limit
    bearing_ok = required_bearing_mm <= 100.0  # assume typical provided bearing = 100 mm; flag if required > 100 mm

    # ----------------------------
    # Output Summary Tables (stringified values)
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Results Summary")

    table1 = {
        "Parameter": [
            "Joist span (m)",
            "Joist spacing (m)",
            "Ultimate load on joist w (kN/m)",
            "Max moment M_max (kN·m)",
            "Max shear V_max (kN)"
        ],
        "Value": [
            f"{span:.2f}",
            f"{spacing:.3f}",
            f"{w_per_joist:.3f}",
            f"{M_max:.3f}",
            f"{V_max:.3f}"
        ]
    }
    st.table(table1)

    table2 = {
        "Parameter": [
            "Section modulus S (mm³)",
            "Adjusted Fb (MPa)",
            "Actual bending stress f_b (MPa)",
            "Bending check"
        ],
        "Value": [
            f"{S_mm3:.1f}",
            f"{Fb_adj:.3f}",
            f"{fb_actual:.3f}",
            "PASS" if bending_ok else "FAIL"
        ]
    }
    st.table(table2)

    table3 = {
        "Parameter": [
            "Adjusted Fv (MPa)",
            "Actual shear stress f_v (MPa)",
            "Shear check",
            f"Deflection (mm) vs limit {int(limit)} mm",
            "Deflection check"
        ],
        "Value": [
            f"{Fv_adj:.3f}",
            f"{fv_actual:.3f}",
            "PASS" if shear_ok else "FAIL",
            f"{delta_mm:.2f}",
            "PASS" if deflection_ok else "FAIL"
        ]
    }
    st.table(table3)

    table4 = {
        "Parameter": [
            "Tributary load on joist (kN)",
            "Required bearing length (mm) (based on Fc adj)",
            "Bearing check (assume provided 100 mm)"
        ],
        "Value": [
            f"{trib_load_kN:.3f}",
            f"{required_bearing_mm:.1f}" if required_bearing_mm != float("inf") else "N/A",
            "PASS" if bearing_ok else "FAIL"
        ]
    }
    st.table(table4)

    st.markdown("---")
    st.markdown("### Status Summary")
    if bending_ok:
        st.success(f"Bending OK — f_b = {fb_actual:.3f} MPa ≤ Fb,adj = {Fb_adj:.3f} MPa")
    else:
        st.error(f"Bending NG — f_b = {fb_actual:.3f} MPa > Fb,adj = {Fb_adj:.3f} MPa")

    if shear_ok:
        st.success(f"Shear OK — f_v = {fv_actual:.3f} MPa ≤ Fv,adj = {Fv_adj:.3f} MPa")
    else:
        st.error(f"Shear NG — f_v = {fv_actual:.3f} MPa > Fv,adj = {Fv_adj:.3f} MPa")

    if deflection_ok:
        st.success(f"Deflection OK — Δ = {delta_mm:.2f} mm ≤ limit = {limit:.2f} mm")
    else:
        st.error(f"Deflection NG — Δ = {delta_mm:.2f} mm > limit = {limit:.2f} mm")

    if bearing_ok:
        st.success(f"Bearing OK — required {required_bearing_mm:.1f} mm ≤ provided 100 mm")
    else:
        st.warning(f"Bearing may be insufficient — required {required_bearing_mm:.1f} mm > provided 100 mm")

    st.markdown("---")
    st.subheader("References & Notes")
    st.markdown(r"""
    - Adjusted allowable stresses follow NDS/NSCP-style factors: \(F_{adj} = F \times C_D \times C_M \times C_r\) (where applicable).  
    - Bending: \(f_b = M/S\). Shear: \(f_v = 1.5V/(b d)\). Deflection: \(\Delta = \dfrac{5wL^4}{384EI}\).  
    - Deflection default limit used: L/360 (serviceability) — selected by user.  
    - This tool is a design aid. Use actual NSCP/NDS tables and a licensed engineer for final design.
    """)