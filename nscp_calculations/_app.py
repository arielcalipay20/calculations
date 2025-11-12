# _app.py
import streamlit as st
from auth.Login import show_login, show_register

# ---- Session Initialization ----
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")

# ---- Hide built-in pages navigation before login ----
if not st.session_state.logged_in:
    st.markdown(
        "<style>[data-testid='stSidebarNav']{display:none;}</style>",
        unsafe_allow_html=True,
    )

# ---- Controller / Router ----
if st.session_state.logged_in:
    # Once logged in, go to your main page
    st.switch_page("pages/0_Home.py")   # path is relative to THIS file
    st.stop()
else:
    # Show exactly ONE auth surface to avoid duplicates
    choice = st.sidebar.selectbox("Menu", ["Login", "Register"], key="auth_menu")
    if choice == "Login":
        show_login()
    else:
        show_register()
    st.stop()
    
