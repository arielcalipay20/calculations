import streamlit as st
from src.masonry import masonry_design

# Page Configuration
st.set_page_config(layout="wide")

st.title("Masonry")

(tab1,) = st.tabs(["Masonry Design"])

with tab1:
    masonry_design.display()