import streamlit as st

st.markdown("""
<style>
  [data-testid="stSidebarNav"] ul li:first-child { display: none; }
</style>
""", unsafe_allow_html=True)

# Guard: if not logged in, bounce back to the main controller
if not st.session_state.get("logged_in", False):
    st.switch_page("_app.py")   # works ONLY if you launch with: streamlit run app.py
    st.stop()
    
with st.sidebar:
    st.write(f"👤  {st.session_state.get('username','')}")
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("_app.py")
        st.stop()
        
st.success("Welcome")
