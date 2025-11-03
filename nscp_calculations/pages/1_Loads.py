import streamlit as st
from src.loads import dead_load, live_load, wind_load, seismc_load

st.title("Loads Page")

tab1, tab2, tab3, tab4 = st.tabs(["Dead Load", "Live Load", "Wind Load", "Seismic Load"])

with tab1:
    dead_load.display()

with tab2:
    live_load.display()

with tab3:
    wind_load.display_tabs()

with tab4:
    seismc_load.display()
