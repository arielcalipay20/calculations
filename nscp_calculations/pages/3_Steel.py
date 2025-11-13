import streamlit as st
from src.steel import baseplate, bracing, moment_connections, simple_connections, ss_beam, ss_column, ss_purlins, ss_tension, steelsplices
from src.auth.guard import require_auth, logout_and_redirect

# 🔒 AUTH GUARD — This guarantees the user is logged in
session_state, cm, sess = require_auth("Home.py")

st.title("Structural Steel")

with st.sidebar:
    st.write(f"👤 {session_state.get('username', '')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="Home.py")
        
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