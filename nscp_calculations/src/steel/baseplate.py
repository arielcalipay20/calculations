import streamlit as st
from src.steel.baseplate_tabs import baseplate_moment, baseplate_pinned

def display_tabs():
    st.title("Base Plate")
    
    tab1, tab2 = st.tabs(["Base Plate Moment", "Base Plate Pinned"])
    
    with tab1:
        baseplate_moment.display()
        
    with tab2:
        baseplate_pinned.display()