import streamlit as st


if "y" == 'y':
    from src.components import sidebar
    sidebar.show_sidebar()

st.title('nscp_calculations')
st.write('Structural calculations as per NSCP 2015.')