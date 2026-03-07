import streamlit as st
from utils.data_utils import get_all_data

st.set_page_config(
    page_title="US International Flight Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        /* Replace the text of the first link in the sidebar */
        [data-testid="stSidebarNav"] ul li:first-child a span {
            visibility: hidden;
        }
        [data-testid="stSidebarNav"] ul li:first-child a span::after {
            content: "Homepage";
            visibility: visible;
            display: block;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("US International Air Travel Dashboard (1990-2025)")

st.markdown("""
### Welcome to the US-International Flight Trends Dashboard/Project
""")