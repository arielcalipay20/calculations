# Home.py
import streamlit as st
import extra_streamlit_components as stx
import time

from src.functions.user_function import login_user
from src.functions.sessions_mysql import create_session, get_session, destroy_session
from auth.Login import show_register

st.set_page_config(layout="wide", page_title="NSCP Calculations")

# ---- Initialize Cookie Manager FIRST ----
cm = stx.CookieManager()

# ---- Initialize session state defaults ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# --- WAIT FOR COOKIES TO LOAD (prevents flickering) ---
all_cookies = cm.cookies

# Debug: Check what we have
# st.write("DEBUG - Cookies loaded:", all_cookies is not None)
# st.write("DEBUG - All cookies:", all_cookies)
# st.write("DEBUG - Current logged_in state:", st.session_state.logged_in)

# If cookies aren't loaded yet, wait briefly
if all_cookies is None:
    st.write("DEBUG - Waiting for cookies...")
    time.sleep(0.1)
    st.rerun()

# --- CHECK TOKEN AND RESTORE SESSION (if not already logged in) ---
if not st.session_state.logged_in:
    token = cm.get("nscp_auth_token")
    # st.write("DEBUG - Token found:", token)
    
    if token:
        sess = get_session(token)
        # st.write("DEBUG - Session from DB:", sess)
        if sess:
            st.session_state.logged_in = True
            st.session_state.user_id = sess["user_id"]
            st.session_state.username = sess["username"]
            # st.write("DEBUG - Session restored!")

# ======================================================
#                 IF LOGGED IN → SHOW HOME
# ======================================================
if st.session_state.logged_in:

    st.title("🏠 Home Dashboard")
    st.write(f"Welcome, **{st.session_state.username}**!")

    with st.sidebar:
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout"):
            # Get token before destroying
            token = cm.get("nscp_auth_token")
            
            # Destroy DB session
            if token:
                destroy_session(token)

            # Delete cookie
            cm.delete("nscp_auth_token")
            
            # Clear session state
            st.session_state.clear()
            
            st.rerun()

    st.stop()

# ======================================================
#              NOT LOGGED IN → SHOW AUTH
# ======================================================

st.markdown("<style>[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

st.title("🔐 NSCP Login")

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
            # Update session
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.user_id = user["id"]

            # Create DB session + cookie
            tok = create_session(user_id=user["id"])
            cm.set("nscp_auth_token", tok, max_age=60 * 60 * 24 * 7, path="/")
            cm.save() 
            st.rerun()

        else:
            st.error("Invalid username or password")