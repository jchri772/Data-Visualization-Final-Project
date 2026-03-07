import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from utils.data_utils import get_all_data

st.header("Geopolitical shocks: country-level collapses and post-COVID movers")

def render_geopolitical_page():
    try:
        st.write("STARTED PAGE")

        pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()
        st.write("Loaded data")

        alt.data_transformers.disable_max_rows()

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

        st.write("Built country_year and global_year")

        # Test chart
        st.subheader("Test chart")

        test_chart = alt.Chart(global_year).mark_line().encode(
            x=alt.X("YEAR:Q", axis=alt.Axis(format="d")),
            y="total_passengers:Q"
        ).properties(width=800, height=250)

        st.altair_chart(test_chart, use_container_width=False)
        st.write("Rendered first chart")

        # Test text
        st.write("If you can see this, the page is running correctly through the chart section.")

    except Exception as e:
        st.error("The page crashed. Exact error below.")
        st.exception(e)

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
                [["foreign_country", "passengers"]]
                .rename(columns={"passengers": "passengers_pre"})
            )
    
            post = (
                country_year[country_year["YEAR"] == e["post"]]
                [["foreign_country", "passengers"]]
                .rename(columns={"passengers": "passengers_post"})
            )
    
            merged = pre.merge(post, on="foreign_country", how="outer").fillna(0)
    
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
            index=shock_events.index("COVID") if "COVID" in shock_events else 0,
            key="shock_event_select"
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
            .properties(width=800, height=450)
        )
    
        st.altair_chart(bars_down, use_container_width=False)
    
        st.write(
            "The figure above shows the percentage change in passenger inflows by country "
            "following the selected shock events. After the September 11 attacks, the largest "
            "declines occurred in Norway, Guyana, Belgium, Ghana, and Saudi Arabia, with Norway "
            "experiencing nearly a complete collapse in passenger inflows relative to its "
            "pre-shock baseline. These sharp contractions suggest that certain international "
            "routes were far more sensitive to security disruptions, particularly those with "
            "smaller but highly concentrated travel flows. In contrast, the period immediately "
            "following the COVID-19 pandemic reveals a much broader and more uniform collapse "
            "in international travel. Countries such as Bolivia, Hungary, Greece, Italy, and "
            "Iceland experienced declines exceeding 90 percent. Unlike the more uneven effects "
            "observed after 9/11, the pandemic produced a systemic shock that simultaneously "
            "disrupted nearly all international travel markets."
        )
    
        st.write("DEBUG SECOND SECTION OK")

render_geopolitical_page()
