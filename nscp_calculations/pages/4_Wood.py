import streamlit as st
from src.wood import wood_beam, wood_column, wood_flooring
from src.auth.guard import require_auth, logout_and_redirect

# 🔒 AUTH GUARD — This guarantees the user is logged in
session_state, cm, sess = require_auth("Home.py")

st.title("Wood")

with st.sidebar:
    st.write(f"👤 {session_state.get('username', '')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="Home.py")

tab1, tab2, tab3 = st.tabs(["Wood Beam", "Wood Post", "Wood Flooring"])

with tab1:
    wood_beam.display()
    
with tab2:
    wood_column.display()
    
with tab3:
    wood_flooring.display()