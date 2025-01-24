import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from current import insert_current
import datetime
import plotly.express as px
import plotly.graph_objects as go
from vegtables import get_veg_data, VEG_COLOUR
import base64
st.set_page_config(layout="wide")

# set the background image for stramlit
def set_background(image_file):
    """
    Adds a background image to both the main app and the sidebar in the Streamlit app.
    """
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

# set the top right image for stramlit
def add_top_right_image(image_file):
    """
    Adds an image in the top-right corner of the Streamlit app.
    """
    with open(image_file, "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode()

    css_code = f"""
    <style>
    .top-right-image {{
        position: absolute;
        top: 10px; /* Adjust the distance from the top */
        right: 10px; /* Adjust the distance from the right */
        width: 100px; /* Set the width of the image */
        z-index: 10; /* Make sure it appears above other elements */
    }}
    </style>
    <img class="top-right-image" src="data:image/png;base64,{b64_image}" alt="Top Right Image">
    """
    st.markdown(css_code, unsafe_allow_html=True)


# Load environment variables
load_dotenv()
db_user = os.getenv('SOURCE_DB_USER')
db_password = os.getenv('SOURCE_DB_PASSWORD')
db_host = os.getenv('SOURCE_DB_HOST')
db_port = os.getenv('SOURCE_DB_PORT')
db_name = os.getenv('SOURCE_DB_NAME')

# connect to the database
def connect_to_db():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

# get temperature and other weather data
def get_weather_data(location="Bristol"):
    conn = connect_to_db()
    query = f"""
    SELECT city, date, avgtemp_c, maxtemp_c, mintemp_c, totalprecip_mm, uv_index
    FROM student.de11_fehu_capstone
    WHERE city = '{location}'
    ORDER BY date ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

    



# ----------------------------------------------------------------------------------- Streamlit app-----------------------------------------------------------------------------------

# create a bar chart where each bar is from min to max temp
def create_range_bar_chart(df,city,veg):

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
        width= 0.5,
        x=monthly_data['month'],
        y=monthly_data['maxtemp_c'] - monthly_data['mintemp_c'],  
        base=monthly_data['mintemp_c'],  
        name='Recorded City Temperature Range',
        marker=dict(color='skyblue'),
        hoverinfo='x+y',  
        opacity=0.75
    ))
    
    fig.add_trace(go.Bar(
        width= 0.3,
        x=veg_data[veg]['month'],
        y=veg_data[veg]['maxtemp_c'] - veg_data[veg]['mintemp_c'],  
        base=veg_data[veg]['mintemp_c'],  
        name=f'Optimal {veg} Temperature Range',
        marker=dict(color=VEG_COLOUR.get(veg,"green")),
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
def get_location():
    user_input = st.sidebar.text_input("Enter City", value="Bristol")
    return user_input


def main():
    
   
    set_background("../../docs/background.png")
    add_top_right_image("../../docs/sun.png")

    st.sidebar.title("Weather Data Analysis")
    city = get_location()

    analysis_type = st.sidebar.selectbox("Select Analysis Type", [
        "Temperature Overview", "Precipitation", "UV Index" , "Correlation: Temperature vs UV Index", "Correlation: Temperature vs Precipitation"
    ])
    
    veg_type = st.sidebar.selectbox("Select Vegetable/Fruit Type", get_veg_data().keys())

    if st.sidebar.button("Fetch Weather Data"):
        insert_current(city) 
        df = get_weather_data(city)
        if not df.empty:
            if analysis_type == "Temperature Overview":
                fig = px.line(df, x='date', y=['avgtemp_c', 'maxtemp_c', 'mintemp_c'],
                              labels={'value': 'Temperature (°C)', 'variable': 'Temperature Type', 'date': 'Date'},
                              title=f"Temperature Overview for {city}")

                fig.update_layout(
                    width=1500,  
                    height=600,   
                    plot_bgcolor="rgba(255, 255, 255, 0.80)", 
                    paper_bgcolor="rgba(255, 255, 255, 0.80)", 
                )
                st.plotly_chart(fig, use_container_width=True)
                
                
                if veg_type:
                    fig = create_range_bar_chart(df,city,veg_type)
                    st.plotly_chart(fig, use_container_width=True)

            elif analysis_type == "Precipitation":
                fig = px.bar(df, x='date', y='totalprecip_mm', title=f"Daily Precipitation for {city}",
                             labels={'totalprecip_mm': 'Precipitation (mm)', 'date': 'Date'})
              
                fig.update_layout(
                    width=1500, 
                    height=600,   
                    plot_bgcolor="rgba(255, 255, 255, 0.80)",  
                    paper_bgcolor="rgba(255, 255, 255, 0.80)", 
                )
                st.plotly_chart(fig, use_container_width=True)

            elif analysis_type == "UV Index":
                fig = px.line(df, x='date', y='uv_index', title=f"Daily UV Index for {city}",
                              labels={'uv_index': 'UV Index', 'date': 'Date'})
                
                fig.update_layout(
                    width=1500,  
                    height=600,   
                    plot_bgcolor="rgba(255, 255, 255, 0.80)",  
                    paper_bgcolor="rgba(255, 255, 255, 0.80)", 
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif analysis_type == "Correlation: Temperature vs UV Index":
                
                correlation = df['avgtemp_c'].corr(df['uv_index'])

                
                st.write(f"### Correlation Between Temperature and UV Index: {correlation:.2f}")

                
                fig = px.scatter(
                    df,
                    x='avgtemp_c',
                    y='uv_index',
                    trendline='ols',  
                    labels={'avgtemp_c': 'Average Temperature (°C)', 'uv_index': 'UV Index'},
                    title=f"Correlation Between Temperature and UV Index for {city}"
                )
                
                fig.update_layout(
                    width=1500,  
                    height=600,  
                    plot_bgcolor="rgba(255, 255, 255, 0.80)",  
                    paper_bgcolor="rgba(255, 255, 255, 0.80)", 
                )
                st.plotly_chart(fig, use_container_width=True)
                
                
            elif analysis_type == "Correlation: Temperature vs Precipitation":
                
                correlation = df['avgtemp_c'].corr(df['totalprecip_mm'])

                
                st.write(f"### Correlation Between Temperature and Precipitation: {correlation:.2f}")

                
                fig = px.scatter(
                    df,
                    x='avgtemp_c',
                    y='totalprecip_mm',
                    trendline='ols',  
                    labels={'avgtemp_c': 'Average Temperature (°C)', 'totalprecip_mm': 'Precipitation'},
                    title=f"Correlation Between Temperature and Precipitation for {city}"
                )
                
                
                fig.update_layout(
                    width=1500, 
                    height=600,   
                    plot_bgcolor="rgba(255, 255, 255, 0.80)",  
                    paper_bgcolor="rgba(255, 255, 255, 0.80)", 
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.write("No data available.")



if __name__ == "__main__":
    main()
