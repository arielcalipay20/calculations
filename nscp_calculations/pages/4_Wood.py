import streamlit as st
from src.wood import wood_beam, wood_column, wood_flooring

# Page Configuration
st.set_page_config(layout="wide")

st.title("Wood")

tab1, tab2, tab3 = st.tabs(["Wood Beam", "Wood Post", "Wood Flooring"])

with tab1:
    wood_beam.display()
    
with tab2:
    wood_column.display()
    
with tab3:
    wood_flooring.display()