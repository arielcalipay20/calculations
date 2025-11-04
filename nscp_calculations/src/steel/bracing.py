import streamlit as st
from src.steel.bracing_tabs import concretic_brace, eccentric_brace

def display_tabs():
    st.title("Bracing")
    
    tab1, tab2 = st.tabs(["Concretic Brace", "Eccentric Brace"])
    
    with tab1:
        concretic_brace.display()
        
    with tab2:
        eccentric_brace.display()



