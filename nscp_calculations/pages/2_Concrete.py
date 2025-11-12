import streamlit as st
from src.concrete import rc_anchorage, rc_beam, rc_beamcolumnjoint, rc_column, rc_footing, rc_onewayslab, rc_pilecap, rc_twowayslab, rc_walls
from src.auth.guard import require_auth, logout_and_redirect

# (optional) if you want unique hydration flags per page, set a key:
st.session_state["_current_page_key"] = "concrete"

st.title("Structural Concrete")

# Gate the page
session_state, cm, sess = require_auth(redirect_to="_app.py")

with st.sidebar:
    st.write(f"👤 {session_state.get('username','')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="_app.py")

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