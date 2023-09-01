import streamlit as st
import plotly.express as px
import pandas as pd
import hvplot.pandas
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
import holoviews as hv
from holoviews import opts
hv.extension('bokeh', logo=False)
from bokeh.plotting import figure, show

# Read the Mapbox API key
load_dotenv('api.env')
map_box_api = os.getenv("mapbox")
px.set_mapbox_access_token(map_box_api)

# Import the necessary CSVs to Pandas DataFrames
# census data df
file_path = Path("Data/sfo_neighborhoods_census_data.csv")
sfo_data = pd.read_csv(file_path, index_col="year")
# coordinates df
geo = pd.read_csv('Data/neighborhoods_coordinates.csv')
geo = geo.rename(columns={'Neighborhood' : 'neighborhood'})


## Streamlit Visualizations

#In this section, you will copy the code for each plot type from your analysis notebook and place it into separate functions that Streamlit can use to visualize the different visualizations.

#These functions will return the plot or figure for each visualization.

#Be sure to include any DataFrame transformation/manipulation code required along with the plotting code.

#Return a figure object from each function that can be used to build the dashboard.

#Note: Remove any `.show()` lines from the code. We want to return the plots instead of showing them. The Streamlit dashboard will then display the plots.


# Define Panel Visualization Functions
def housing_units_per_year():
    """Housing Units Per Year."""
    # Calculate the mean number of housing units per year (hint: use groupby) 
    units_year = sfo_data.housing_units.groupby('year').mean()
    units_year = pd.DataFrame(units_year)
    # Storing min, max, and std values for y
    y_min = min(units_year.housing_units)
    y_max = max(units_year.housing_units)
    y_std = np.std(units_year.housing_units)
    # Using these stored values to define the bottom and top of the y values
    bottom = y_min - y_std
    top = y_max + y_std
    
    
    # Calling the bottom and top of y
    plt.ylim(bottom, top)

    plt.xlabel('Year')
    plt.ylabel('Housing Units')
    plt.title('Scaled Housing Units per Year')
    
    return plt.bar(units_year.index, units_year.housing_units)


def average_gross_rent():
    costs_df = sfo_data[['sale_price_sqr_foot', 'gross_rent']]
    costs_df = costs_df.groupby(costs_df.index).mean()
    
    return costs_df.gross_rent.plot(color='red')



def average_sales_price():
    costs_df = sfo_data[['sale_price_sqr_foot', 'gross_rent']]
    costs_df = costs_df.groupby(costs_df.index).mean()
    return costs_df.sale_price_sqr_foot.plot()



def average_sqft_price_by_neighborhood():
    neigh = sfo_data.reset_index()
    neigh = neigh.groupby(['year', 'neighborhood']).mean()
    render = neigh.hvplot.line(x='year', y='sale_price_sqr_foot', groupby='neighborhood')
    render = hv.render(render, backend='bokeh')
    return render



def gross_rent_by_neighborhood():
    neigh = sfo_data.reset_index()
    neigh = neigh.groupby(['year', 'neighborhood']).mean()
    render = neigh.hvplot.line(x='year', y='gross_rent', groupby='neighborhood')
    render = hv.render(render, backend='bokeh')
    return render

def top_most_expensive_neighborhoods():
    top10 = sfo_data.groupby(['neighborhood']).mean().reset_index()
    top10 = top10.sort_values('sale_price_sqr_foot', ascending=False)
    top10 = top10.head(10).reset_index().drop(columns='index')
    render = top10.hvplot.bar(x='neighborhood', y='sale_price_sqr_foot').opts(
    xlabel='Neighborhood',
    ylabel='Average Price per Square Foot',
    title='Top 10 Neighborhoods by Average Price per Square Foot',
    xrotation=45
    )
    render = hv.render(render, backend='bokeh')
    return render

def comparison_of_rent_and_sqrft_by_neighborhood():
    neigh = sfo_data.reset_index()
    neigh = neigh.groupby(['year', 'neighborhood']).mean()   
    side_x_side = ['gross_rent', 'sale_price_sqr_foot']
    render = neigh.hvplot.bar(x='year', y=side_x_side, groupby='neighborhood', ylabel='Num Housing Units', xlabel='Neighborhood Cost Metrics', rot=90)
    render = hv.render(render, backend='bokeh')
    return render
    
    
def parallel_coordinates():
    top10 = sfo_data.groupby(['neighborhood']).mean().reset_index()
    top10 = top10.sort_values('sale_price_sqr_foot', ascending=False)
    top10 = top10.head(10).reset_index().drop(columns='index')
    
    return px.parallel_coordinates(top10, color='sale_price_sqr_foot')



def parallel_categories():
    top10 = sfo_data.groupby(['neighborhood']).mean().reset_index()
    top10 = top10.sort_values('sale_price_sqr_foot', ascending=False)
    top10 = top10.head(10).reset_index().drop(columns='index')

    return px.parallel_categories(
    top10,
    # columns to use from top10 dataframe
    dimensions=['neighborhood', 'sale_price_sqr_foot', 'housing_units', 'gross_rent'],
    color='sale_price_sqr_foot',
    color_continuous_scale=px.colors.sequential.Inferno,
    #Redefining column names into readable names
    labels={
        'neighborhood':'Neighborhood',
        'sale_price_sqr_foot':'Sale Price per Square Foot',
        'housing_units':'Housing Units',
        'gross_rent':'Gross Rent'
    }
    )



def neighborhood_map():
    mean = sfo_data.groupby(['neighborhood']).mean().reset_index()
    merge_df = pd.merge(geo, mean, on='neighborhood', how='inner')
    return px.scatter_mapbox(
        merge_df,
        lat='Lat',
        lon='Lon',
        size='sale_price_sqr_foot',
        color='sale_price_sqr_foot',
        zoom=10,
        color_continuous_scale='Inferno',
    )

def sunburst():
    neigh = sfo_data.reset_index()
    neigh = neigh.groupby(['year', 'neighborhood']).mean()
    neigh = neigh.reset_index()
    top10 = sfo_data.groupby(['neighborhood']).mean().reset_index()
    top10 = top10.sort_values('sale_price_sqr_foot', ascending=False)
    top10 = top10.head(10).reset_index().drop(columns='index')
    df_expensive_neighborhoods_per_year = neigh[neigh["neighborhood"].isin(top10["neighborhood"])]
    df_expensive_neighborhoods_per_year = df_expensive_neighborhoods_per_year.groupby(['year', 'neighborhood']).mean().reset_index()
    
    return px.sunburst(
    df_expensive_neighborhoods_per_year,
    # path starts in the center with year, ends in the outer circle with neighborhood. Values decides how big each category will be depicted as.
    path=['year', 'neighborhood'], values='sale_price_sqr_foot',
    color='gross_rent',
    color_continuous_scale='RdBu'
    )

# Start Streamlit App
st.title('San Francisco Real Estate Analysis')

# Define list of pages
pages = ['Housing Units Per Year', 'Average Gross Rent', 'Average Sales Price', 'Average Square Ft Price by Neighborhood', 'Gross Rent by Neighborhood', 'Top 10 Most Expensive Neighborhoods', 'Comparing Rent and Sqft Prices by Neighborhood', 'Parallel Categories', 'Parallel Coordinates', 'Sunburst Chart', 'Neighborhood Map']
st.sidebar.title('Select a Page to Show')
selected_page = st.sidebar.selectbox('Select Chart', pages)


    
# Create a function to render the Plotly graphs
if selected_page == "Housing Units Per Year":
    st.header(selected_page)
    fig, ax = plt.subplots()
    ax = housing_units_per_year()
    st.pyplot(fig)
elif selected_page == "Average Gross Rent": 
    st.header(selected_page)
    fig, ax = plt.subplots()
    ax = average_gross_rent()
    st.pyplot(fig)
elif selected_page == 'Average Sales Price':
    st.header(selected_page)
    fig, ax = plt.subplots()
    ax = average_sales_price()
    st.pyplot(fig)
elif selected_page == 'Average Square Ft Price by Neighborhood':
    st.header(selected_page)
    fig = average_sqft_price_by_neighborhood()
    st.bokeh_chart(fig)
elif selected_page == 'Gross Rent by Neighborhood':
    st.header(selected_page)
    st.bokeh_chart(gross_rent_by_neighborhood())
elif selected_page == 'Top 10 Most Expensive Neighborhoods':
    st.header(selected_page)
    st.bokeh_chart(top_most_expensive_neighborhoods())
elif selected_page == 'Comparing Rent and Sqft Prices by Neighborhood':
    st.header(selected_page)
    st.bokeh_chart(comparison_of_rent_and_sqrft_by_neighborhood())
elif selected_page == 'Parallel Categories':
    st.header(selected_page)
    fig = parallel_categories()
    st.plotly_chart(fig)
elif selected_page == 'Parallel Coordinates':
    st.header(selected_page)
    fig = parallel_coordinates()
    st.plotly_chart(fig)
elif selected_page == 'Sunburst Chart':
    st.header(selected_page)
    fig = sunburst()
    st.plotly_chart(fig)
elif selected_page == 'Neighborhood Map':
    st.header(selected_page)
    fig = neighborhood_map()
    st.plotly_chart(fig)
