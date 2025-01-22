import streamlit as st
import psycopg2
import pandas as pd
import os
import datetime
from dotenv import load_dotenv
from current import insert_current

# Load environment variables
load_dotenv()
db_user = os.getenv('SOURCE_DB_USER')
db_password = os.getenv('SOURCE_DB_PASSWORD')
db_host = os.getenv('SOURCE_DB_HOST')
db_port = os.getenv('SOURCE_DB_PORT')
db_name = os.getenv('SOURCE_DB_NAME')

# Function to connect to the database
def connect_to_db():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn

# Function to get data
def get_temperature_data(location="Bristol"):
    conn = connect_to_db()
    current_query = '''
    SELECT city, date, AVG(temp_c) AS avgtemp_c
    FROM student.weather_data
    WHERE city = '{location}' AND date >= '{date}'
    GROUP BY city, date
    '''.format(location = location, date = datetime.date.today())
    
    current_df = pd.read_sql(current_query, conn)
    
    print(current_df)
    
    history_query = """
    SELECT city, date, avgtemp_c 
    FROM student.de11_fehu_capstone 
    WHERE city = '{location}'
    ORDER BY date;
    """.format(location = location)
    
    history_df = pd.read_sql(history_query, conn)
    print(history_df)
    df = pd.concat([history_df,current_df]).reset_index()
    conn.close()
    print(df)
    return df

def get_location():
    user_input = st.text_input("Enter City")
    return user_input

# Streamlit app
def main():
    
    city = get_location()
    if st.button("about to fly?"):
        insert_current(city)
    
        st.title('Average Temperature Over Time')
        df = get_temperature_data(city)

        if not df.empty:
            st.line_chart(df.set_index('date'),y='avgtemp_c')
        else:
            st.write("No data available.")


if __name__ == "__main__":
    main()

