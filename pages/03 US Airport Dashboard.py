
import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data
from utils.data_utils import get_all_data

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* Target the main container */
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Optional: Center your headers and subheaders for a cleaner look */
    h1, h2, h3 {
        text-align: center;
    }
    
    /* Center the chart container itself */
    .stVegaLiteChart {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)


st.title("US-International Travel: Passenger Trends by US Gateway Airports (1990-2025)")

st.write(
    "To fully understand how the composition of international air travel connected to the United States "
    "has changed since 1990, it is not enough to examine which foreign countries send passengers to the "
    "United States. It is also important to analyze where those passengers enter the country. The location "
    "of international gateway airports reveals how global connectivity is distributed within the United "
    "States and whether growth in international travel has been concentrated among a small number of major "
    "hubs or spread more broadly across the national airport network."
)

st.write(
    "This section therefore shifts the focus from foreign countries to U.S. gateway airports that receive "
    "international flights. By examining how passenger volumes at different airports have evolved over "
    "time, we can observe whether globalization in air travel has reinforced the dominance of traditional "
    "gateway hubs such as New York, Los Angeles, and Miami or whether new entry points have emerged. These "
    "patterns help reveal how international mobility is geographically distributed within the United "
    "States and provide an additional perspective on how global air travel networks connecting to the "
    "United States have evolved over the past three decades."
)

import textwrap

def create_text_chart(content, fontSize=13, width_chars=140):
        wrapped_text = textwrap.wrap(content, width=width_chars)
        return alt.Chart(alt.Data(values=[{'text': wrapped_text}])).mark_text(
         align='left',     
         baseline='top', 
         fontSize=fontSize, 
         fontWeight='normal',
         color='#666', lineBreak='\n', x=0               
     ).encode(
          text='text:N'
     ).properties(
          width=800,        
          height=len(wrapped_text) * (fontSize + 6))


def render_airport_page():
    pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()

    alt.data_transformers.disable_max_rows()

    #Create year and airport selections
    full_airport_map = pd.concat([us_airport_map, new_data], ignore_index=True)

    full_airport_map = full_airport_map.merge(
        pax_by_airport, left_on='code', 
        right_on='US_AIRPORT', how='left'
    ).fillna(0)
    full_airport_map = full_airport_map[full_airport_map['PASSENGERS'] > 0]

    full_airport_map['lon'] = full_airport_map['geometry'].apply(lambda x: x['coordinates'][0])
    full_airport_map['lat'] = full_airport_map['geometry'].apply(lambda x: x['coordinates'][1])

    states = alt.topo_feature(data.us_10m.url, feature='states')

    click_selection = alt.selection_point(
        on='click', fields=['code'], 
        empty=False, nearest=True,
        clear='dblclick')

    Years = sorted(pax_by_airport['YEAR'].unique().tolist())
    Years_Options = [None] + Years 
    Years_Labels = ['All'] + [str(y) for y in Years]

    min_year = int(pax_by_airport['YEAR'].min())
    max_year = int(pax_by_airport['YEAR'].max())

    selection_year = alt.selection_point(
        fields=['YEAR'],
        value=min_year,
        bind=alt.binding_range(
            min=min_year, 
            max=max_year, 
            step=1, 
            name='Select Year: ', 
            debounce=500),
        name='year_selection')

    years_bar_chart = alt.Chart(pax_by_airport).mark_bar().add_params(selection_year).encode(
        x=alt.X('YEAR:O', title="Year"),
        y=alt.Y('sum(PASSENGERS):Q', title="Total Passengers", 
                axis=alt.Axis(titlePadding=10, format='.2s', minExtent=80)),
        opacity=alt.condition(
            selection_year, alt.value(1.0), alt.value(0.3)),
        tooltip=[
            alt.Tooltip('YEAR:O', title='Year'), 
            alt.Tooltip('sum(PASSENGERS):Q', title='Total Passengers', format=',.0f')]
        ).properties(
            width=600,
            height=200, 
            title=alt.Title(
                'US International Air Traffic - Annual Passenger Volume', 
                fontSize=20, anchor = 'middle'))

    #create map for showing size of airport international destinations and selecting the airport
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray', stroke='black',
        strokeWidth=1.5
    ).properties(
        width='container',
        height=600,
        title=alt.TitleParams(
            text="US Airports By Annual International Passengers - Volume Map",
            subtitle=["Select year through dropdown menu at the bottom.", 
            "Click an airport to view passenger trends, top airlines, and top foreign destinations."],
            subtitleFontSize=14, subtitleColor='gray',
            anchor='middle' ))

    max_pax = full_airport_map.groupby(['YEAR', 'code'])['PASSENGERS'].sum().max()

    circles = alt.Chart(full_airport_map).mark_circle(
        stroke='white', 
        strokeWidth=1, 
        strokeOpacity=0.8
    ).encode(
        longitude='lon:Q', 
        latitude='lat:Q', 
        size=alt.Size('total_pax:Q', 
            scale=alt.Scale(type='sqrt', 
                            domain=[0, max_pax], range=[0, 1500]), 
            title='International Passengers',
            legend=alt.Legend(
                orient='bottom',direction='horizontal',
                titleOrient='top',    
                format='.2s', symbolFillColor='steelblue',
                offset=20)), 
        opacity=alt.condition(click_selection, alt.value(0.9), alt.value(0.4)),
        tooltip=[alt.Tooltip('code:N', title='Airport Code'),
            alt.Tooltip('US_CITY_NAME:N', title='City Name'),
            alt.Tooltip('total_pax:Q', title='International Passengers', format=',.0f')]
    ).transform_filter(
        selection_year
    ).transform_aggregate(
        total_pax='sum(PASSENGERS)',
        groupby=['code', 'lon', 'lat', 'US_CITY_NAME']).add_params(
        click_selection)

    airport_label_block = alt.Chart(full_airport_map).mark_text(
        fontSize=20, align='center',
    ).encode(
        text=alt.condition(
            click_selection,
            alt.Text('label:N'),
            alt.value("Select an airport"))
    ).transform_calculate(
        label="'Annual International Passenger Volume - ' + datum.code + ' (' + datum.US_CITY_NAME + ')'"
    ).transform_filter(
        click_selection).properties(
        width='container', 
        height=30 ).add_params(click_selection)

    line_graph_by_airport = alt.Chart(full_airport_map).mark_line(point=True).encode(
        y=alt.Y('sum(PASSENGERS):Q', title='Sum of International Passengers', 
                axis=alt.Axis(titlePadding=10, format='.2s', minExtent=80)),
        x=alt.X('YEAR:O', title='Year'),
        tooltip=[
            alt.Tooltip('YEAR:O', title='Year'),
            alt.Tooltip('US_CITY_NAME:N', title='City Name'),
            alt.Tooltip('sum(PASSENGERS):Q', title='International Passengers', format=',.0f')]
    ).transform_filter(
        click_selection 
    ).properties(
        width='container',
        height=250,
    ).add_params(
        click_selection)

    bar_graph_top_airlines_label_block = alt.Chart(full_airport_map).mark_text(
        fontSize=20,
        align='center'
    ).encode(
        text=alt.condition(
            click_selection,
            alt.Text('label:N'),
            alt.value("Select an airport to view top airlines"))
    ).transform_calculate(
        year_txt="isValid(year_selection.YEAR) ? year_selection.YEAR : 'All Years'",
        label="datum.code + ' (' + datum.US_CITY_NAME + ') - ' + datum.year_txt + ' Summary Statistics'"
    ).transform_filter(
        click_selection
    ).properties(
        width='container', 
        height=30 
    ).add_params(click_selection, selection_year)

    #create bar graph showing top airlines for each airport
    unique_airlines = full_airport_map['CARRIER_NAME'].unique().tolist()
    bar_graph_top_airlines = alt.Chart(full_airport_map).mark_bar().encode(
        y=alt.Y('sum_passengers:Q', title='Sum of International Passengers'),
        x=alt.X('CARRIER_NAME:N', title='Airline Name', sort='-y', 
                axis=alt.Axis(labelAngle=-45, labelOverlap=False)),
        color=alt.Color('CARRIER_NAME:N', 
            scale=alt.Scale(
                domain=unique_airlines,
                scheme='category20'), 
            legend=None),
        tooltip=[
            alt.Tooltip('CARRIER_NAME:N', title='Airline Name'),
            alt.Tooltip('sum_passengers:Q', title='Total International Passengers', format=',.0f')]
    ).transform_filter(
        click_selection 
    ).transform_filter(
        selection_year 
    ).transform_aggregate(
        sum_passengers='sum(PASSENGERS)',
        groupby=['CARRIER_NAME']
    ).transform_window(
        rank='rank(sum_passengers)',
        sort=[alt.SortField('sum_passengers', order='descending')]
    ).transform_filter(
        alt.datum.rank <= 5
    ).properties(
        width=320, height=450, 
        title=alt.TitleParams(
            text='Top 5 Airlines by International Passenger Volume',
            anchor='middle',
            fontSize=16))

    #create bar graph showing top destinations
    unique_cities = full_airport_map['NON_US_CITY_NAME'].unique().tolist()
    bar_graph_top_destinations = alt.Chart(full_airport_map).mark_bar().encode(
        y=alt.Y('sum_passengers:Q', title='Sum of Passengers'),
        x=alt.X('NON_US_CITY_NAME:N', title='Foreign City', sort='-y', 
                axis=alt.Axis(labelAngle=-45, labelOverlap=False)),
        color=alt.Color('NON_US_CITY_NAME:N', 
            scale=alt.Scale(
                domain=unique_cities,  
                scheme='category20'), legend=None),
        tooltip=[
            alt.Tooltip('NON_US_CITY_NAME:N', title='Foreign City Name'),
            alt.Tooltip('NON_US_AIRPORT:N', title='Foreign Airport Code'),
            alt.Tooltip('sum_passengers:Q', title='Total Passengers', format=',.0f')],
    ).transform_filter(
        click_selection 
    ).transform_filter(
        selection_year 
    ).transform_aggregate(
        sum_passengers='sum(PASSENGERS)',
        groupby=['NON_US_CITY_NAME', 'NON_US_AIRPORT']
    ).transform_window(
        rank='rank(sum_passengers)',
        sort=[alt.SortField('sum_passengers', order='descending')]
    ).transform_filter(
        alt.datum.rank <= 5
    ).properties(
        width=320, height=450, 
        title=alt.TitleParams(
            text='Top 5 Foreign Destinations',
            anchor='middle',
            fontSize=16))

    map_chart = (background + circles).project(type='albersUsa')

    spacer = alt.Chart().mark_rect(
        color='white',           
        opacity=0             
    ).encode(
    ).properties(
        width='container',
        height=120)

    years_bar_chart_text_2 = create_text_chart("""The first figure below is identical to the first figure shown on the previous dashboard and uses a bar chart format to display the total number of international passengers flown to and from the United States each year. You may again select the year to highlight for this chart and the remaining figures using the slider at the bottom of the dashboard.""")
    map_text = create_text_chart("""Next, we explore the number of international passengers flown each year from each airport serving international flights within the United States. Each circle represents a specific airport within the United States, while the size of the circle represents the number of passengers traveling internationally to and from the airport in the selected year. Hovering over a circle displays the airport’s name, code, and the precise number of passengers flying to and from it. By selecting an airport, the three charts below, which provide greater detail into the international trends for each airport, populate. You can observe the change in the number of passengers traveling internationally from each airport—and thus how the airports that serve as the largest international gateways have changed—by changing the year using the slider at the bottom of the dashboard. From the map, we can observe that the majority of the airports with the most international passengers are, as expected, in the country’s largest cities, especially those located near the coasts or the northern or southern borders. New York JFK Airport, Miami International Airport, and Los Angeles International Airport are consistently the airports that serve the most international passengers, and all experience steady growth in the number of passengers flown.""")
    line_plot_text = create_text_chart("""The figures below populate once you select an airport from the map above. We next explore how trends change at the airport level; the line chart compares the year with the number of passengers flown internationally to and from the selected airport. At many airports, such as Atlanta and Washington Dulles, we see mostly steady growth in international passengers over time—though as seen in the previous dashboard, there are consistent decreases in 2020 due to the COVID-19 pandemic. New York JFK and Newark appear to be the airports with the greatest decreases in annual passengers in 2001 and 2002, which correlates with the September 11 attacks; both experienced roughly 15% decreases in passengers in 2001 compared to 2000. A number of airports also experience large shocks in international passenger volume within narrow timeframes. For example, St. Louis, Pittsburgh, Memphis, and Cincinnati all saw significant decreases that correlate with airlines closing down their local hubs. In recent years, several airports have experienced significant growth from historically low levels; these include Austin, Denver, Nashville, and San Diego, among others.""")
    bar_charts_specific_text = create_text_chart("""Lastly, in the charts below, we use a bar chart on the left to explore the five top airlines by international passenger volume from the selected U.S. airport, while the bar chart on the right explores the top five international destinations. You can observe that while some airports have international traffic dominated by a single carrier, many have a more even mix of airlines. For example, hub airports such as Atlanta, Charlotte, Miami, and Houston have international traffic dominated by the specific U.S. airline that maintains a hub there. Meanwhile, several airports have a more balanced mix of international passengers; these include hubs for multiple airlines, such as Chicago O’Hare, New York JFK, Los Angeles, and Boston. This also includes smaller airports like Nashville, Austin, Cleveland, and Raleigh, which see a mix of domestic and foreign carriers as their largest international operators. Additionally, while there is a diverse range of top destinations depending on the U.S. gateway, London, Paris, Frankfurt, and Cancun are among the most common foreign airports with the highest service levels from the selected U.S. airports.""")

    dashboard = (years_bar_chart_text_2 & years_bar_chart & 
                 map_text & map_chart & 
                 airport_label_block & line_plot_text &
                 line_graph_by_airport & bar_charts_specific_text &
                 bar_graph_top_airlines_label_block &
                 (bar_graph_top_airlines | bar_graph_top_destinations) & 
                 spacer).resolve_scale(
        color='independent',
        size='independent').configure_view(strokeWidth=0)

    st.altair_chart(dashboard, use_container_width=True)

    

render_airport_page()

st.write("The figures above demonstrate that similarly to how international traffic is concentrated in a few foreign countries, the distribution of U.S. gateway airports is also highly concentrated. While the top three gateways, New York JFK, Los Angeles, and Miami, have remained the leaders throughout the entire period analyzed, there has been significant change in the composition of secondary gateway airports. Some airports that previously served as secondary hubs, such as Cincinnati or Pittsburgh, now see very few international passengers. Conversely, other airports that previously had minimal international service, such as Austin or Nashville, have now emerged as significant secondary gateways.")

