import streamlit as st
from src.loads import dead_load, live_load, wind_load, seismc_load
from src.calculations.simple_maths import add, multiply

# Page configuration
st.set_page_config(layout="wide")

st.markdown("""
<style>
  [data-testid="stSidebarNav"] ul li:first-child { display: none; }
</style>
""", unsafe_allow_html=True)
# Guard: if not logged in, bounce back to the main controller
if not st.session_state.get("logged_in", False):
    st.switch_page("_app.py")   # works ONLY if you launch with: streamlit run app.py
    st.stop()
    
with st.sidebar:
    st.write(f"👤  {st.session_state.get('username','')}")
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("_app.py")
        st.stop()

st.title("Loads Page")

# --- INPUT SECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    dead_load_input = st.number_input("Dead Load (kN/m²)", min_value=0.0, step=0.1, value=5.0)

with col2:
    live_load_input = st.number_input("Live Load (kN/m²)", min_value=0.0, step=0.1, value=2.0)

with col3:
    wind_load_input = st.number_input("Wind Load (kN/m²)", min_value=0.0, step=0.1, value=1.0)

# --- LOAD FACTORS (for ultimate limit state design, example factors) ---
st.markdown("### Load Combination Factors")
col4, col5, col6 = st.columns(3)

with col4:
    dead_factor_input = st.number_input("Dead Load Factor", min_value=0.0, step=0.1, value=1.2)

with col5:
    live_factor_input = st.number_input("Live Load Factor", min_value=0.0, step=0.1, value=1.6)

with col6:
    wind_factor_input = st.number_input("Wind Load Factor", min_value=0.0, step=0.1, value=1.0)

# --- CALCULATION ---
if st.button("Calculate Total Load"):
    total_load = add(multiply(dead_load_input, dead_factor_input), multiply(live_load_input, live_factor_input), multiply(wind_load_input, wind_factor_input))

    st.success(f"**Total Design Load = {total_load:.2f} kN/m²**")

    st.write("---")
    st.write("#### Calculation Details:")
    st.write(f"Dead Load: {dead_load_input:.2f} × {dead_factor_input:.2f} = {dead_load_input * dead_factor_input:.2f}")
    st.write(f"Live Load: {live_load_input:.2f} × {live_factor_input:.2f} = {live_load_input * live_factor_input:.2f}")
    st.write(f"Wind Load: {wind_load_input:.2f} × {wind_factor_input:.2f} = {wind_load_input * wind_factor_input:.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["Dead Load", "Live Load", "Wind Load", "Seismic Load"])

with tab1:
    dead_load.display()

with tab2:
    live_load.display()

with tab3:
    wind_load.display_tabs()

with tab4:
    seismc_load.display()
