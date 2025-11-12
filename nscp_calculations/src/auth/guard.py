# src/auth/guard.py
import streamlit as st
import extra_streamlit_components as stx
from typing import Optional, Tuple, Dict, Any
from src.functions.sessions_mysql import get_session, destroy_session

# Optional UI helper
def hide_controller_entry():
    st.markdown(
        "<style>[data-testid='stSidebarNav'] ul li:first-child{display:none;}</style>",
        unsafe_allow_html=True,
    )

def require_auth(redirect_to: str = "_app.py") -> Tuple[st.session_state.__class__, stx.CookieManager, Optional[Dict[str, Any]]]:
    """
    Ensures the user is authenticated.
    - Trusts in-session state first (post-login hop).
    - Falls back to cookie + DB session (reloads/new tabs).
    - Performs a one-time rerun to hydrate cookies if needed.
    - Redirects to redirect_to if not authenticated.

    Returns:
        (session_state, cookie_manager, session_row_or_none)
        - session_row_or_none is the row from DB (token, user_id, username, ...)
    """
    hide_controller_entry()  # optional; remove if you don't want this globally

    cm = stx.CookieManager()
    # page-level hydration flag (unique per page to avoid cross-page interference)
    flag_key = "__cookie_checked__" + st.session_state.get("_current_page_key", "default")
    st.session_state.setdefault(flag_key, False)

    # 1) Trust in-session state first
    if st.session_state.get("logged_in", False):
        return st.session_state, cm, None

    # 2) Fallback to cookie + DB for reloads/new tabs
    token = cm.get("nscp_auth_token")

    # One-time hydration: CookieManager may return "" or None on the very first render
    if (not token) and (not st.session_state[flag_key]):
        st.session_state[flag_key] = True
        st.rerun()
        st.stop()

    sess = get_session(token) if token else None
    if not sess:
        # Not authenticated -> bounce to controller
        st.switch_page(redirect_to)
        st.stop()

    # 3) Restore Streamlit state from DB session
    st.session_state.logged_in  = True
    st.session_state.user_id    = sess["user_id"]
    st.session_state.username   = sess["username"]
    return st.session_state, cm, sess

def logout_and_redirect(cm: stx.CookieManager, redirect_to: str = "_app.py"):
    """Clear both server- and client-side session, then redirect."""
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
