import streamlit as st
from src.steel.steelsplices_tabs import bolted_splice, welded_splice

def display_tabs():
    st.header("Steel Splices")
    
    tab1, tab2 = st.tabs(["Bolted Splice","Welded Splice"])

    with tab1:
        bolted_splice.display()
        
    with tab2:
        welded_splice.display()