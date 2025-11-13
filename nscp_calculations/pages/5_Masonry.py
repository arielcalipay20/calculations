import streamlit as st
from src.masonry import masonry_design
from src.auth.guard import require_auth, logout_and_redirect

# 🔒 AUTH GUARD — This guarantees the user is logged in
session_state, cm, sess = require_auth("Home.py")

st.title("Masonry")

with st.sidebar:
    st.write(f"👤 {session_state.get('username', '')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="Home.py")
        
(tab1,) = st.tabs(["Masonry Design"])

with tab1:
    masonry_design.display()