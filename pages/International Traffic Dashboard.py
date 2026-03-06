import textwrap

import streamlit as st
import altair as alt
from utils.data_utils import get_all_data


st.title("US-International Travel: Passenger Trends by Foreign Country Dashboard (1990-2025)")
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* Target the main container */
    .block-container {
        max-width: 750;
        padding-top: 2rem;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Optional: Center your headers and subheaders for a cleaner look */
    h1, h2, h3 {
        text-align: left;
    }
    
    /* Center the chart container itself */
    .stVegaLiteChart {
        display: flex;
        justify-content: left;
    }
    </style>
    """, unsafe_allow_html=True)

st.write("Our first dashboard illustrates how the composition of foreign countries with the most passengers flying to the United States has changed over time. Throughout this dashboard, you can see general trends in international passenger traffic to and from the United States from 1990 until 2024. Additionally, you can narrow down the selection by year and country to see more detailed statistics for individual nations, such as the top five routes by passenger traffic to the U.S. and the top five airlines flying between that country and the U.S. Other figures in the dashboard show the relationship of distance to the United States and income with the number of passengers flown to and from the U.S., along with the top 10 foreign countries in terms of passenger volume. You can select the year to view through the slider at the bottom of the dashboard. You may select the country to view through the dropdown menu at the bottom of the dashboard, by selecting a country from the Top 10 Countries chart, or by selecting a country from the Distance vs. Passengers Flown scatterplot.")

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
    
    #### Text charts 
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


    years_bar_chart_text = create_text_chart("""The figure below uses a bar chart format to display the total number of international passengers flown to and from the United States each year. It highlights the selected year and is intended to give the reader a sense of the steady overall growth in international passenger traffic over time, despite two significant decreases: the first occurring in 2001 and 2002 following 9/11, and the second, much larger decrease occurring in 2020 as a result of the COVID-19 pandemic. You may select the year to highlight for this chart and the remaining figures using the slider at the bottom of the dashboard.""")
    top_10_text = create_text_chart("""The next figure below is a line chart displaying the annual passenger count for international travelers flying to and from the United States for the top 10 countries in terms of overall traffic between 1990 and 2024. This figure provides an impression of which countries have the most international traffic to the United States and how the ranking of those countries has shifted over time. The countries with consistently the most passengers flown to and from the United States are Canada, Mexico, and the United Kingdom, while Germany, the Dominican Republic, Japan, France, the Netherlands, Jamaica, and Brazil make up the remaining top nations. As shown in the overall passenger trends chart above, there was a steep decline in the number of passengers flown between the U.S. and all countries below in 2020, followed by a recovery that continued through 2024. Interestingly, Mexico was far less affected by the pandemic than any other top country and surpassed Canada in 2020 as the top foreign country for flights to the United States for the first time. Mexico maintained this position through 2024, and by 2022, it had more passengers flying to and from the United States than in 2019—a point at which most other countries were still far from fully recovering to pre-pandemic levels. This likely relates to the lower level of travel restrictions in Mexico compared to other foreign countries during the pandemic, along with the close ties between the two nations.""")
    scatterplot_text = create_text_chart("""Next, we explore the relationship between a foreign country's average distance from the U.S. and its annual passenger volume through a scatterplot. Individual points on the graph represent data for a single foreign country. The x-axis represents the average distance flown between the United States and the foreign country across all years, meaning that as you change the year selection, a country's x-axis position remains constant. The y-axis represents the annual number of passengers flown between each country and the United States. Since there is a large disparity between countries with the fewest and most passengers, the y-axis uses a logarithmic scale. Additionally, each country's continent is encoded by color, providing more intuitive groupings for the viewer. While the figure above offers a look at trends for top countries,this figure is intended to provide a deeper look at traffic figures for every country at the individual year level. You can observe similar trends to the previous graph by noting that Canada, Mexico, and the United Kingdom are typically the three countries with the most passengers flown to and from the U.S. For each year, you can also observe clusters of countries,with those on the same continent generally located at similar positions on the x-axis. However, there is significant variation within some continents regarding the average distance flown to the United States. For example, within Oceania, Australia, New Zealand, and Fiji have a very large average flown distance to the U.S. because most flights from those nations are to the mainland. In contrast, for other countries in Oceania, such as Tonga, Palau, or the Marshall Islands, the average distance is significantly shorter because most flights are not to the mainland but rather to Hawaii or U.S. territories such as Guam or American Samoa. By selecting a country on the graph, information for the following three charts will also populate.""")
    income_text = create_text_chart("""The following three figures populate only once you have selected a country to view from either the two charts above or through the dropdown menu below. Next, we explore the relationship between passengers flown to the U.S. and income. The orange line shows the average number of passengers flown to the U.S. for the selected country by year, while the blue line indicates that foreign country’s average GDP per capita. While there are naturally many reasons why the average number of passengers flown to the U.S. could change, we expect many of them to be at least strongly correlated with the country’s average income; as income rises, more individuals have the capacity to spend on flights to the U.S., while rising wealth can also correlate with increased U.S. investment or tourism in that country. However, since it takes time for airlines to establish nonstop flights to the U.S. as income grows, we expect changes in nonstop passengers to lag behind changes in income. Income appears to be correlated with the number of passengers flying nonstop to the U.S. in many countries, such as Guyana, which simultaneously experienced a sudden boom in income and passengers around 2021. Other countries, such as Panama or Ireland, experienced highly correlated steady growth in both income and passengers throughout the entire timeframe, excluding the pandemic. However, some changes in average passengers flown to the U.S. appear highly correlated with evolving airline commercial strategies. For many nations, the increase in passengers traveling nonstop to the United States is explained by airlines establishing large connecting operations in their home countries. This is the case for the United Arab Emirates and Qatar, which throughout the 2010s saw nonstop passenger growth driven by airlines such as Emirates, Etihad, and Qatar Airways setting up large connecting hubs. Thus, many passengers included in the data as flying between those countries and the U.S. were actually flying to a third country via the respective airline.""")
    bar_charts_specific_text = create_text_chart("""The final two graphs below provide a deeper look at the composition of international flights for the selected country during the chosen year. The bar graph on the left shows the top five airlines for the selected year in terms of the number of passengers flying between the U.S. and the selected country. The bar graph on the right displays the top five nondirectional routes (with the first code representing the U.S. airport and the second representing the foreign airport) between the U.S. and the foreign country during that year. Some countries, especially those with more flights to and from the United States—such as Canada, Mexico, and the United Kingdom—have a larger distribution of airlines and routes. Meanwhile, some relatively smaller countries or those further away are more likely to be dominated by a single airline or route. For example, flights from Morocco are dominated by Royal Air Maroc, which for most years only operated to New York’s JFK Airport from Casablanca. Similarly, flights to the Marshall Islands consist almost entirely of United (formerly Continental) flights from Honolulu to Majuro, the capital of the Marshall Islands.""")




    #display
    chart = (years_bar_chart_text &
    years_bar_chart & top_10_text & 
    country_change_chart & 
    scatterplot_text &
    scatterplot_title & 
    scatterplot & 
    income_text & income_chart & 
    bar_charts_specific_text & bar_plots_title &
    (top_airlines_bar_chart | top_routes_bar_chart) & 
    spacer).resolve_scale(
        color='independent')
    
    st.altair_chart(chart, use_container_width=True)
render_story_page()

st.write("Overall, the figures above demonstrate that the expansion of international flights to and from the U.S. has been anything but uniform. Much of the growth has been concentrated in only a few countries, many of which are physically closer to the U.S. Additionally, while certain events like 9/11 and COVID-19 have caused significant fluctuations in traffic across the board, much of the growth seen within short periods appears to be driven by factors specific to individual countries.")

