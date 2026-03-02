import streamlit as st
from utils.data_utils import get_all_data

st.set_page_config(
    page_title="US International Flight Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("US International Air Travel Dashboard (1990-2025)")

st.markdown("""
### Welcome to the US-International Flight Trends Dashboard/Project
""")