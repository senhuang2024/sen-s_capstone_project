import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from etl.extract.current import insert_current
import datetime
import plotly.express as px
import plotly.graph_objects as go
from etl.extract.vegtables import get_veg_data, VEG_COLOUR
import base64
import random
import time
from PIL import Image

st.set_page_config(layout="wide")

# set the background image for stremlit
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode()
    css_code = f"""
    <style>
    .stApp {{
        background-color:rgb(255,255,255)
    }}
    [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{b64_image}");
        background-color:rgb(255,255,255,0.8);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-blend-mode: lighten;
    }}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

# set the sun image on the top right corner of streamlit
def add_top_right_image(image_file):
    with open(image_file, "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode()
    css_code = f"""
    <style>
    .top-right-image {{
        position: absolute;
        top: 10px;
        right: 10px;
        width: 100px;
        z-index: 10;
    }}
    </style>
    <img class="top-right-image" src="data:image/png;base64,{b64_image}" alt="Top Right Image">
    """
    st.markdown(css_code, unsafe_allow_html=True)

# load environment variables
load_dotenv()
db_user = os.getenv('SOURCE_DB_USER')
db_password = os.getenv('SOURCE_DB_PASSWORD')
db_host = os.getenv('SOURCE_DB_HOST')
db_port = os.getenv('SOURCE_DB_PORT')
db_name = os.getenv('SOURCE_DB_NAME')

# connect to the postgresql database
def connect_to_db():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

# fetch weather data for a specific location
def get_weather_data(location):
    conn = connect_to_db()

    # query for historical data in sql
    historical_query = f"""
    SELECT city, date, avgtemp_c, maxtemp_c, mintemp_c, totalprecip_mm, uv_index
    FROM student.de11_fehu_capstone
    WHERE LOWER(city) = LOWER('{location}')
    ORDER BY date ASC;
    """
    historical_df = pd.read_sql(historical_query, conn)

    # query for current data in sql
    current_query = f"""
    SELECT city, date, temp_c AS avgtemp_c, temp_c AS maxtemp_c, temp_c AS mintemp_c, precip_mm AS totalprecip_mm, uv_index
    FROM student.weather_data
    WHERE LOWER(city) = LOWER('{location}')
    ORDER BY date DESC
    LIMIT 1;
    """
    current_df = pd.read_sql(current_query, conn)

    conn.close()

    # combine both dataframes
    combined_df = pd.concat([historical_df, current_df]).drop_duplicates(subset=['date'], keep='first')
    return combined_df

# data transformation functions
def transform_to_monthly_data(df):
    df['month'] = df['date'].dt.to_period('M').astype(str)
    monthly_df = df.groupby('month', as_index=False).agg({
        'avgtemp_c': 'mean',
        'maxtemp_c': 'max',
        'mintemp_c': 'min',
        'totalprecip_mm': 'sum'
    })
    # convert month from period to string
    monthly_df['month'] = monthly_df['month'].astype(str)
    return monthly_df

#max and min temperature
def add_extreme_flags(df):
    df['is_highest_temp'] = df['maxtemp_c'] == df['maxtemp_c'].max()
    df['is_lowest_temp'] = df['mintemp_c'] == df['mintemp_c'].min()
    return df

#fill missing dates
def fill_missing_dates(df):
    all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())
    df = df.set_index('date').reindex(all_dates).reset_index()
    df.rename(columns={'index': 'date'}, inplace=True)
    return df

#cumulative frequency of the precipitation data
def add_cumulative_precipitation(df):
    df['cumulative_precip_mm'] = df['totalprecip_mm'].cumsum()
    return df

# create a range bar chart for temprature and vegtable data
def create_range_bar_chart(df, city, veg):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B')
    monthly_data = df.groupby('month', as_index=False).agg({
        'maxtemp_c': 'max',
        'mintemp_c': 'min'
    })

    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=month_order, ordered=True)
    monthly_data = monthly_data.sort_values('month')

    veg_data = get_veg_data()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        width=0.5,
        x=monthly_data['month'],
        y=monthly_data['maxtemp_c'] - monthly_data['mintemp_c'],
        base=monthly_data['mintemp_c'],
        name='Recorded City Temperature Range',
        marker=dict(color='skyblue'),
        hoverinfo='x+y',
        opacity=0.75
    ))

    fig.add_trace(go.Bar(
        width=0.3,
        x=veg_data[veg]['month'],
        y=veg_data[veg]['maxtemp_c'] - veg_data[veg]['mintemp_c'],
        base=veg_data[veg]['mintemp_c'],
        name=f'Optimal {veg} Temperature Range',
        marker=dict(color=VEG_COLOUR.get(veg, "green")),
        hoverinfo='x+y',
        opacity=0.75
    ))

    fig.update_layout(
        title=f"Monthly Temperature Range {city}",
        xaxis_title="Month",
        yaxis_title="Temperature (°C)",
        yaxis=dict(showgrid=True),
        barmode='stack',
        plot_bgcolor="rgba(255, 255, 255, 0.80)",
        paper_bgcolor="rgba(255, 255, 255, 0.80)",
    )

    return fig

# get location from user input
def get_location():
    user_input = st.sidebar.text_input("Enter City", value="Bristol")
    return user_input

# fun facts about weather
fun_facts = [
    "A bolt of lightning is five times hotter than the surface of the sun.",
    "The highest temperature ever recorded on Earth was 56.7°C in Furnace Creek, California.",
    "Tomatoes are technically fruits, not vegetables!",
    "Raindrops can fall at speeds of about 22 miles per hour.",
    "Hailstones can reach the size of grapefruits in extreme storms."
]

##---------------------------------------------- main function for the Streamlit app--------------------------------------------------------


def main():
    
    ## streamlit main page images
    set_background("../../docs/background.png")
    add_top_right_image("../../docs/sun.png")
    
    # add a button to display pictures
    if st.sidebar.button("Pictures!"):
        st.write("### Family Garden Pictures!")

        # list of uploaded pictures and edit
        picture_paths = ["../../docs/1.jpg","../../docs/2.jpg","../../docs/3.jpg","../../docs/4.jpg","../../docs/5.jpg","../../docs/6.jpg","../../docs/7.jpg",]

        for picture_path in picture_paths:
            image = Image.open(picture_path)
            rotated_image = image.rotate(-90, expand=True)
            st.image(rotated_image, use_container_width=True, caption=f"Picture: {os.path.basename(picture_path)}")
            
    st.sidebar.title("Weather and Vegetable Data Analysis")
    city = get_location()

    # all the analysis type
    analysis_type = st.sidebar.selectbox("Select Analysis Type", [
        "Temperature Overview", "Precipitation", "Monthly Trends", "Extreme Temperatures", "Vegetable and Temperature Comparison"
    ])

    veg_type = st.sidebar.selectbox("Select Vegetable/Fruit Type", get_veg_data().keys())

    # add a button for random fun facts
    if st.sidebar.button("Show a Fun Fact"):
        st.write(f"🌟 Fun Fact: {random.choice(fun_facts)}")

    if st.sidebar.button("Fetch Weather and Vegetable Data"):
        with st.spinner("Fetching weather and vegetable data..."):
            progress_bar = st.progress(0)
            for percent in range(100):
                time.sleep(0.01)  # simulate work
                progress_bar.progress(percent + 1)
            insert_current(city)  # insert current weather data into the database
            df = get_weather_data(city)

        if not df.empty:
            
            # apply transformations
            df['date'] = pd.to_datetime(df['date'])  # ensure date column is datetime
            df = fill_missing_dates(df)
            df = add_extreme_flags(df)
            df = add_cumulative_precipitation(df)
            monthly_df = transform_to_monthly_data(df)

            # temperature overview analysis
            if analysis_type == "Temperature Overview":
                fig = px.line(df, x='date', y=['avgtemp_c', 'maxtemp_c', 'mintemp_c'],
                              labels={'value': 'Temperature (°C)', 'variable': 'Temperature Type', 'date': 'Date'},
                              title=f"Temperature Overview for {city}")
                fig.update_traces(mode='lines+markers')
                st.plotly_chart(fig, use_container_width=True)

                # add summary insights below the plot
                st.write("### Summary Insights")
                avg_temp = df['avgtemp_c'].mean()
                max_temp = df['maxtemp_c'].max()
                min_temp = df['mintemp_c'].min()
                st.write(f"**Average Temperature**: {avg_temp:.2f}°C")
                st.write(f"**Maximum Temperature**: {max_temp:.2f}°C")
                st.write(f"**Minimum Temperature**: {min_temp:.2f}°C")

                temp_boxplot = px.box(df, y=['avgtemp_c', 'maxtemp_c', 'mintemp_c'],
                                      labels={'value': 'Temperature (°C)', 'variable': 'Temperature Type'},
                                      title="Temperature Distribution")
                st.plotly_chart(temp_boxplot, use_container_width=True)

            # precipitation analysis
            elif analysis_type == "Precipitation":
                
                # plot cumulative precipitation
                fig = px.line(df, x='date', y='cumulative_precip_mm',
                              title=f"Cumulative Precipitation for {city}",
                              labels={'cumulative_precip_mm': 'Cumulative Precipitation (mm)', 'date': 'Date'})
                fig.update_traces(mode='lines+markers')
                st.plotly_chart(fig, use_container_width=True)

                # plot daily precipitation
                st.write(f"### Daily Precipitation for {city}")
                daily_precip_fig = px.bar(df, x='date', y='totalprecip_mm',
                                          title=f"Daily Precipitation for {city}",
                                          labels={'totalprecip_mm': 'Daily Precipitation (mm)', 'date': 'Date'})
                st.plotly_chart(daily_precip_fig, use_container_width=True)

                # add comparison with vegetable's optimal precipitation data
                st.write(f"### Comparing Precipitation with {veg_type.capitalize()} Needs")
                veg_data = get_veg_data()
                veg_df = pd.DataFrame(veg_data[veg_type])


                # aggregate vegetable data to get max precipitation per month
                veg_df['month'] = veg_df['month']
                veg_precip = veg_df[['month', 'precip_mm']].groupby('month').max().reset_index()
                
                # add vegetable precipitation to monthly weather data
                monthly_precip = df.resample('M', on='date').sum().reset_index()
                monthly_precip['month'] = monthly_precip['date'].dt.strftime('%B')
                monthly_precip = monthly_precip.merge(veg_precip, on='month', how='left')
                
                # create comparison bar chart
                precip_fig = go.Figure()
                precip_fig.add_trace(go.Bar(
                    x=monthly_precip['month'],
                    y=monthly_precip['totalprecip_mm'],
                    name=f'{city} Precipitation',
                    marker_color='skyblue'
                ))
                precip_fig.add_trace(go.Bar(
                    x=monthly_precip['month'],
                    y=monthly_precip['precip_mm'],
                    name=f'{veg_type.capitalize()} Optimal Precipitation',
                    marker_color=VEG_COLOUR.get(veg_type, 'green')
                ))
                precip_fig.update_layout(
                    title=f"Monthly Precipitation: {city} vs {veg_type.capitalize()}",
                    xaxis_title="Month",
                    yaxis_title="Precipitation (mm)",
                    barmode='group',
                    plot_bgcolor="rgba(255, 255, 255, 0.80)",
                    paper_bgcolor="rgba(255, 255, 255, 0.80)",
                )
                st.plotly_chart(precip_fig, use_container_width=True)

            # monthly trends analysis
            elif analysis_type == "Monthly Trends":
                fig = px.bar(monthly_df, x='month', y='avgtemp_c',
                             title=f"Monthly Average Temperature for {city}",
                             labels={'avgtemp_c': 'Average Temperature (°C)', 'month': 'Month'})
                st.plotly_chart(fig, use_container_width=True)

            # extreme temperture analysis
            elif analysis_type == "Extreme Temperatures":
                extreme_points = df[df['is_highest_temp'] | df['is_lowest_temp']]
                st.write("Extreme Temperature Days:")
                st.dataframe(extreme_points[['date', 'maxtemp_c', 'mintemp_c']])

                fig = px.scatter(extreme_points, x='date', y='maxtemp_c',
                                 color='is_highest_temp',
                                 title="Extreme Temperatures",
                                 labels={'maxtemp_c': 'Temperature (°C)', 'date': 'Date'})
                st.plotly_chart(fig, use_container_width=True)

            # veg and temp comparison
            elif analysis_type == "Vegetable and Temperature Comparison":
                fig = create_range_bar_chart(df, city, veg_type)
                st.plotly_chart(fig, use_container_width=True)

                # display the veg data frame
                st.write(f"### {veg_type.capitalize()} Growing Conditions")
                veg_data = get_veg_data()
                veg_df = pd.DataFrame(veg_data[veg_type])
                st.dataframe(veg_df)

        else:
            st.write(f"No data available for {city}. Please check the city name or try another location.")
            

if __name__ == "__main__":
    main()
