import streamlit as st
from src.steel.moment_connections_tabs import bolted, welded

def display_tabs():
    st.header("Moment Connections")
    
    tab1, tab2 = st.tabs(["Bolted", "Welded"])
    
    with tab1:
        bolted.display()
        
    with tab2:
        welded.display()