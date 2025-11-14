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

cm = stx.CookieManager()

# --- Load token instantly ---
token = cm.get("nscp_auth_token")
st.write("Stored cookies:", cm.cookies)
st.write("Fetched token:", token)

# --- Restore login from DB session ---
if token and not st.session_state.logged_in:
    sess = get_session(token)
    if sess:
        st.session_state.logged_in = True
        st.session_state.user_id = sess["user_id"]
        st.session_state.username = sess["username"]

# ======================================================
#                 IF LOGGED IN → SHOW HOME
# ======================================================
if st.session_state.logged_in:

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
            # cm.set("nscp_auth_token", "", max_age=0, path="/")
            # st.session_state.clear()
            # st.session_state["logged_in"] = False
            # st.rerun()
            
            # Delete cookie 
            cm.delete("nscp_auth_token") 
            # cm.save() 
            st.session_state.clear() 
            st.session_state.update({ "logged_in": False, }) 
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
