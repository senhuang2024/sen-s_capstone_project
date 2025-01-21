import requests
import os
from dotenv import load_dotenv
import psycopg2 


load_dotenv()
weather_api_key = os.getenv("API_KEY")


# base url setup
base_url = "http://api.weatherapi.com/v1"
endpoint = "/current.json"
location = "bristol"


#complete url
url = f"{base_url}{endpoint}?key={weather_api_key}&q={location}"

print(url)

response_json = requests.get(url)
response_data = response_json.json()
print(response_data)

###------------------------------------------------Creating Table in Postgres---------------------------------------------------------------------------------------

import psycopg2
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()
weather_api_key = os.getenv("API_KEY")

# Database connection parameters
db_user = os.getenv('SOURCE_DB_USER')
db_password = os.getenv('SOURCE_DB_PASSWORD')
db_host = os.getenv('SOURCE_DB_HOST')
db_port = os.getenv('SOURCE_DB_PORT')
db_name = os.getenv('SOURCE_DB_NAME')

# Create connection and cursor
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
cursor = conn.cursor()

# Set the schema


# SQL to create a table
create_table_query = """
CREATE TABLE IF NOT EXISTS student.weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255),
    region VARCHAR(255),
    country VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    timezone_id VARCHAR(100),
    localtime_epoch BIGINT,
    temp_c FLOAT,
    condition_text VARCHAR(100),
    wind_mph FLOAT,
    wind_dir VARCHAR(10),
    pressure_mb FLOAT,
    precip_mm FLOAT,
    humidity INTEGER,
    feelslike_c FLOAT,
    visibility_miles FLOAT,
    uv_index FLOAT
);
"""

# Execute the SQL command to create the table
cursor.execute(create_table_query)
conn.commit()  # Commit the transaction

# API request
base_url = "http://api.weatherapi.com/v1"
endpoint = "/current.json"
location = "bristol"
url = f"{base_url}{endpoint}?key={weather_api_key}&q={location}"

response = requests.get(url)
response_data = response.json()

# Prepare insert statement
insert_stmt = """
INSERT INTO student.weather_data (
    city, region, country, latitude, longitude, timezone_id, localtime_epoch,
    temp_c, condition_text, wind_mph, wind_dir,
    pressure_mb, precip_mm, humidity, feelslike_c, visibility_miles, uv_index
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Data to be inserted
data = (
    response_data['location']['name'],
    response_data['location']['region'],
    response_data['location']['country'],
    response_data['location']['lat'],
    response_data['location']['lon'],
    response_data['location']['tz_id'],
    response_data['location']['localtime_epoch'],
    response_data['current']['temp_c'],
    response_data['current']['condition']['text'],
    response_data['current']['wind_mph'],
    response_data['current']['wind_dir'],
    response_data['current']['pressure_mb'],
    response_data['current']['precip_mm'],
    response_data['current']['humidity'],
    response_data['current']['feelslike_c'],
    response_data['current']['vis_miles'],
    response_data['current']['uv']
)

# Execute the insertion
cursor.execute(insert_stmt, data)
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("Data inserted successfully.")
