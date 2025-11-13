# src/auth/guard.py
import streamlit as st
import extra_streamlit_components as stx
from typing import Optional, Tuple, Dict, Any
from src.functions.sessions_mysql import get_session, destroy_session

def require_auth(
    redirect_to: str = "Home.py",
) -> Tuple[st.session_state.__class__, stx.CookieManager, Optional[Dict[str, Any]]]:
    """
    Simple auth guard for pages/*.
    - If st.session_state.logged_in is True -> allow.
    - Else, try to restore from cookie+DB.
    - If still not authenticated, redirect to app.py.
    """

    cm = stx.CookieManager()

    # 1) Trust current session first (post-login navigation)
    if st.session_state.get("logged_in", False):
        return st.session_state, cm, None

    # 2) Try to restore from cookie + DB (e.g. page opened in new tab)
    token = cm.get("nscp_auth_token")
    sess = get_session(token) if token else None

    if not sess:
        # No valid session → back to main app/login
        st.switch_page(redirect_to)
        st.stop()

    # 3) Restore session state from DB session
    st.session_state.logged_in = True
    st.session_state.user_id = sess["user_id"]
    st.session_state.username = sess["username"]

    return st.session_state, cm, sess


def logout_and_redirect(cm: stx.CookieManager, redirect_to: str = "Home.py"):
    """Clear DB session, cookie, and Streamlit state, then go to app.py."""
    token = cm.get("nscp_auth_token")
    if token:
        try:
            destroy_session(token)
        except Exception:
            pass
        try:
            cm.delete("nscp_auth_token")
        except KeyError:
            pass

    st.session_state.clear()
    st.switch_page(redirect_to)
    st.stop()
