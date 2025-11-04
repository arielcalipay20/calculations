import streamlit as st
from src.steel import baseplate, bracing, moment_connections, simple_connections, ss_beam, ss_column, ss_purlins, ss_tension, steelsplices

# Page Configuration
st.set_page_config(layout="wide")

st.title("Steel")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    ["Baseplate", "Bracing", "Moment Connections", "Single Connections", "SS Beam", "SS Column", "SS Purlins", "SS Tension", "Steel Splices"]
    )

with tab1: 
    baseplate.display_tabs()
    
with tab2:
    bracing.display_tabs()

with tab3:
    moment_connections.display_tabs()
    
with tab4:
    simple_connections.display_tabs()
    
with tab5:
    ss_beam.display()

with tab6:
    ss_column.display()
    
with tab7:
    ss_purlins.display()
    
with tab8:
    ss_tension.display()
    
with tab9:
    steelsplices.display_tabs()