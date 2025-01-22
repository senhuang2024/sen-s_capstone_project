#### Extraction Script Instructions

##### API Key and database connection configuration are stored in the .env file

1. Download the .env file in the NOODLE submission file

2. To extract the weather data from weatherapi, api key is provided in the .env file.

3. To store the extracted data onto DBeaver - pagila and within the student schema, connection parameters are provided in the .env file.

4. cd into etl/extract folder to Run the current.py script: python current.py in the gitbash terminal. It should add a new entry into the pagila database within the student.weather_data table.


##### Chron detail

Run the script every hour

