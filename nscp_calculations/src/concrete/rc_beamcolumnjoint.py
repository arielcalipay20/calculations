import streamlit as st
import pandas as pd
import math

def display():

    st.header("🔗 RC Beam–Column Joint Checks (NSCP-style)")

    st.markdown(r"""
    Quick joint checks:
    - Joint shear demand vs joint shear capacity (Vc,j)
    - Required joint transverse reinforcement (stirrups or hoops)
    - Beam-bar anchorage / development length check into column
    - Simple guidance and pass/fail flags

    **Important:** Joint design is code-sensitive. Use NSCP/ACI clause and tables for final design.
    """)

    # ----------------------------
    # Geometry & materials
    # ----------------------------
    st.markdown("### Section & Material")
    c1, c2, c3 = st.columns(3)
    with c1:
        b_col = st.number_input("Column width b_col (mm)", value=350.0, min_value=50.0, step=10.0, key="jc_bcol")
        h_col = st.number_input("Column depth h_col (mm)", value=350.0, min_value=50.0, step=10.0, key="jc_hcol")
        col_cover = st.number_input("Column clear cover (mm)", value=25.0, min_value=0.0, step=1.0, key="jc_covercol")
    with c2:
        b_beam = st.number_input("Beam width b (mm)", value=300.0, min_value=50.0, step=10.0, key="jc_bbeam")
        h_beam = st.number_input("Beam overall depth h (mm)", value=500.0, min_value=100.0, step=10.0, key="jc_hbeam")
        beam_cover = st.number_input("Beam clear cover (mm)", value=25.0, min_value=0.0, step=1.0, key="jc_coverbeam")
    with c3:
        fck = st.number_input("Concrete strength f'c (MPa)", value=25.0, min_value=5.0, step=1.0, key="jc_fck")
        fy = st.number_input("Steel yield fy (MPa)", value=420.0, min_value=200.0, step=10.0, key="jc_fy")
        phi = st.number_input("φ (flexural) use", value=0.9, min_value=0.5, max_value=1.0, step=0.01, key="jc_phi")

    # ----------------------------
    # Beam reinforcement entering column
    # ----------------------------
    st.markdown("### Beam Reinforcement Entering Column")
    bc1, bc2 = st.columns(2)
    with bc1:
        n_bars = st.number_input("Number of tension bars developing into column (per face)", value=3, min_value=0, step=1, key="jc_nbars")
        bar_dia = st.number_input("Beam bar diameter (mm)", value=16.0, min_value=6.0, step=1.0, key="jc_bardia")
    with bc2:
        top_bars = st.number_input("Number of top bars crossing joint (if any)", value=0, min_value=0, step=1, key="jc_topbars")
        # approximate effective depth d_beam:
        d_beam = st.number_input("Effective depth of beam d (mm)", value=430.0, min_value=0.0, step=1.0, key="jc_dbeam")

    # ----------------------------
    # Actions (inputs from frame analysis)
    # ----------------------------
    st.markdown("### Actions from Frame Analysis (factored) — enter positive values")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        Vb = st.number_input("Factored shear in beam entering joint V_b (kN)", value=120.0, min_value=0.0, step=1.0, key="jc_Vb")
        Vc = st.number_input("Factored shear in column at joint V_c (kN)", value=80.0, min_value=0.0, step=1.0, key="jc_Vc")
    with ac2:
        Nd = st.number_input("Factored axial load in column N_d (kN) (+ compressive)", value=1000.0, step=10.0, key="jc_Nd")
        Md_top = st.number_input("Factored top moment in column M_top (kN·m)", value=50.0, step=1.0, key="jc_Mtop")
    with ac3:
        Md_bot = st.number_input("Factored bottom moment in column M_bot (kN·m)", value=60.0, step=1.0, key="jc_Mbot")
        joint_type = st.selectbox("Joint type", ["Interior", "Exterior", "Corner"], index=0, key="jc_joint_type")

    # ----------------------------
    # Derived geometry & areas
    # ----------------------------
    # approximate joint clear width (b_j) = column width + beam flange? for rectangular beams use column width
    b_j = b_col  # mm
    d_j = min(h_col, h_beam) - col_cover  # conservative joint depth (mm)
    if d_j <= 0:
        st.error("Computed joint effective depth <= 0 — check geometry inputs.")
        return

    # beam tension steel entering joint area
    As_beam_mm2 = n_bars * (math.pi * (bar_dia**2) / 4.0)

    # ----------------------------
    # Joint shear demand (ACI/NSCP style approximation)
    # per ACI/NSCP: V_j = ΣV_b + ... simplified here:
    # Use conservative estimate: joint shear demand Vj = Vb (left) + Vb (right) + Vc (if applicable)
    # For single-beam frame we approximate as Vj = Vb + Vc
    # ----------------------------
    Vj_demand_kN = Vb + Vc  # conservative envelope (kN)

    # ----------------------------
    # Joint shear capacity (approx)
    # ACI-318 uses: Vc = 0.17 * sqrt(f'c) * b_j * d_j   (N) — but joint has different expression.
    # We'll use a conservative concrete contribution: Vc_j (kN) = 0.17*sqrt(f'c)*b_j*d_j /1000
    # Then required shear reinforcement is computed accordingly.
    # ----------------------------
    Vc_j_N = 0.17 * math.sqrt(max(fck,1.0)) * b_j * d_j
    Vc_j_kN = Vc_j_N / 1000.0

    # design shear resistance available (φ·Vc_j)
    phiVc_j_kN = 0.75 * Vc_j_kN  # use φ for shear = 0.75 commonly

    # shear shortfall requiring joint transverse reinforcement (kN)
    V_short_kN = max(Vj_demand_kN - phiVc_j_kN, 0.0)

    # transverse reinforcement calculation:
    # use Vs provided by stirrups: Vs = 0.87*fy*Av * (d_j / s)
    # pick a representative stirrup configuration (legs and diameter) inputs
    st.markdown("### Joint transverse reinforcement assumption")
    tr1, tr2 = st.columns(2)
    with tr1:
        jt_st_dia = st.number_input("Joint stirrup dia (mm)", value=10.0, min_value=4.0, step=1.0, key="jc_stdia")
        jt_legs = st.number_input("Stirrup legs inside joint (n legs)", value=4, min_value=2, step=1, key="jc_stlegs")
    with tr2:
        jt_spacing = st.number_input("Target stirrup spacing s (mm)", value=150.0, min_value=25.0, step=5.0, key="jc_sts")

    Av_single_mm2 = jt_legs * (math.pi * (jt_st_dia**2) / 4.0)
    # available Vs from provided spacing (kN)
    Vs_available_N = 0.87 * fy * Av_single_mm2 * (d_j / jt_spacing)
    Vs_available_kN = Vs_available_N / 1000.0

    # check if available Vs >= required V_short
    joint_trans_ok = Vs_available_kN >= V_short_kN if V_short_kN > 0 else True

    # ----------------------------
    # Beam bar anchorage / development checks (approx)
    # use simple ACI-like ld = (fy * db) / (4 * sqrt(f'c))  (mm)
    # required embedment into column = max(ld, 12*db) etc. We'll show ld and compare to user-provided embed.
    # ----------------------------
    ld_mm = (fy * bar_dia) / (4.0 * math.sqrt(max(fck,1.0)))
    # ask user for provided embedment
    embed = st.number_input("Provided embedment of beam bars into column (mm)", value=300.0, min_value=0.0, step=10.0, key="jc_embed")
    embed_ok = embed >= ld_mm

    # ----------------------------
    # Interaction checks (very simplified)
    # For corner/exterior joints, consider additional demands — we'll flag based on joint_type
    # ----------------------------
    if joint_type == "Interior":
        joint_location_note = "Interior joint: typically receives shear from two beams."
    elif joint_type == "Exterior":
        joint_location_note = "Exterior joint: reinforcement needs to resist unbalanced shear."
    else:
        joint_location_note = "Corner joint: special detailing often required."

    # ----------------------------
    # Output Tables / Metrics
    # ----------------------------
    st.markdown("---")
    st.markdown("### 🧾 Joint Results Summary")
    st.table({
        "Parameter": [
            "Joint type",
            "Beam shear Vb (kN)",
            "Column shear Vc (kN)",
            "Joint shear demand Vj (kN)",
            "Concrete joint shear capacity φ·Vc_j (kN)",
            "Shear shortfall (kN) (if >0 => need transverse reinforcement)",
            "Provided stirrup Vs available (kN)",
            "Transverse reinforcement sufficient?"
        ],
        "Value": [
            joint_type,
            f"{Vb:.2f}",
            f"{Vc:.2f}",
            f"{Vj_demand_kN:.2f}",
            f"{phiVc_j_kN:.2f}",
            f"{V_short_kN:.2f}",
            f"{Vs_available_kN:.2f}",
            "PASS" if joint_trans_ok else "FAIL"
        ]
    })

    st.markdown("### 🔩 Beam Bar Anchorage / Development")
    st.table({
        "Parameter": [
            "Beam bars area As (mm²)",
            "Bar dia (mm)",
            "Calculated development length l_d (mm) (approx.)",
            "Provided embedment (mm)",
            "Embedment sufficient?"
        ],
        "Value": [
            f"{As_beam_mm2:.2f}",
            f"{bar_dia:.1f}",
            f"{ld_mm:.1f}",
            f"{embed:.1f}",
            "PASS" if embed_ok else "FAIL"
        ]
    })

    st.markdown("---")
    st.subheader("Formulas & Notes (summary)")
    st.markdown(r"""
    - **Joint shear demand (conservative):** \(V_j \approx V_b + V_c\). Use frame analysis for exact sign/direction.
    - **Concrete contribution (approx):** \(V_{c,j} \approx 0.17 \sqrt{f'_c} \, b_j \, d_j\) (N). Convert to kN by /1000.
    - **Design φ·V_{c,j}:** use φ for shear (typical 0.75).
    - **Shortfall:** \(V_{short} = V_j - \phi V_{c,j}\). If > 0, provide transverse joint reinforcement so that \(V_s \ge V_{short}\).
    - **Transverse reinforcement capacity:** \(V_s = 0.87 f_y A_v (d_j / s)\). Solve for spacing s or required Av.
    - **Development length (approx):** \(l_d \approx \dfrac{f_y d_b}{4 \sqrt{f'_c}}\) (mm). Use code for adjustments (coatings, confinement, hooks).
    """)
