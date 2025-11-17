# pages/login.py
import streamlit as st
import extra_streamlit_components as stx
import time

from src.functions.user_function import login_user
from src.functions.sessions_mysql import create_session
from auth.Login import show_register

st.set_page_config(layout="wide", page_title="Login - NSCP")

# Initialize cookie manager
cm = stx.CookieManager()

# If already logged in, redirect to home (which will then route to dashboard)
if st.session_state.get("logged_in", False):
    st.switch_page("Home.py")

# Hide sidebar navigation
st.markdown("<style>[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

st.title("🔐 NSCP Login")

# Sidebar choice for Login or Register
choice = st.sidebar.selectbox("Account", ["Login", "Register"], key="auth_menu")

if choice == "Register":
    show_register()

else:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = login_user(u, p)
        
        if user:
            # Update session state
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.user_id = user["id"]
            st.session_state.initial_load = True

            # Create DB session + cookie
            tok = create_session(user_id=user["id"])
            cm.set("nscp_auth_token", tok, max_age=60 * 60 * 24 * 7, path="/")
            
            st.success(f"Welcome back, {user['username']}!")
            time.sleep(0.5)
            
            # Redirect to Home (which will route to last_page or dashboard)
            st.switch_page("Home.py")

        else:
            st.error("❌ Invalid username or password")

# Optional: Add some styling or additional info
st.markdown("---")
st.info("💡 Don't have an account? Select 'Register' from the sidebar.")