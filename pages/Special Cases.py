import streamlit as st
import altair as alt
import pandas as pd
from utils.data_utils import get_all_data

st.set_page_config(layout="wide")

st.title("Special-case airports: irregular post-COVID recovery patterns")

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

    chart = (
        alt.Chart(special_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y("passengers:Q", title="International passengers"),
            tooltip=[
                alt.Tooltip("YEAR:O", title="Year"),
                alt.Tooltip("airport_label:N", title="Airport"),
                alt.Tooltip("passengers:Q", title="Passengers", format=",.0f")
            ]
        )
        .properties(
            width=200,
            height=250
        )
        .facet(
            column=alt.Column("airport_label:N", title=None)
        )
    )

    st.altair_chart(chart, use_container_width=True)


render_special_case_airports()
