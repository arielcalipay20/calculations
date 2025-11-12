# _app.py
import streamlit as st
import extra_streamlit_components as stx

from src.functions.user_function import login_user    # returns {"id","username"} or None
from auth.Login import show_register
from src.functions.sessions_mysql import create_session, get_session

st.set_page_config(layout="wide", page_title="NSCP Calculations")

# (Optional) hide the “app” entry if it shows
st.markdown("<style>[data-testid='stSidebarNav'] ul li:first-child{display:none;}</style>", unsafe_allow_html=True)

# ---- session init (Streamlit only)
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("user_id", None)
st.session_state.setdefault("cookie_checked", False)

cm = stx.CookieManager()

token = cm.get("nscp_auth_token")

# If cookie is not available on the first render, rerun once to hydrate
if not token and not st.session_state.cookie_checked:
    st.session_state.cookie_checked = True
    st.rerun()

# ---- restore from cookie -> DB session
sess = get_session(token) if token else None
if sess and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_id = sess["user_id"]
    st.session_state.username = sess["username"]

# ---- hide built-in pages list until authenticated
if not st.session_state.logged_in:
    st.markdown("<style>[data-testid='stSidebarNav']{display:none;}</style>", unsafe_allow_html=True)

# ---- already authenticated? go to Home
if st.session_state.logged_in:
    st.switch_page("pages/0_Home.py")
    st.stop()

# ------------------ AUTH SURFACE ------------------
choice = st.sidebar.selectbox("Menu", ["Login", "Register"], key="auth_menu")

if choice == "Register":
    show_register()

else:
    st.subheader("🔐 Login to Your Account")
    with st.form("login_form"):
        u = st.text_input("Username", key="login_username_input")
        p = st.text_input("Password", type="password", key="login_password_input")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = login_user(u, p)            # <- must return {"id","username"} on success
        if user:
            # 1) set Streamlit state
            st.session_state.logged_in = True
            st.session_state.user_id = user["id"]
            st.session_state.username = user["username"]

            # 2) issue server-side session + cookie
            tok = create_session(user_id=user["id"], meta={"ua": "streamlit"})
            cm.set("nscp_auth_token", tok, max_age=60*60*24*7, path="/")   # keep flags minimal

            # 3) redirect immediately (no rerun needed)
            st.switch_page("pages/0_Home.py")
            st.stop()
        else:
            st.error("Invalid username or password")
