import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from utils.data_utils import get_all_data

st.header("Geopolitical shocks: country-level collapses and post-COVID movers")
st.write("")
st.write("")
st.write("Taking a deeper look, this section examines how major geopolitical shocks affected international passenger flows to and from the United States. For clarity, the analysis focuses on two major disruptions, the September 11 attacks and the COVID-19 pandemic. The first visualization presents the aggregate impact of these events on overall passenger volumes. Subsequent visuals then move to the country level, highlighting where the largest contractions occurred using measures such as magnitude of passenger loss and percentage change relative to pre-shock levels.")

def render_geopolitical_page():

    pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()

    alt.data_transformers.disable_max_rows()

    # ---------------------------
    # Normalize column names
    # ---------------------------
    df = pax_by_country.copy()
    df.columns = [c.strip() for c in df.columns]

    df = df.rename(columns={
        "Country Name": "foreign_country",
        "YEAR": "YEAR",
        "PASSENGERS": "PASSENGERS"
    })

    required = {"YEAR", "foreign_country", "PASSENGERS"}
    missing = required - set(df.columns)

    if missing:
        st.error(f"Missing required columns in pax_by_country: {missing}")
        st.stop()

    country_year = (
        df.groupby(["YEAR", "foreign_country"], as_index=False)
        .agg(passengers=("PASSENGERS", "sum"))
    )

    country_year["YEAR"] = pd.to_numeric(
        country_year["YEAR"], errors="coerce"
    ).astype("Int64")

    global_year = (
        country_year.groupby("YEAR", as_index=False)
        .agg(total_passengers=("passengers", "sum"))
    )

    # ---------------------------
    # Global timeline
    # ---------------------------
    st.subheader("International passengers to and from the U.S. (1990–2025)")

    events = pd.DataFrame({
        "YEAR": [2001, 2020],
        "event": ["9/11", "COVID"]
    })

    timeline = alt.Chart(global_year).mark_line().encode(
        x=alt.X("YEAR:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y("total_passengers:Q", title="Total international passengers"),
        tooltip=["YEAR:Q", alt.Tooltip("total_passengers:Q", format=",.0f")]
    ).properties(
        width=800,
        height=260
    )

    markers = alt.Chart(events).mark_rule(
        strokeDash=[6, 4]
    ).encode(
        x="YEAR:Q",
        tooltip=["event:N", "YEAR:Q"]
    )

    st.altair_chart(timeline + markers, use_container_width=False)
    st.caption("The figure above shows the total volume of international passengers traveling to and from the United States between 1990 and 2025. A line chart is used to represent this quantitative data as a continuous trend over time, making long-run patterns and disruptions easier to interpret. The dotted vertical lines mark the timing of two major shocks to international travel, the September 11 attacks and the COVID-19 pandemic.")
    
    st.markdown("")

    # ---------------------------
    # Shock collapses
    # ---------------------------
    st.subheader("Largest country-level collapses during major shocks")

    event_windows = [
        {"event": "9/11", "pre": 2000, "post": 2002},
        {"event": "COVID", "pre": 2019, "post": 2020},
    ]

    shocks_list = []

    for e in event_windows:

        pre = (
            country_year[country_year["YEAR"] == e["pre"]]
            [["", "passengers"]]
            .rename(columns={"passengers": "passengers_pre"})
        )

        post = (
            country_year[country_year["YEAR"] == e["post"]]
            [["", "passengers"]]
            .rename(columns={"passengers": "passengers_post"})
        )

        merged = pre.merge(post, on="", how="outer").fillna(0)

        merged["event"] = e["event"]
        merged["pre_year"] = e["pre"]
        merged["post_year"] = e["post"]

        merged["abs_change"] = merged["passengers_post"] - merged["passengers_pre"]

        merged["pct_change"] = np.where(
            merged["passengers_pre"] > 0,
            merged["abs_change"] / merged["passengers_pre"],
            np.nan
        )

        shocks_list.append(merged)

    shocks = pd.concat(shocks_list, ignore_index=True)

    shock_events = sorted(shocks["event"].unique())

    selected_event = st.selectbox(
        "Shock event:",
        options=shock_events,
        index=shock_events.index("COVID") if "COVID" in shock_events else 0
    )

    BASELINE_MIN = 50_000

    shocks_filtered = shocks[
        (shocks["event"] == selected_event) &
        (shocks["passengers_pre"] >= BASELINE_MIN)
    ].copy()

    shocks_filtered["pct_change_pct"] = shocks_filtered["pct_change"] * 100
    shocks_filtered["loss_mag"] = -1 * shocks_filtered["pct_change_pct"]

    shocks_filtered = shocks_filtered[
        shocks_filtered["pct_change_pct"] < 0
    ].copy()

    shocks_filtered = shocks_filtered.sort_values(
        "loss_mag", ascending=False
    ).head(25)

    bars_down = (
        alt.Chart(shocks_filtered)
        .mark_bar(color="#ac3333c9")
        .encode(
            x=alt.X(
                "foreign_country:N",
                sort=alt.SortField("loss_mag", order="descending"),
                axis=alt.Axis(labelAngle=90),
                title=None
            ),
            y=alt.Y(
                "loss_mag:Q",
                title="Percent decline (pre → post)",
                scale=alt.Scale(domain=[0, 105], reverse=True)
            ),
            tooltip=[
                "foreign_country:N",
                alt.Tooltip("passengers_pre:Q", title="Pre-shock passengers", format=",.0f"),
                alt.Tooltip("passengers_post:Q", title="Post-shock passengers", format=",.0f"),
                alt.Tooltip("pct_change_pct:Q", title="Percent change", format=".1f"),
            ]
        )
        .properties(
            width=800,
            height=450
        )
    )

    st.altair_chart(bars_down, use_container_width=False)

    st.markdown("")

    # ---------------------------
    # Post-COVID movers
    # ---------------------------
    st.subheader("Top post-COVID movers (2019 → 2024)")

    PRE_YEAR = 2019
    POST_YEAR = 2024

    cy_19_24 = (
        country_year[country_year["YEAR"].isin([PRE_YEAR, POST_YEAR])]
        .pivot_table(
            index="foreign_country",
            columns="YEAR",
            values="passengers",
            aggfunc="sum"
        )
        .reset_index()
        .rename(columns={
            PRE_YEAR: "passengers_pre",
            POST_YEAR: "passengers_post"
        })
        .fillna(0)
    )

    cy_19_24["abs_change"] = (
        cy_19_24["passengers_post"] - cy_19_24["passengers_pre"]
    )

    cy_19_24["pct_change"] = np.where(
        cy_19_24["passengers_pre"] > 0,
        cy_19_24["abs_change"] / cy_19_24["passengers_pre"],
        np.nan
    )

    cy_19_24["pct_change_pct"] = 100 * cy_19_24["pct_change"]

    BASELINE_MIN_POSTCOVID = 50_000
    cy_19_24 = cy_19_24[
        cy_19_24["passengers_pre"] >= BASELINE_MIN_POSTCOVID
    ].copy()

    movers_view = st.selectbox(
        "Post-COVID movers view:",
        options=["Percent change", "Magnitude change"],
        index=0
    )

    if movers_view == "Percent change":
        top_inc = cy_19_24.nlargest(5, "pct_change").copy()
        top_dec = cy_19_24.nsmallest(5, "pct_change").copy()
        movers_df = pd.concat([top_dec, top_inc], ignore_index=True).copy()

        movers_chart = (
            alt.Chart(movers_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "foreign_country:N",
                    sort=alt.SortField("pct_change_pct", order="ascending"),
                    axis=alt.Axis(
                        labelAngle=45,
                        labelOverlap=False,
                        title=None
                ),
                y=alt.Y(
                    "pct_change_pct:Q",
                    title="Percent change (2019 → 2024)"
                ),
                tooltip=[
                    "foreign_country:N",
                    alt.Tooltip("passengers_pre:Q", title="2019 passengers", format=",.0f"),
                    alt.Tooltip("passengers_post:Q", title="2024 passengers", format=",.0f"),
                    alt.Tooltip("abs_change:Q", title="Absolute change", format=",.0f"),
                    alt.Tooltip("pct_change_pct:Q", title="Percent change", format=".1f"),
                ]
            )
            .properties(
                width=800,
                height=450
            )
        )

    else:
        top_inc = cy_19_24.nlargest(5, "abs_change").copy()
        top_dec = cy_19_24.nsmallest(5, "abs_change").copy()
        movers_df = pd.concat([top_dec, top_inc], ignore_index=True).copy()

        movers_chart = (
            alt.Chart(movers_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "foreign_country:N",
                    sort=alt.SortField("abs_change", order="ascending"),
                    axis=alt.Axis(
                        labelAngle=45,
                        labelOverlap=False,
                        title=None
                    )
                ),
                y=alt.Y(
                    "abs_change:Q",
                    title="Passenger change (2019 → 2024)"
                ),
                tooltip=[
                    "foreign_country:N",
                    alt.Tooltip("passengers_pre:Q", title="2019 passengers", format=",.0f"),
                    alt.Tooltip("passengers_post:Q", title="2024 passengers", format=",.0f"),
                    alt.Tooltip("abs_change:Q", title="Absolute change", format=",.0f"),
                    alt.Tooltip("pct_change_pct:Q", title="Percent change", format=".1f"),
                ]
            )
            .properties(
                width=800,
                height=450
            )
        )

    zero_line = alt.Chart(
        pd.DataFrame({"y": [0]})
    ).mark_rule(strokeDash=[4, 4]).encode(
        y="y:Q"
    )

    st.altair_chart(movers_chart + zero_line, use_container_width=False)


render_geopolitical_page()
