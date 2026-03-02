import streamlit as st
import altair as alt
from utils.data_utils import get_all_data


st.markdown("""
    <style>
    /* Target the main container */
    .block-container {
        max-width: 800px;
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


def render_story_page():
    pax_by_country, pax_by_airport, full_airport_map, new_data = get_all_data()

    ### Scatterplot ### 
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    #create years selection and country selection
    Years = sorted(pax_by_country['Year'].unique().tolist())
    Years_Options = [None] + Years 
    Years_Labels = ['All'] + [str(y) for y in Years]

    country_list = sorted(pax_by_country['Country Name'].unique())

    dropdown_country = alt.binding_select(
        options=country_list, 
        labels=country_list,
        name='Country Name: ')

    min_year = int(pax_by_country['Year'].min())
    max_year = int(pax_by_country['Year'].max())

    selection_year = alt.selection_point(
        fields=['Year'],
        value=min_year,
        bind=alt.binding_range(
            min=min_year, 
            max=max_year, 
            step=1, 
            name='Select Year: ', debounce=500),
        name='year_selection')

    country_selection = alt.selection_point(
        name='country_selection',   
        bind=dropdown_country,
        fields=['Country Name'],
        empty=False,
        toggle=False, on = 'click')

    #Create initial top bar chart showing year selected
    years_bar_chart = alt.Chart(pax_by_country).mark_bar().add_params(selection_year).encode(
            x=alt.X('Year:O', 
                    title="Year"),
            y=alt.Y('sum(PASSENGERS):Q', title="Total Passengers Flown To/From The US"),
            opacity=alt.condition(selection_year,
                alt.value(1.0),   
                alt.value(0.3)),
            tooltip=['Year:O', alt.Tooltip('sum(PASSENGERS):Q', title='Sum of Passengers', format=',.0f')]
            ).properties(#width=1000, 
                         height=200, 
                         title=alt.Title('US International Air Traffic: Annual Passenger Volume to/from the United States', fontSize = 20, anchor = 'middle'))

    top_10_countries = pax_by_country.groupby('Country Name')['PASSENGERS'].sum().nlargest(10).index.tolist()

    #Create scatterplot for selecting country 
    country_change_chart = alt.Chart(pax_by_country).transform_filter(alt.FieldOneOfPredicate(field='Country Name', oneOf=top_10_countries)
    ).mark_line(point=True).encode(
        x=alt.X('Year:O', title= 'Year'),
        y=alt.Y('sum(PASSENGERS):Q', title= 'Total Passengers Flown To/From The US'),
        color=alt.Color('Country Name:N', title="Country",
                        scale=alt.Scale(scheme='category10')),
        opacity=alt.condition(country_selection, alt.value(1.0), alt.value(0.6)),
        tooltip=[
            alt.Tooltip('Country Name:N'),
            alt.Tooltip('Year:O'),
            alt.Tooltip('sum(PASSENGERS):Q', title='Total Passengers', format=',.0f')]).add_params(
        country_selection).properties(#width
                                      height=400,
        title=alt.TitleParams(
            text="Annual Passenger Trends: Top 10 Countries",
            fontSize=20, anchor = 'middle'))

    scatterplot_title = alt.Chart(full_airport_map).mark_text(
        fontSize=20,           
        align='center',
    ).encode(
        text=alt.Text('label:N') 
    ).transform_calculate(
        year_txt="isValid(year_selection.Year) ? year_selection.Year : 'All Years'",
        label="'US-International Travel: ' + datum.year_txt + ' Average Country Distance vs. Passengers Flown'"
    ).properties(
        #width=1000,
        height=40 
    ).add_params(selection_year)

    scatterplot = alt.Chart(pax_by_country).mark_circle(size = 100).encode(
        x = alt.X('mean(AVG_DISTANCE_FLOWN):Q', 
                        title='Average Flown Distance To US (Miles)'),
        color = alt.Color('Continent:N', title = 'Continent', scale=alt.Scale(scheme='category10'), 
        legend=alt.Legend(
            orient='right', 
            symbolSize=100, 
            titleFontSize=14, 
            labelFontSize=12)),
        y=alt.Y('sum(PASSENGERS):Q', 
                     title='Total Passengers Flown To/From The US', axis=alt.Axis(tickCount=5, grid=True, minExtent=40),
                        scale=alt.Scale(type='log', domain=[10, 100000000], clamp=True)),
        opacity=alt.condition(
            country_selection,
            alt.value(1.0),   
            alt.value(0.8)),
        stroke=alt.condition(country_selection, alt.value('black'), alt.value('transparent')),
        detail=['Country Name:N','Continent:N'],
        tooltip =[alt.Tooltip('Country Name:N', title='Country Name'),
                  alt.Tooltip('mean(AVG_DISTANCE_FLOWN):Q', title='Average Flown Distance To US (Miles)', format=',.0f'),
                  alt.Tooltip('sum(PASSENGERS):Q', title='Total Passengers Flown', format=',.0f')]
                ).add_params(country_selection).transform_filter("(year_selection.Year == null) || (datum.Year == year_selection.Year)"
                                                                ).properties(#width=1000,
                    height=500)

    #Create income chart
    base_income = alt.Chart(pax_by_country).encode(
        x=alt.X('Year:O', title="Year")
    ).add_params(country_selection).transform_filter(country_selection)

    income_line = base_income.mark_line(color='#5276A7', point=True).encode(
        y=alt.Y('mean(GDP_Per_Capita):Q', 
                title='Income (GDP Per Capita)', 
                axis=alt.Axis(titleColor='#5276A7')),
        tooltip=[
            alt.Tooltip('Year:O'),
            alt.Tooltip('Country Name:N'),
            alt.Tooltip('mean(GDP_Per_Capita):Q', 
                        title='GDP Per Capita', 
                        format='$,.0f'),
            alt.Tooltip('sum(PASSENGERS):Q', 
                        title='Total Passengers', 
                        format=',.0f')])

    passenger_line = base_income.mark_line(color='#F18536', point=True).encode(
        y=alt.Y('sum(PASSENGERS):Q', 
                title='Total Passengers Flown To/From The US', 
                axis=alt.Axis(titleColor='#F18536')),
        tooltip=[
            alt.Tooltip('Year:O'),
            alt.Tooltip('Country Name:N'),
            alt.Tooltip('mean(GDP_Per_Capita):Q', 
                        title='GDP Per Capita', 
                        format='$,.0f'),
            alt.Tooltip('sum(PASSENGERS):Q', 
                        title='Total Passengers', 
                        format=',.0f')])

    income_chart = alt.layer(
        income_line,
        passenger_line
    ).resolve_scale(
        y='independent').encode(
        x=alt.X(
            'Year:O',
            title="Year",
            axis=alt.Axis(labelAngle=0, tickCount=10))
    ).properties(
        width=800,
        height=400,
        title=alt.TitleParams(
        text=alt.ExprRef(
            "country_selection['Country Name'] ? "
            "country_selection['Country Name'] + ' GDP Per Capita vs. Passenger Volume' : "
            "''"), fontSize=20, anchor='middle'))

    bar_plots_title = alt.Chart(full_airport_map).mark_text(
        fontSize=20,           
        align='center',
    ).encode(
        text=alt.Text('label:N') 
    ).transform_calculate(
        label="(isValid(year_selection.Year) && country_selection['Country Name']) ? "
              "country_selection['Country Name'] + ' ' + year_selection.Year + ' Summary Statistics' : ''").properties(
        width=800,
        height=50 
    ).add_params(
        selection_year, 
        country_selection)

    #create top airlines and top routes bar charts
    top_airlines_bar_chart = alt.Chart(pax_by_country).transform_filter(
        country_selection                    
    ).transform_filter(
        "isValid(year_selection.Year) && datum.Year == year_selection.Year"
    ).transform_fold(
        ['TOP_1_CARRIER_NAME', 'TOP_2_CARRIER_NAME', 'TOP_3_CARRIER_NAME', 'TOP_4_CARRIER_NAME', 'TOP_5_CARRIER_NAME'],
        as_=['rank_name', 'carrier_name']
    ).transform_fold(
        ['TOP_1_CARRIER_NAME_PAX', 'TOP_2_CARRIER_NAME_PAX', 'TOP_3_CARRIER_NAME_PAX', 'TOP_4_CARRIER_NAME_PAX', 'TOP_5_CARRIER_NAME_PAX'],
        as_=['rank_pax', 'passenger_count']
    ).transform_filter(
       (alt.expr.substring(alt.datum.rank_name, 4, 5) == alt.expr.substring(alt.datum.rank_pax, 4, 5)) &
        (alt.datum.carrier_name != None) & (alt.datum.carrier_name != '')).mark_bar().encode(
        x=alt.X('carrier_name:N', title='Carrier', 
            sort='-y',
        axis=alt.Axis(
            labelAngle=-45)),
        y=alt.Y('passenger_count:Q', title='Passengers'),
        color=alt.Color('carrier_name:N', legend=None),
        tooltip=[
            alt.Tooltip('carrier_name:N', title='Carrier'),
            alt.Tooltip('passenger_count:Q', title='Passengers', format=',.0f')]
    ).properties(
        width=350,
        height=450,
        title=alt.TitleParams(
            text="Top 5 Carriers",
            anchor='middle'
        ))

    top_routes_bar_chart = alt.Chart(pax_by_country).transform_filter(
        country_selection                    
    ).transform_filter(
        "isValid(year_selection.Year) && datum.Year == year_selection.Year"
    ).transform_fold(
        ['TOP_1_NONDIRECTIONAL_MARKET', 'TOP_2_NONDIRECTIONAL_MARKET', 'TOP_3_NONDIRECTIONAL_MARKET', 'TOP_4_NONDIRECTIONAL_MARKET', 'TOP_5_NONDIRECTIONAL_MARKET'],
        as_=['rank_name', 'route_name']
    ).transform_fold(
        ['TOP_1_NONDIRECTIONAL_MARKET_PAX', 'TOP_2_NONDIRECTIONAL_MARKET_PAX', 'TOP_3_NONDIRECTIONAL_MARKET_PAX', 'TOP_4_NONDIRECTIONAL_MARKET_PAX', 'TOP_5_NONDIRECTIONAL_MARKET_PAX'],
        as_=['rank_pax', 'passenger_count']
    ).transform_filter(
       (alt.expr.substring(alt.datum.rank_name, 4, 5) == alt.expr.substring(alt.datum.rank_pax, 4, 5)) &
        (alt.datum.route_name != None) & (alt.datum.route_name != '')).mark_bar().encode(
        x=alt.X('route_name:N', title='Nondirectional Route', 
            sort='-y',
        axis=alt.Axis(
            labelAngle=-45)),
        y=alt.Y('passenger_count:Q', title='Passengers'),
        color=alt.Color('route_name:N', legend=None),
        tooltip=[
            alt.Tooltip('route_name:N', title='Nondirectional Route'),
            alt.Tooltip('passenger_count:Q', title='Passengers', format=',.0f')]
    ).properties(
        width=350,
        height=450,
        title=alt.TitleParams(
            text="Top 5 Nondirectional Nonstop Routes",
            anchor='middle'
        ))

    #create spacer so that bar chart labels become visible
    spacer = alt.Chart().mark_rect(
        color='white',           
        opacity=0             
    ).encode(
    ).properties(
        width=400,
        height=120)

    #display
    chart = (years_bar_chart & 
     country_change_chart & 
     scatterplot_title &
     scatterplot & 
     income_chart & 
     bar_plots_title &
     (top_airlines_bar_chart | top_routes_bar_chart) & 
     spacer).resolve_scale(
        color='independent')
    
    st.altair_chart(chart, use_container_width=True)

render_story_page()


import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data
from utils.data_utils import get_all_data

def render_airport_page():
    pax_by_country, pax_by_airport, us_airport_map, new_data = get_all_data()

    alt.data_transformers.disable_max_rows()

    title = alt.Chart(us_airport_map).mark_text(
        fontSize=30, fontWeight='bold', align='center', baseline='middle',).encode(
        text=alt.value('US-International Travel: Passenger Trends by US Gateway Airports')
    ).properties(width=1000, height=50)

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
        y=alt.Y('sum(PASSENGERS):Q', title="Total Passengers"),
        opacity=alt.condition(
            selection_year, alt.value(1.0), alt.value(0.3)),
        tooltip=[
            alt.Tooltip('YEAR:O', title='Year'), 
            alt.Tooltip('sum(PASSENGERS):Q', title='Total Passengers', format=',.0f')]
        ).properties(
            width=1000, 
            height=200, 
            title=alt.Title(
                'US International Air Traffic - Annual Passenger Volume', 
                fontSize=20))

    #create map for showing size of airport international destinations and selecting the airport
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        stroke='black',
        strokeWidth=1.5
    ).properties(
        width=1000,
        height=500,
        title=alt.TitleParams(
            text="US Airports By Annual International Passengers - Volume Map",
            subtitle="Select year through dropdown menu at the bottom. Click an airport to view passenger trends by airport by year, top airlines, and top foreign destinations.",
            fontSize=20,
            subtitleFontSize=14,
            subtitleColor='gray',
            anchor='middle' ))

    max_pax = full_airport_map.groupby(['YEAR', 'code'])['PASSENGERS'].sum().max()

    circles = alt.Chart(full_airport_map
                        ).mark_circle(stroke = 'white', strokeWidth = 1, strokeOpacity =.8).encode(
        longitude='lon:Q', 
        latitude='lat:Q', 
        size=alt.Size('total_pax:Q', 
                      scale=alt.Scale(domain=[0, max_pax],range=[10, 4000]), 
                      title='Total Passengers'),
        opacity=alt.condition(click_selection, alt.value(.9), alt.value(0.4)),
        tooltip=[
            alt.Tooltip('code:N', title='Airport Code'),
            alt.Tooltip('US_CITY_NAME:N', title='City Name'),
            alt.Tooltip('total_pax:Q', title='International Passengers', format=',.0f')]
        ).transform_filter(
            selection_year
        ).transform_aggregate(
            total_pax='sum(PASSENGERS)',
            groupby=['code', 'lon', 'lat', 'US_CITY_NAME'] 
        ).add_params(
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
        width=1000, height=30 ).add_params(click_selection)

    line_graph_by_airport = alt.Chart(full_airport_map).mark_line(point=True).encode(
        y=alt.Y('sum(PASSENGERS):Q', title='Sum of International Passengers'),
        x=alt.X('YEAR:O', title='Year'),
        tooltip=[
            alt.Tooltip('YEAR:O', title='Year'),
            alt.Tooltip('US_CITY_NAME:N', title='City Name'),
            alt.Tooltip('sum(PASSENGERS):Q', title='International Passengers', format=',.0f')]
    ).transform_filter(
        click_selection 
    ).properties(
        width=1000, height=250,
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
        width=1000, height=30 
    ).add_params(click_selection, selection_year)

    #create bar graph showing top airlines for each airport
    unique_airlines = full_airport_map['CARRIER_NAME'].unique().tolist()
    bar_graph_top_airlines = alt.Chart(full_airport_map).mark_bar().encode(
        y=alt.Y('sum_passengers:Q', title='Sum of International Passengers'),
        x=alt.X('CARRIER_NAME:N', title='Airline Name', sort='-y', 
                axis=alt.Axis(labelAngle=-45)),
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
        width=450, height=450, 
        title = 'Top 5 Airlines by International Passengers')

    #create bar graph showing top destinations
    unique_cities = full_airport_map['NON_US_CITY_NAME'].unique().tolist()
    bar_graph_top_destinations = alt.Chart(full_airport_map).mark_bar().encode(
        y=alt.Y('sum_passengers:Q', title='Sum of Passengers'),
        x=alt.X('NON_US_CITY_NAME:N', title='Foreign City', sort='-y', 
                axis=alt.Axis(labelAngle=-45)),
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
        width=450, height=450, 
        title = 'Top 5 Foreign Destinations')

    map_chart = (background + circles).project(type='albersUsa')

    # Define spacer since it was used in dashboard but not defined in snippet
    spacer = alt.Chart(pd.DataFrame({'x': [0]})).mark_point(opacity=0).properties(height=50)

    dashboard = (title & 
                 years_bar_chart & 
                 map_chart & 
                 airport_label_block & 
                 line_graph_by_airport & 
                 bar_graph_top_airlines_label_block &
                 (bar_graph_top_airlines | bar_graph_top_destinations) & 
                 spacer).resolve_scale(
        color='independent',
        size='independent')

    st.altair_chart(dashboard, use_container_width=True)

if __name__ == "__main__":
    render_airport_page()