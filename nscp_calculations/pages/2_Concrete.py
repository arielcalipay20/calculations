import streamlit as st
from src.concrete import rc_anchorage, rc_beam, rc_beamcolumnjoint, rc_column, rc_footing, rc_onewayslab, rc_pilecap, rc_twowayslab, rc_walls

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

st.title("Structural Concrete")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["RC Anchorage", "RC Beam", "RC Beam Column Joint", "RC Column", "RC Footing", "RC One Way SLab", "RC Pile Cap", "RC Two Way SLab", "RC Walls"]
    )

with tab1:
    rc_anchorage.display()
    
with tab2:
    rc_beam.display()
    
with tab3:
    rc_beamcolumnjoint.display()
    
with tab4:
    rc_column.display()
    
with tab5:
    rc_footing.display()
    
with tab6:
    rc_onewayslab.display()
    
with tab7:
    rc_pilecap.display()
    
with tab8:
    rc_twowayslab.display()
    
with tab9:
    rc_walls.display()