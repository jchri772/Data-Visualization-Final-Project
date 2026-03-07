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

render_geopolitical_page()
