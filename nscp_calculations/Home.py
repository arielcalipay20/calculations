# Home.py
import streamlit as st
import extra_streamlit_components as stx

from src.functions.user_function import login_user
from src.functions.sessions_mysql import create_session, get_session, destroy_session
from auth.Login import show_register

st.set_page_config(layout="wide", page_title="NSCP Calculations")

# ---- Initialize defaults ----
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("cookie_checked", False)
st.session_state.setdefault("session_checked", False)

cm = stx.CookieManager()

if not st.session_state.get("cookie_checked", False):
    st.session_state.cookie_checked = True
    st.write("Loading cookies...")
    st.stop()  # wait until cookies are ready

token = cm.get("nscp_auth_token")

# Testing Purpose
# st.write(token)
# sess = get_session("0qTWUGUlWKGdMEFcE7KujnaZmC34OT1uhoKpr0dq3Ao")
# if sess:
#     st.write("✅ Session found!")
#     st.json(sess)
# else:
#     st.write("❌ Session NOT found or expired")

if token and not st.session_state.get("session_checked", False):
    sess = get_session(token)
    if sess:
        st.session_state.logged_in = True
        st.session_state.user_id = sess["user_id"]
        st.session_state.username = sess["username"]
    st.session_state.session_checked = True

# --- Prevent flicker / infinite loop ---
if not st.session_state.cookie_checked:
    st.session_state.cookie_checked = True
    # Only rerun once to allow cookies to load
    st.rerun()

# --- Restore from DB session (only once) ---
if token and not st.session_state.logged_in and not st.session_state.session_checked:
    sess = get_session(token)
    st.session_state.session_checked = True  # Avoid repeated DB lookups
    if sess:
        st.session_state.logged_in = True
        st.session_state.user_id = sess["user_id"]
        st.session_state.username = sess["username"]

# ======================================================
#                 IF LOGGED IN → SHOW HOME
# ======================================================
if st.session_state.logged_in:

    # --------------- HOME CONTENT ----------------
    st.title("🏠 Home Dashboard")
    st.write(f"Welcome, **{st.session_state.username}**!")

    with st.sidebar:
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout"):
            # Destroy DB session
            token = cm.get("nscp_auth_token")
            if token:
                destroy_session(token)

            # Delete cookie
            try:
                cm.delete("nscp_auth_token", path="/")
            except KeyError:
                pass

            # Clear Streamlit session safely
            cookie_checked = st.session_state.get("cookie_checked", True)
            st.session_state.clear()
            st.session_state.update({
                "logged_in": False,
                "cookie_checked": cookie_checked,
                "session_checked": False
            })

            st.rerun()

    st.write("Your Home content goes here...")
    st.write("Charts, tables, tools, etc.")
    st.stop()

# ======================================================
#              NOT LOGGED IN → SHOW AUTH
# ======================================================

# Hide sidebar navigation until login
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
            # Update session_state
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.user_id = user["id"]

            # Create DB-backed session + cookie
            tok = create_session(user_id=user["id"])
            cm.set("nscp_auth_token", tok, max_age=60 * 60 * 24 * 7, path="/")

            st.rerun()
        else:
            st.error("Invalid username or password")
