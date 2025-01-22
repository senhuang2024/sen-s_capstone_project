import requests
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()
weather_api_key = os.getenv("API_KEY")
db_user = os.getenv('SOURCE_DB_USER')
db_password = os.getenv('SOURCE_DB_PASSWORD')
db_host = os.getenv('SOURCE_DB_HOST')
db_port = os.getenv('SOURCE_DB_PORT')
db_name = os.getenv('SOURCE_DB_NAME')

# Base URL setup
base_url = "http://api.weatherapi.com/v1"
endpoint = "/history.json"
location = "bristol"
date = "2025-01-08"
end_date = "2025-01-21"

# Complete URL
url = f"{base_url}{endpoint}?key={weather_api_key}&q={location}&dt={date}&end_dt={end_date}"

# Make API request
response = requests.get(url)
if response.status_code == 200:
    response_data = response.json()

    # Create connection and cursor
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cursor = conn.cursor()

    # SQL to create a table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS student.de11_fehu_capstone (
        id SERIAL PRIMARY KEY,
        city VARCHAR(255),
        region VARCHAR(255),
        country VARCHAR(255),
        latitude FLOAT,
        longitude FLOAT,
        timezone_id VARCHAR(100),
        localtime_epoch BIGINT,
        date DATE,
        maxtemp_c FLOAT,
        mintemp_c FLOAT,
        avgtemp_c FLOAT,
        totalprecip_mm FLOAT,
        uv_index INTEGER
    );
    """
    cursor.execute(create_table_query)
    conn.commit()  # Commit the transaction

    # Prepare insert statement for weather data
    insert_stmt = """
    INSERT INTO student.de11_fehu_capstone (
        city, region, country, latitude, longitude, timezone_id, localtime_epoch,
        date, maxtemp_c, mintemp_c, avgtemp_c, totalprecip_mm, uv_index
    ) VALUES %s;
    """

    # Data to be inserted, extracting from the appropriate location and forecast sections
    data_tuples = [
        (
            response_data['location']['name'],
            response_data['location']['region'],
            response_data['location']['country'],
            response_data['location']['lat'],
            response_data['location']['lon'],
            response_data['location']['tz_id'],
            response_data['location']['localtime_epoch'],
            forecast_day['date'],
            forecast_day['day']['maxtemp_c'],
            forecast_day['day']['mintemp_c'],
            forecast_day['day']['avgtemp_c'],
            forecast_day['day']['totalprecip_mm'],
            forecast_day['day']['uv']
        ) for forecast_day in response_data['forecast']['forecastday']
    ]

    # Execute the insertion using execute_values for batch insertion
    execute_values(cursor, insert_stmt, data_tuples)
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

    print("Data inserted successfully.")
else:
    print(f"Failed to retrieve data: HTTP Status Code {response.status_code}")
