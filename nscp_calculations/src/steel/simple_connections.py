import streamlit as st
from src.steel.simple_connections_tabs import anglecleat, sheartab

def display_tabs():
    st.title("Simple Connections")
    
    tab1, tab2 = st.tabs(["Angle Cleat", "Shear Tab"])
    
    with tab1:
        anglecleat.display()
        
    with tab2:
        sheartab.display()