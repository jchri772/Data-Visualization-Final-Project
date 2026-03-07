import streamlit as st
import altair as alt
import pandas as pd
from utils.data_utils import get_all_data

st.set_page_config(layout="wide")

st.title("Special-case airports: irregular post-COVID recovery patterns")

st.write(
    "This section isolates four U.S. gateway airports with unusually weak or irregular post-COVID "
    "recovery patterns: Cincinnati (CVG), Pittsburgh (PIT), Memphis (MEM), and St. Louis (STL). "
    "These airports are analytically important because they differ from major coastal gateways and "
    "also from newer growth airports such as Austin or Nashville. Examining their passenger trends "
    "from 2019 through 2024 helps show that post-pandemic recovery in international air travel has "
    "not been uniform across the U.S. airport network."
)

st.write(
    "In particular, these airports help illustrate how international connectivity can erode when an "
    "airport loses hub status, sees reduced carrier commitment, or occupies a weaker position in the "
    "national aviation system. Their trajectories suggest that recovery after COVID was shaped not only "
    "by the return of demand, but also by longer-run structural changes in airline networks."
)


def render_special_case_airports():
    pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()

    alt.data_transformers.disable_max_rows()

    special_airports = ["CVG", "PIT", "MEM", "STL"]

    airport_labels = {
        "CVG": "CVG (Cincinnati)",
        "PIT": "PIT (Pittsburgh)",
        "MEM": "MEM (Memphis)",
        "STL": "STL (St. Louis)"
    }

    special_df = pax_by_airport.copy()
    special_df.columns = [c.strip() for c in special_df.columns]

    special_df = special_df[
        (special_df["US_AIRPORT"].isin(special_airports)) &
        (special_df["YEAR"].between(2019, 2024))
    ].copy()

    special_df = (
        special_df.groupby(["YEAR", "US_AIRPORT"], as_index=False)
        .agg(passengers=("PASSENGERS", "sum"))
    )

    special_df["airport_label"] = special_df["US_AIRPORT"].map(airport_labels)

    line_chart = (
        alt.Chart(special_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "YEAR:O",
                title="Year"
            ),
            y=alt.Y(
                "passengers:Q",
                title="International passengers"
            ),
            color=alt.Color(
                "airport_label:N",
                title="Airport"
            ),
            tooltip=[
                alt.Tooltip("YEAR:O", title="Year"),
                alt.Tooltip("airport_label:N", title="Airport"),
                alt.Tooltip("passengers:Q", title="Passengers", format=",.0f")
            ]
        )
        .properties(
            width=850,
            height=450
        )
    )

    st.altair_chart(line_chart, use_container_width=False)

    st.markdown(
        "<p style='text-align: center; font-size: 12px;'><i>"
        "The figure above compares international passenger volumes at four U.S. airports with irregular "
        "post-COVID recovery patterns between 2019 and 2024. Unlike major international gateways that "
        "rebounded more strongly, Cincinnati, Pittsburgh, Memphis, and St. Louis remain useful special "
        "cases because they reflect longer-run structural weakness in international service, likely tied "
        "to hub loss, network restructuring, and reduced airline emphasis."
        "</i></p>",
        unsafe_allow_html=True
    )


render_special_case_airports()
