import textwrap

import streamlit as st
import altair as alt
from utils.data_utils import get_all_data

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f2f2f2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    /* Target the main container */
    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Optional: Center your headers and subheaders for a cleaner look */
    h1, h2, h3 {
        text-align: left;
    }
    
    /* Center the chart container itself */
    .stVegaLiteChart {
        display: flex;
        justify-content: left;
    }
    </style>
    """, unsafe_allow_html=True)


st.title("Sources")

st.markdown("**Datasets**")
st.markdown("- [T-100 Flight Segment Data](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FJE)")
st.markdown("- [Country-Continent Mapping](https://github.com/dbouquin/IS_608/blob/master/NanosatDB_munging/Countries-Continents.csv)")
st.markdown("- [World Bank Income Data](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)")
st.markdown("- [Vega US Map Data](https://github.com/vega/vega/pulse)")
st.markdown("- [US Airport GeoJSON](https://github.com/blackmad/neighborhoods/blob/master/united-states-international-airports.geojson)")

st.markdown("**Background Research**")
st.markdown("- [Mexico Pandemic Travel Trends](https://www.businessinsider.com/why-americans-have-been-escaping-to-mexico-during-the-pandemic-2021-2)")
st.markdown("- [Evolution of Airline Hubs](https://www.reuters.com/article/business/former-hub-airports-find-new-life-after-downsizing-idUSKBN0F80B3/)")
