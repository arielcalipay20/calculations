# Home.py (Router only - no UI)
# Home.py (Router with debugging)
import streamlit as st
import extra_streamlit_components as stx
import time
from src.functions.sessions_mysql import get_session

st.markdown("""
        <style>
        [data-testid="stSidebarNav"] li:first-child,
        [data-testid="stSidebarNav"] li:last-child {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="NSCP Calculations")

cm = stx.CookieManager()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# DEBUG - Uncomment to see what's happening
# st.write("DEBUG - Session State:", {
#     "logged_in": st.session_state.logged_in,
#     "username": st.session_state.username,
#     "user_id": st.session_state.user_id
# })

# Wait for cookies
all_cookies = cm.cookies
# st.write("DEBUG - Cookies loaded:", all_cookies is not None)

if all_cookies is None:
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h2>🔄 Loading...</h2>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(0.1)
    st.rerun()

# Check session if not logged in
if not st.session_state.logged_in:
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h2>🔄 Loading...</h2>
        </div>
    """, unsafe_allow_html=True)
    token = cm.get("nscp_auth_token")
    # st.write("DEBUG - Token from cookie:", token)
    
    if token:
        sess = get_session(token)
        # st.write("DEBUG - Session from DB:", sess)
        
        if sess:
            st.session_state.logged_in = True
            st.session_state.user_id = sess["user_id"]
            st.session_state.username = sess["username"]
            # st.write("DEBUG - Session restored, will rerun")
            time.sleep(1)  # Give time to see the debug
            st.rerun()

# st.write("DEBUG - About to route...")
# st.write("DEBUG - logged_in:", st.session_state.logged_in)

# Route based on login status
if st.session_state.logged_in:
    # Redirect to last page or default dashboard
    # Hide Home and login from sidebar
    last = st.session_state.get("last_page", "pages/0_Dashboard.py")
    st.write(f"Redirecting to: {last}")
    time.sleep(1)  # See the message before redirect
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h2>🔄 Loading...</h2>
        </div>
    """, unsafe_allow_html=True)
    st.switch_page(last)
    # 
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h2>🔄 Loading...</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <h2>🔄 Loading...</h2>
        </div>
    """, unsafe_allow_html=True)
    # Redirect to login
    # st.write("DEBUG - Redirecting to login")
    time.sleep(1)
    st.switch_page("pages/login.py")