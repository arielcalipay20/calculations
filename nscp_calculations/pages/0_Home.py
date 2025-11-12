import streamlit as st
from src.auth.guard import require_auth, logout_and_redirect

# (optional) if you want unique hydration flags per page, set a key:
st.session_state["_current_page_key"] = "home"

st.title("Home")

# Gate the page
session_state, cm, sess = require_auth(redirect_to="_app.py")

with st.sidebar:
    st.write(f"👤 {session_state.get('username','')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="_app.py")

st.write("Your home content here...")
