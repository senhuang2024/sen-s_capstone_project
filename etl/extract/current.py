import requests
import os
from dotenv import load_dotenv
import psycopg2 
from datetime import datetime

##------------------------------------------------Create database-------------------------------------------------------------------------------------

def initialize_db():
    

    # Load environment variables
    load_dotenv()
    
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
        last_updated TIMESTAMP,
        date DATE,
        temp_c FLOAT,
        wind_mph FLOAT,
        precip_mm FLOAT,
        humidity INTEGER,
        feelslike_c FLOAT,
        uv_index FLOAT
    );
    """
    # Execute the SQL command to create the table
    cursor.execute(create_table_query)
    conn.commit()  # Commit the transaction

def insert_current(location="Bristol"):
    # API request
    
    initialize_db()
    
    weather_api_key = os.getenv("API_KEY")
    base_url = "http://api.weatherapi.com/v1"
    endpoint = "/current.json"
    url = f"{base_url}{endpoint}?key={weather_api_key}&q={location}"

    response = requests.get(url)
    response_data = response.json()
    if response.status_code == 200:
        response_data = response.json()

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
        
        # Prepare insert statement
        insert_stmt = """
        INSERT INTO student.weather_data (
            city, region, country, latitude, longitude, timezone_id, localtime_epoch,
            last_updated, date, temp_c, wind_mph, precip_mm, humidity, feelslike_c, uv_index
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Data to be inserted
        data = (
            response_data['location']['name'],
            response_data['location']['region'],
            response_data['location']['country'],
            float(response_data['location']['lat']),
            float(response_data['location']['lon']),
            response_data['location']['tz_id'],
            response_data['location']['localtime_epoch'],
            datetime.strptime(response_data['current']['last_updated'], '%Y-%m-%d %H:%M'),
            datetime.strptime(response_data['current']['last_updated'], '%Y-%m-%d %H:%M').date(),
            response_data['current']['temp_c'],
            response_data['current']['wind_mph'],
            response_data['current']['precip_mm'],
            response_data['current']['humidity'],
            response_data['current']['feelslike_c'],
            response_data['current']['uv']
        )

        # Execute the insertion
        cursor.execute(insert_stmt, data)
        conn.commit()

        print("Data inserted successfully.")
    else:
        print(f"Failed to retrieve data: HTTP Status Code {response.status_code}")

    # Close the connection
    cursor.close()
    conn.close()
    
    
def main():
    insert_current()
if __name__ == "__main__":
    main()
