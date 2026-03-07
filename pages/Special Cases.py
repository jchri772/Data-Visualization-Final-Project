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
    "To make this contrast easier to interpret, the figure also includes Los Angeles (LAX) as a benchmark "
    "major international gateway. The vertical scale is fixed using only the four special-case airports, "
    "so LAX extends beyond that range and visually emphasizes how much larger its international recovery was."
)


def render_special_case_airports():
    pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()

    alt.data_transformers.disable_max_rows()

    selected_airports = ["CVG", "PIT", "MEM", "STL", "LAX"]

    airport_labels = {
        "CVG": "CVG (Cincinnati)",
        "PIT": "PIT (Pittsburgh)",
        "MEM": "MEM (Memphis)",
        "STL": "STL (St. Louis)",
        "LAX": "LAX (Los Angeles, benchmark)"
    }

    special_df = pax_by_airport.copy()
    special_df.columns = [c.strip() for c in special_df.columns]

    special_df = special_df[
        (special_df["US_AIRPORT"].isin(selected_airports)) &
        (special_df["YEAR"].between(2019, 2024))
    ].copy()

    special_df = (
        special_df.groupby(["YEAR", "US_AIRPORT"], as_index=False)
        .agg(passengers=("PASSENGERS", "sum"))
    )

    special_df["airport_label"] = special_df["US_AIRPORT"].map(airport_labels)
    special_df["line_type"] = special_df["US_AIRPORT"].apply(
        lambda x: "Benchmark" if x == "LAX" else "Special case"
    )

    special_only_max = special_df.loc[
        special_df["US_AIRPORT"].isin(["CVG", "PIT", "MEM", "STL"]),
        "passengers"
    ].max()

    y_max = special_only_max * 1.10

    line_chart = (
        alt.Chart(special_df)
        .mark_line(point=True, clip=False)
        .encode(
            x=alt.X("YEAR:O", title="Year"),
            y=alt.Y(
                "passengers:Q",
                title="International passengers",
                scale=alt.Scale(domain=[0, y_max], clamp=False)
            ),
            color=alt.Color("airport_label:N", title="Airport"),
            strokeDash=alt.StrokeDash(
                "line_type:N",
                title=None,
                scale=alt.Scale(
                    domain=["Special case", "Benchmark"],
                    range=[[1, 0], [6, 4]]
                )
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
        "post-COVID recovery patterns between 2019 and 2024, while also including Los Angeles (LAX) as a "
        "benchmark major gateway. The y-axis is scaled to the four special-case airports only, so LAX rises "
        "beyond the plotted range and makes the contrast in recovery scale immediately visible."
        "</i></p>",
        unsafe_allow_html=True
    )


render_special_case_airports()
