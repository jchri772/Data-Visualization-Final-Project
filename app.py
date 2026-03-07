import streamlit as st
from utils.data_utils import get_all_data

st.set_page_config(
    page_title="US International Flight Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("DATA 227 Final Project: Analyzing US-International Flight Trends (1990-2025)")

st.write("""For decades, international aviation has served as a significant engine for global connectivity and has acted as a crucial bridge for both economic and cultural exchange. International flights to and from the United States have, with few pauses, steadily increased in both scope and volume, resulting both from increasing globalization and more efficient aircraft. However, this passenger growth has been far from uniform; the vast majority of volume is concentrated within a handful of countries, while most international flights arrive at only a few key U.S. gateway airports. Additionally, there have been significant changes in the makeup of both the primary U.S. international airports and the foreign countries with the most traffic to the U.S. In this project, we use data that tracks the number of passengers traveling on specific routes each month since 1990 and until 2024 to illustrate how the composition of international flight traffic has evolved.""")

st.write("""Please note that throughout this project, we track foreign traffic by the initial foreign airport each passenger travels to and from, and by the final U.S. airport traveled to by each passenger. This means that, for example, a passenger traveling from Chicago to Rome connecting in both New York and London will count as flying internationally between New York and London, the same as a passenger originating in New York and terminating in London. We analyze the data this way in order to track the volume of individual flights by airlines and how they change over time. Thus, we do not track the ultimate destination or country of each passenger, which would require the use of a separate dataset.""")

st.write("""Why is this important and page description""")

st.write("""The primary dataset we use is the T-100 International Segment dataset, released by the United States Bureau of Transportation Statistics, which contains international nonstop flight segment data. An individual observation in the dataset represents one month of international flights operated to or from the United States by a specific airline on a specified aircraft type. The columns include information on the number of flights and passengers for each observation, the flight distance, and the foreign country, along with the origin airport, destination airport, and airline. We augment this dataset with World Bank data on the annual GDP per capita for each foreign country to compare passenger volume with national income. We also include a dataset that labels each country by continent to perform analysis at the continent level. Additionally, we use GeoJSON maps of the United States (from the vega datasets) and of airport locations (downloaded from a user from GitHub but augmented with additional international airports not shown in the dataset) to visualize the number of passengers flown from U.S. international gateway airports. For the purposes of our analysis, we aggregate the data by foreign country and the year each flight was flown.""")


