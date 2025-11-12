import streamlit as st
from src.wood import wood_beam, wood_column, wood_flooring
from src.auth.guard import require_auth, logout_and_redirect

# (optional) if you want unique hydration flags per page, set a key:
st.session_state["_current_page_key"] = "wood"

st.title("Wood")

# Gate the page
session_state, cm, sess = require_auth(redirect_to="_app.py")

with st.sidebar:
    st.write(f"👤 {session_state.get('username','')}")
    if st.button("Logout"):
        logout_and_redirect(cm, redirect_to="_app.py")

tab1, tab2, tab3 = st.tabs(["Wood Beam", "Wood Post", "Wood Flooring"])

with tab1:
    wood_beam.display()
    
with tab2:
    wood_column.display()
    
with tab3:
    wood_flooring.display()