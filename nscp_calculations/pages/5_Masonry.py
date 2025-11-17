import streamlit as st
from src.masonry import masonry_design
from src.auth.guard import require_auth, logout_and_redirect

st.session_state["last_page"] = "pages/5_Masonry.py"

# 🔒 AUTH GUARD — This guarantees the user is logged in
session_state, cm, sess = require_auth("Home.py")
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] li:first-child,
    [data-testid="stSidebarNav"] li:last-child {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Masonry")

with st.sidebar:
    st.write(f"### 👤 {session_state.get('username', '')}")
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        logout_and_redirect(cm, redirect_to="Home.py")
        
(tab1,) = st.tabs(["Masonry Design"])

with tab1:
    masonry_design.display()