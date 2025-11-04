import streamlit as st
from src.loads.wind import wind_directional, wind_envelope, wind_others

def display_tabs():
    st.title("Wind Load")
    
    tab1, tab2, tab3 = st.tabs(["Direction Procedure", "Envelope Procedure", "Other Wind"])
    
    with tab1:
        wind_directional.display()
        
    with tab2:
        wind_envelope.display()
        
    with tab3:
        wind_others.display()
