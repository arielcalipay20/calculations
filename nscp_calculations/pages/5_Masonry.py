import streamlit as st
from src.masonry import masonry_design

# Page Configuration
st.set_page_config(layout="wide")

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

st.title("Masonry")

(tab1,) = st.tabs(["Masonry Design"])

with tab1:
    masonry_design.display()