import streamlit as st
from src.concrete import rc_anchorage, rc_beam, rc_beamcolumnjoint, rc_column, rc_footing, rc_onewayslab, rc_pilecap, rc_twowayslab, rc_walls
from src.auth.guard import require_auth, logout_and_redirect

# 🔒 AUTH GUARD — This guarantees the user is logged in
session_state, cm, sess = require_auth("Home.py")

st.title("Structural Concrete")

with st.sidebar:
    st.write(f"👤 {session_state.get('username', '')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="Home.py")
        
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