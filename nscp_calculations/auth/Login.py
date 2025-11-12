# auth/Login.py
import streamlit as st
from src.functions.user_function import register_user, login_user

st.set_page_config(layout="centered")

def show_register():
    st.subheader("📝 Create a New Account")

    # Unique keys to avoid collisions anywhere else in the app
    with st.form("register_form"):
        username = st.text_input("Username", key="register_username_input")
        password = st.text_input("Password", type="password", key="register_password_input")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_input")
        submitted = st.form_submit_button("Register")

    if submitted:
        if not username or not password or not confirm_password:
            st.warning("Please fill in all fields!")
        elif password != confirm_password:
            st.warning("Passwords do not match!")
        else:
            if register_user(username, password):
                st.success("User registered successfully! You can now login.")
            else:
                st.error("Username already exists!")

def show_login():
    st.subheader("🔐 Login to Your Account")

    # Use a form to avoid partial re-renders causing duplicates
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username_input")
        password = st.text_input("Password", type="password", key="login_password_input")
        submitted = st.form_submit_button("Login")

    if submitted:
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            # No sleep, no switch_page here. Let app.py decide and redirect.
            st.rerun()
        else:
            st.error("Incorrect Username or Password")
