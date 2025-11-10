import streamlit as st
from src.steel.bracing_tabs import concentric_brace, eccentric_brace

def display_tabs():
    st.header("Bracing Connections")
    
    tab1, tab2 = st.tabs(["Concentric Brace", "Eccentric Brace"])
    
    with tab1:
        concentric_brace.display()
        
    with tab2:
        eccentric_brace.display()



