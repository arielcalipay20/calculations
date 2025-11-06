import streamlit as st
import pandas as pd

def display():
    st.header("🔩 Anchorage Checks (NSCP template)")

    st.markdown("""
    This module helps check anchor designs (tension and shear) using user-supplied characteristic
    capacities (from NSCP tables, manufacturer or test reports).  
    Enter the applied loads, number and arrangement of anchors, and the anchor/component capacities.
    """)

    # ----------------------------
    # Basic Inputs (loads & config)
    # ----------------------------
    st.markdown("### Input — Loads & Configuration")
    c1, c2, c3 = st.columns(3)

    with c1:
        fact_load_t = st.number_input("Applied tensile design load (T_d) [kN]", min_value=0.0, value=20.0, step=0.1, key="anch_Td")
        fact_load_v = st.number_input("Applied shear design load (V_d) [kN]", min_value=0.0, value=10.0, step=0.1, key="anch_Vd")
        n_anchors = st.number_input("Number of anchors (n)", min_value=1, value=2, step=1, key="anch_n")

    with c2:
        phi_t = st.number_input("Strength reduction factor φ_t (tension)", min_value=0.0, value=0.75, step=0.01, key="anch_phi_t")
        phi_v = st.number_input("Strength reduction factor φ_v (shear)", min_value=0.0, value=0.75, step=0.01, key="anch_phi_v")
        edge_dist = st.number_input("Edge distance (m)", min_value=0.0, value=0.15, step=0.01, key="anch_edge")

    with c3:
        concrete_fck = st.number_input("Concrete compressive strength f'c (MPa)", min_value=5.0, value=25.0, step=1.0, key="anch_fck")
        embed = st.number_input("Embedment depth (mm)", min_value=10.0, value=100.0, step=5.0, key="anch_embed")
        anchor_dia = st.number_input("Anchor diameter (mm)", min_value=6.0, value=16.0, step=1.0, key="anch_dia")

    st.markdown("---")
    st.markdown("### Input — Anchor Characteristic Capacities (from NSCP / manufacturer / test)")

    colA, colB, colC = st.columns(3)
    with colA:
        cap_conc_breakout = st.number_input("Concrete breakout capacity (N_char) [kN]", min_value=0.0, value=60.0, step=1.0, key="anch_cb")
        cap_pullout = st.number_input("Pullout capacity (kN) (if available)", min_value=0.0, value=80.0, step=1.0, key="anch_po")
    with colB:
        cap_steel = st.number_input("Steel (tensile) capacity (kN)", min_value=0.0, value=100.0, step=1.0, key="anch_st")
        cap_shear = st.number_input("Shear capacity (kN)", min_value=0.0, value=90.0, step=1.0, key="anch_sv")
    with colC:
        cap_anchor_test = st.number_input("Characteristic anchor test capacity (kN) (optional)", min_value=0.0, value=0.0, step=1.0, key="anch_test")
        k_group_factor = st.number_input("Group reduction factor k_g (for group effect)", min_value=0.0, value=1.0, step=0.01, key="anch_kg")

    st.markdown("---")
    st.markdown("### Load factors / combinations")
    
    colGamma1, colGamma2 = st.columns(2)
    with colGamma1:
        gamma1 = st.number_input("Load factor for tension (γ_T)", value=1.0, step=0.01, key="anch_gammaT")
    with colGamma2:
        gamma2 = st.number_input("Load factor for shear (γ_V)", value=1.0, step=0.01, key="anch_gammaV")

    # ----------------------------
    # Derived / required checks
    # ----------------------------
    # Required capacity per anchor (simple equal-share assumption)
    required_T_per_anchor = (fact_load_t * gamma1) / float(n_anchors)
    required_V_per_anchor = (fact_load_v * gamma2) / float(n_anchors)

    # Effective characteristic capacity per anchor (choose the minimum controlling mode)
    # If a specific test capacity is provided, consider it first.
    char_capacity_t = cap_anchor_test if cap_anchor_test > 0 else min(cap_conc_breakout, cap_pullout, cap_steel)
    char_capacity_v = cap_shear

    # Apply group factor (k_g) and phi
    design_capacity_t = (char_capacity_t * k_group_factor) * phi_t
    design_capacity_v = (char_capacity_v * k_group_factor) * phi_v

    # Safety margins
    margin_t = design_capacity_t / required_T_per_anchor if required_T_per_anchor > 0 else float("inf")
    margin_v = design_capacity_v / required_V_per_anchor if required_V_per_anchor > 0 else float("inf")

    # Simple combined check (interaction) — conservative linear interaction (not code-specific)
    # (T_req / T_cap) + (V_req / V_cap) <= 1.0
    interaction_ratio = 0.0
    if design_capacity_t > 0:
        interaction_ratio += required_T_per_anchor / design_capacity_t
    if design_capacity_v > 0:
        interaction_ratio += required_V_per_anchor / design_capacity_v

    # ----------------------------
    # Results display
    # ----------------------------
    st.markdown("### Anchorage Results")

    cols = st.columns(2)
    with cols[0]:
        st.metric("Reqd T per anchor (kN)", f"{required_T_per_anchor:.2f}")
        st.metric("Char T capacity (kN)", f"{char_capacity_t:.2f}")
        st.metric("Design T capacity (φ·k_g·N) (kN)", f"{design_capacity_t:.2f}")
    with cols[1]:
        st.metric("Reqd V per anchor (kN)", f"{required_V_per_anchor:.2f}")
        st.metric("Char V capacity (kN)", f"{char_capacity_v:.2f}")
        st.metric("Design V capacity (φ·k_g·N) (kN)", f"{design_capacity_v:.2f}")

    st.markdown("---")
    st.markdown("### 🧾 Anchorage Results Summary")

    st.table({
        "Parameter": [
            "Tension required per anchor (kN)",
            "Available tension capacity (kN) — design",
            "Tension safety margin (cap / req)",
            "Shear required per anchor (kN)",
            "Available shear capacity (kN) — design",
            "Shear safety margin (cap / req)",
            "Interaction ratio (T/Tcap + V/Vcap)"
        ],
        "Value": [
            f"{required_T_per_anchor:.2f}",
            f"{design_capacity_t:.2f}",
            f"{margin_t:.2f} ×",
            f"{required_V_per_anchor:.2f}",
            f"{design_capacity_v:.2f}",
            f"{margin_v:.2f} ×",
            f"{interaction_ratio:.3f}"
        ]
    })