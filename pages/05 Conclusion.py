import streamlit as st
import base64

st.markdown(
    """
    <style>
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("background.jpg")

st.title("Conclusion")

st.markdown("---")

st.write("""
This project examined how international passenger traffic between the United States and the rest of the world has evolved over the past three decades using the Bureau of Transportation Statistics T-100 International Segment dataset. Across the visualizations, several consistent patterns emerge. First, international aviation has expanded substantially since 1990, reflecting broader trends in globalization, rising incomes, and improvements in aircraft technology. At the same time, this growth has been highly uneven. Passenger traffic is heavily concentrated among a relatively small number of foreign countries and is routed through a limited number of major U.S. gateway airports. This concentration highlights the importance of large hub airports and dominant travel markets in shaping the structure of global air transportation networks.

The analysis also shows that the composition of international traffic has changed meaningfully over time. Some regions and countries have become increasingly integrated into the U.S. aviation network, while others have remained relatively marginal in terms of passenger volume. These shifts likely reflect broader economic and demographic dynamics, including migration patterns, tourism demand, and economic growth in emerging markets. The airport-level analysis similarly illustrates how airline network strategies and regional economic changes have influenced which U.S. airports serve as primary international gateways.

In addition, the project demonstrates how major geopolitical or global disruptions can significantly affect international passenger flows. Events such as the September 11 attacks and the COVID-19 pandemic produced sharp declines in international travel, though the magnitude and speed of recovery varied across countries and markets. These differences suggest that international aviation systems are both globally interconnected and locally sensitive to economic conditions, policy responses, and travel demand.

While this project provides a broad overview of long-term trends in U.S. international aviation, several extensions could further deepen the analysis. Future work could incorporate additional datasets, such as airline route networks, ticket pricing data, or tourism statistics, to better understand the drivers of passenger demand. More detailed route-level analysis could also reveal how airline strategies and hub-and-spoke network structures shape global connectivity. Finally, expanding the analysis to include cargo traffic or comparing U.S. patterns with those of other major aviation markets could provide additional insight into how international transportation networks evolve over time.

Together, these findings highlight how international aviation reflects broader economic integration and global mobility patterns. By analyzing passenger flows across countries, airports, and time, the project illustrates how transportation networks both shape and respond to the forces of globalization.
""")
