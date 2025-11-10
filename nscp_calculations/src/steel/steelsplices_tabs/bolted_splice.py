# streamlit_bolted_splice.py
import streamlit as st
import math

def display():
    st.header("🔩 Bolted Splice — NSCP / AISC style calculation template")
    st.markdown(
        r"""
        This tool performs typical bolted splice checks used in NSCP/AISC workflows:
        - gross/net area (tension)
        - bolt shear capacity (per bolt, including number of shear planes)
        - bearing capacity at bolt holes
        - block shear checks for plate or connected element
        - simple moment/axial combination check (transfer)
        
        **Notes**
        - This is a calculation *template*. Default factors are provided but **verify with your project's chosen design method (LRFD/ASD)** and the code clauses.
        - References: AISC connection design examples and NSCP connection notes. 
        """
    )

    st.subheader("Materials & code factors (editable)")
    col1, col2 = st.columns(2)
    with col1:
        Fy = st.number_input("Fy — Yield strength of connected member (MPa)", value=250.0, step=10.0)
        Fu = st.number_input("Fu — Ultimate strength of connected member (MPa)", value=410.0, step=10.0)
        Fub = st.number_input("Fub — Ultimate strength of bolt material (MPa)", value=800.0, step=10.0)
    with col2:
        phi_shear = st.number_input("Φ (phi) — resistance factor for bolt shear", value=0.75, format="%.3f")
        phi_tension = st.number_input("Φ (phi) — resistance factor for tension/rupture", value=0.9, format="%.3f")
        phi_bearing = st.number_input("Φ (phi) — resistance factor for bearing", value=0.9, format="%.3f")

    st.subheader("Bolt & plate geometry")
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        bolt_d_nom = st.number_input("Bolt nominal diameter (mm)", value=20.0)
        bolt_type = st.text_input("Bolt spec (e.g., A325/A490) — for note only", value="A490M")
        n_bolts_rows = st.number_input("Number of bolts in one stagger/row (per half splice)", value=6, step=1)
        shear_planes_per_bolt = st.number_input("Shear planes per bolt (1 for single, 2 for double)", value=2, step=1)
    with bcol2:
        plate_t = st.number_input("Splice plate thickness (mm)", value=10.0)
        hole_d_add = st.number_input("Hole allowance: (nominal hole = d + mm)", value=2.0)
        edge_distance = st.number_input("Edge distance (mm)", value=40.0)
        bolt_spacing = st.number_input("Longitudinal spacing between bolts (mm)", value=60.0)

    st.subheader("Section geometry (connected members)")
    scol1, scol2 = st.columns(2)
    with scol1:
        gross_width = st.number_input("Gross width of connected element (mm)", value=200.0)
        thickness = st.number_input("Thickness of connected element (mm)", value=10.0)
    with scol2:
        n_bolt_rows = st.number_input("Number of bolt rows across section (per half splice)", value=1, step=1)
        n_bolts_total_each_side = st.number_input("Total bolts in one splice half (all rows aggregated)", value=6, step=1)

    st.subheader("Applied loads (design values)")
    lcol1, lcol2 = st.columns(2)
    with lcol1:
        N_axial = st.number_input("Applied axial force (N) — positive for tension", value=0.0, step=100.0)
        V_shear = st.number_input("Applied shear (N)", value=0.0, step=100.0)
    with lcol2:
        M_moment = st.number_input("Applied moment about strong axis (N·mm)", value=0.0, step=1000.0)
        eccentricity = st.number_input("Eccentricity for axial transfer (mm)", value=0.0, step=1.0)

    if st.button("Run splice checks"):
        st.subheader("Computed geometric values")
        d_hole = bolt_d_nom + hole_d_add
        A_gross = gross_width * thickness
        A_net = (gross_width - (d_hole * n_bolt_rows)) * thickness
        A_bolt_shank = math.pi * (bolt_d_nom ** 2) / 4.0  # mm^2
        n_bolts_each = n_bolts_total_each_side
        st.write(f"- Nominal bolt hole diameter (d0): {d_hole:.1f} mm")
        st.write(f"- Gross area, A_g = {A_gross:.1f} mm²")
        st.write(f"- Net area (simple deduction), A_n = {A_net:.1f} mm²")
        st.write(f"- Bolt cross-sectional area (shank), A_b = {A_bolt_shank:.2f} mm²")
        st.write(f"- Bolts per splice half: {n_bolts_each}, shear planes per bolt: {shear_planes_per_bolt}")

        st.subheader("Bolt shear capacity (nominal & design)")
        # Nominal shear per shear plane: use tensile strength of bolt (approx Fub) * A_b * 0.6 (common AISC simplification)
        # Let user override phi; we used phi_shear already.
        Vn_per_plane = 0.6 * Fub * A_bolt_shank  # N·mm units mismatch (we treat MPa*mm^2 -> N)
        # Convert MPa*mm^2 to N: 1 MPa = 1 N/mm^2, so value is in N
        Vn_per_plane_N = Vn_per_plane
        Vn_per_bolt = Vn_per_plane_N * shear_planes_per_bolt
        phiV = phi_shear
        Vr_per_bolt = phiV * Vn_per_bolt
        total_Vr = Vr_per_bolt * n_bolts_each
        st.write(f"Nominal shear per shear plane, Vn_plane = 0.6 * Fub * A_b = {Vn_per_plane_N:.1f} N")
        st.write(f"Nominal shear per bolt (all planes): Vn_bolt = {Vn_per_bolt:.1f} N")
        st.write(f"Design shear per bolt (ΦVn): {Vr_per_bolt:.1f} N")
        st.write(f"Total design shear resistance (all bolts on one half): {total_Vr:.1f} N")
        st.write(f"Applied shear V = {V_shear:.1f} N")
        if total_Vr >= V_shear:
            st.success("Bolt shear capacity OK (resists applied shear).")
        else:
            st.error("Bolt shear capacity INSUFFICIENT.")

        st.subheader("Bearing capacity at bolt holes (connected element)")
        # Simplified AISC-style bearing: Rn = k * t * d * Fu
        # Use k = 2.4 for threads excluded? Many guides use 2.4/2.9 depending on condition; we'll allow k default.
        k_default = 2.4
        k = st.number_input("Bearing k-factor (use 2.4~2.9 depending on condition)", value=k_default)
        Rn_bearing_per_bolt = k * thickness * d_hole * Fu  # N (MPa*mm^2 -> N)
        R_design_bearing = phi_bearing * Rn_bearing_per_bolt
        total_bearing = R_design_bearing * n_bolts_each
        st.write(f"Nominal bearing per bolt Rn ≈ k * t * d * Fu = {Rn_bearing_per_bolt:.1f} N")
        st.write(f"Design bearing per bolt ΦRn = {R_design_bearing:.1f} N")
        st.write(f"Total design bearing (all bolts): {total_bearing:.1f} N")
        if total_bearing >= V_shear:
            st.success("Bearing capacity OK.")
        else:
            st.warning("Bearing capacity may be insufficient vs applied shear.")

        st.subheader("Tension / Net area check (for axial transfer)")
        # Nominal tension capacity using net area and Fu (rupture) and gross area and Fy (yield)
        Pn_yield = Fy * A_gross  # N (MPa*mm2 -> N)
        Pn_rupture = Fu * A_net
        # apply phi for tension rupture
        phiT = phi_tension
        R_tension = phiT * min(Pn_yield, Pn_rupture)
        st.write(f"Gross capacity (yield) Pn_yield = Fy * A_g = {Pn_yield:.1f} N")
        st.write(f"Net rupture capacity Pn_rupture = Fu * A_n = {Pn_rupture:.1f} N")
        st.write(f"Design tension resistance ΦPn = {R_tension:.1f} N")
        st.write(f"Applied axial N = {N_axial:.1f} N")
        if R_tension >= N_axial:
            st.success("Tension capacity OK.")
        else:
            st.error("Tension capacity INSUFFICIENT.")

        st.subheader("Block-shear check (simplified)")
        # Simple block shear: Rn = 0.6*Fy*(A_gv) + Fu*(A_nt) [this is a simplified form]
        # User must provide assumed shear path and tension path areas; we estimate from geometry:
        A_gv = thickness * (edge_distance)  # gross shear area (mm2) - approximate
        A_nt = thickness * (bolt_spacing * n_bolt_rows)  # net tensile area along tension path - approx
        Rn_block = 0.6 * Fy * A_gv + Fu * A_nt
        R_design_block = phi_tension * Rn_block
        st.write("**(Approximate)** block shear areas used:")
        st.write(f"- A_gv (gross shear area) ≈ t * edge_distance = {A_gv:.1f} mm²")
        st.write(f"- A_nt (net tension area) ≈ t * (bolt_spacing * rows) = {A_nt:.1f} mm²")
        st.write(f"Nominal block-shear Rn ≈ 0.6*Fy*A_gv + Fu*A_nt = {Rn_block:.1f} N")
        st.write(f"Design block-shear ΦRn = {R_design_block:.1f} N")
        if R_design_block >= N_axial:
            st.success("Block-shear capacity OK for axial transfer.")
        else:
            st.warning("Block-shear may control; check detailed geometry per code.")

        st.subheader("Moment transfer (rough check)")
        if M_moment != 0.0 and n_bolts_each > 0:
            # compute axial from eccentricity due to moment (simple): N_eq = M / e
            if eccentricity == 0:
                st.info("Eccentricity = 0; using axial only. If moment present but no eccentricity, provide eccentricity.")
            else:
                N_from_M = M_moment / eccentricity
                st.write(f"Equivalent axial from moment: N_eq = M / e = {N_from_M:.1f} N")
                combined_N = N_axial + N_from_M
                st.write(f"Combined axial (applied + from moment) = {combined_N:.1f} N")
                if R_tension >= combined_N:
                    st.success("Combined axial+moment check OK (based on net/gross tension check).")
                else:
                    st.error("Combined axial+moment requires stronger splice (increase bolts/plate).")

        st.markdown("---")
        st.markdown(
            r"""
            **Important**
            - This template uses *simplified* forms of AISC/NSCP checks to give a clear, auditable calculation flow.
            - **Verify each result with the relevant NSCP / AISC clause** and consider factors such as bolt slip (for slip-critical connections), threaded shank in shear plane, plate tear-out geometry, and shear-lag for flange splices.
            - Example references: AISC verification examples and NSCP connection guidance.
            """
        )
