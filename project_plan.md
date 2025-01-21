#### Project Overview - Dynamic Weather Travel Planner

Objective:

To develop a dynamic weather data application that leverages real-time and forecasted weather information from WeatherAPI. This application aims to provide users with up-to-date weather insights and visualisations that assist in making informed travel decisions. By offering precise and timely weather details, the application enhances travel planning efficiency and effectiveness, enabling users to anticipate and adapt to weather conditions for upcoming trips.

Goals:

Data Acquisition: Automatically extract live and forecasted weather data frequently to ensure the application reflects current conditions and near-future predictions.
Data Storage: Efficiently store the extracted data in a structured SQL database, focusing on incremental updates to minimise resource usage.
Data Visualisation: Implement interactive and informative visualisations that highlight weather patterns and their implications for travel planning.
User Interaction: Design an intuitive user interface in Streamlit that allows users to easily access, interact with, and understand the weather data relevant to their travel needs.

Target Users:

Travelers: Individuals planning trips who need to understand weather conditions for specific dates and destinations.
Travel Analysts: Professionals analysing trends in travel destinations related to weather conditions.
Event Planners: Coordinators organising outdoor or location-specific events who need to plan based on weather forecasts.

#### User Requirements

| Epic                                             | User Requirements                                                                                     |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Epic 1: Real-Time Weather Data Extraction**    | Develop a script to fetch current and forecasted weather data at frequent intervals.                  |
|                                                  | Implement logic to identify and fetch only new or updated data since the last extraction (delta data).|
| **Epic 2: Efficient Data Management**            | Data must be stored in an SQL database (DBeaver-Pagila) with a focus on incremental updates to optimise storage.       |
|                                                  | Develop a schema that supports quick queries and data retrieval for the application.                  |
| **Epic 3: Interactive Data Visualisation**       | Create dynamic visualisations in Streamlit that display current and forecasted weather data.          |
|                                                  | Visualisations should allow users to select different locations and dates for travel planning.        |
| **Epic 4: User-Friendly Interface Design**       | Design an intuitive interface in Streamlit that is easy for all users to navigate and use.            |   |
