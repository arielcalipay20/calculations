import streamlit as st
from src.steel import baseplate, bracing, moment_connections, simple_connections, ss_beam, ss_column, ss_purlins, ss_tension, steelsplices

# Page Configuration
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

st.title("Structural Steel")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["Baseplate", "Bracing", "Moment Connections", "Simple Connections", "SS Beam", "SS Column", "SS Purlins", "SS Tension", "Steel Splices"]
    )

with tab1: 
    baseplate.display_tabs()
    
with tab2:
    bracing.display_tabs()

with tab3:
    moment_connections.display_tabs()
    
with tab4:
    simple_connections.display_tabs()
    
with tab5:
    ss_beam.display()

with tab6:
    ss_column.display()
    
with tab7:
    ss_purlins.display()
    
with tab8:
    ss_tension.display()
    
with tab9:
    steelsplices.display_tabs()