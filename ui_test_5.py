import time
import streamlit as st
import folium
import pickle
import numpy as np
from streamlit.components.v1 import html
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta
import plotly.express as px
from catboost import CatBoostClassifier
from sklearn.preprocessing import StandardScaler

import streamlit as st

st.set_page_config(
    page_title="Chicago CrimeWiz",
    page_icon=":cop:",
)


# Dummy user credentials (replace with actual authentication logic) //CONNECT TO MYSQL LATER
valid_username = "user1"
valid_password = "123"

# Load Catboost model
with open('catboost_model.pkl', 'rb') as model_file:
    catboost_model = pickle.load(model_file)

# Load StandardScaler
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Define a list of districts in Chicago
list_of_districts_in_chicago = [
    "Central", "Wentworth", "Grand Crossing", "South Chicago", "Calumet",
    "Gresham", "Englewood", "Chicago Lawn", "Deering", "Ogden",
    "Harrison", "Near West", "Wood", "Shakespeare", "Austin",
    "Jefferson Park", "Albany Park", "Near North", "Town Hall", "Morgan Park",
    "Rogers Park", "Pullman"
]

# Define the coordinates or shapes for each district
district_coordinates = {
    "Central": [41.8781, -87.6298],
    "Wentworth": [41.8525, -87.6315],
    "Grand Crossing": [41.7625, -87.6096],
    "South Chicago": [41.7399, -87.5667],
    "Calumet": [41.7300, -87.5545],
    "Gresham": [41.7500, -87.6528],
    "Englewood": [41.7798, -87.6455],
    "Chicago Lawn": [41.7750, -87.6963],
    "Deering": [41.7143, -87.6900],
    "Ogden": [41.8568, -87.6589],
    "Harrison": [41.8731, -87.7050],
    "Near West": [41.8819, -87.6638],
    "Wood": [41.7769, -87.6646],
    "Shakespeare": [41.9182, -87.6525],
    "Austin": [41.8947, -87.7654],
    "Jefferson Park": [41.9702, -87.7649],
    "Albany Park": [41.9681, -87.7234],
    "Near North": [41.9000, -87.6345],
    "Town Hall": [41.9434, -87.6703],
    "Morgan Park": [41.6908, -87.6668],
    "Rogers Park": [42.0095, -87.6768],
    "Pullman": [41.7076, -87.6096]
    # Add coordinates for other districts as needed
}

# Sidebar - EDA and Login
st.sidebar.title(":blue[Chicago CrimeWiz] 👮")
# st.sidebar.subheader("Exploratory Data Analysis")

# Display EDA visualizations and summary here

# Login
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type='password')

# Authentication logic
if st.sidebar.button("Login"):
    if username == valid_username and password == valid_password:
        st.sidebar.success("Logged in as {}".format(username))
        # Set a session variable or flag to indicate successful login
        # For simplicity, you can use st.session_state for this purpose
        st.session_state.logged_in = True
    else:
        st.sidebar.error("Invalid credentials. Please try again.")

# Selector for Navigation
navigation_option = st.sidebar.selectbox("Select Option", ["Make Predictions", "Data Analysis"])

# Main Section - Predictions and Map
st.title(":blue[Chicago CrimeWiz] 👮")


# Check if the user is logged in before allowing access to predictions and map
if getattr(st.session_state, 'logged_in', False):

    if navigation_option == "Make Predictions":
        st.subheader("Make Prediction Section")
        # User Inputs
        selected_date = st.date_input("Select Date")
        selected_location = st.selectbox("Select Location", list_of_districts_in_chicago)

        # Retrieve latitude and longitude for the selected location
        selected_latitude, selected_longitude = district_coordinates[selected_location]

        # Create a NumPy array with the selected features
        selected_features = np.array([selected_date.year, selected_date.month, selected_date.day,
                                      selected_date.weekday(), selected_latitude, selected_longitude])

        # Standardize the input using the loaded scaler
        preprocessed_input = scaler.transform(selected_features.reshape(1, -1))

        # Map Section
        st.subheader("Chicago Districts Map")

        # Create a unique ID for the map div
        map_div_id = f"map-{selected_location}"

        # Display the map div
        html(f'<div id="{map_div_id}"></div>')

        # Create a Folium map
        m = folium.Map(location=[selected_latitude, selected_longitude], zoom_start=12)

        # Add a marker to the map
        folium.Marker([selected_latitude, selected_longitude], popup=selected_location).add_to(m)

        # Display the map
        folium_static(m)

        # Predictions Button
        if st.button("See Predictions"):
            # Add a loading spinner
            with st.spinner('Making Predictions...'):
                # Simulate a delay (you can replace this with the actual prediction logic)
                time.sleep(1.2)
                # Make predictions
                predictions = catboost_model.predict(preprocessed_input)
                if predictions[0] == 1:
                    # Display the predictions
                    st.write("Predictions for {} in {}: A Violent Crime can happen".format(selected_date, selected_location))
                else:
                    st.write("Predictions for {} in {}: A Violent Crime may not happen".format(selected_date, selected_location))

    elif navigation_option == "Data Analysis":
        # Data Analysis logic goes here
        st.subheader("Data Analysis Section")
        # st.write("This is the Data Analysis section.")

        # Socrata API endpoint for Chicago crime data
        socrata_domain = "data.cityofchicago.org"
        socrata_dataset_identifier = "ijzp-q8t2"

        # Create a Socrata client
        client = Socrata(socrata_domain, None)

        # Add date and time input options
        start_date = st.date_input("Start Date", datetime(2022, 1, 1))
        end_date = st.date_input("End Date", datetime.today())

        # Convert the selected dates to strings
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

        # Build the query for the Socrata API
        query = f"date between '{start_date_str}' and '{end_date_str}'"

        # Create a spinner for loading animation
        with st.spinner("Loading data..."):
            # Fetch the data from the Socrata API
            results = client.get(socrata_dataset_identifier, where=query, limit=50000)

        # Convert the data to a DataFrame
        df = pd.DataFrame.from_records(results)

        # Convert the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Convert the 'latitude' and 'longitude' columns to numeric, filtering out non-numeric values
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        # Extract the day of the week and create a new column
        df['day_of_week'] = df['date'].dt.day_name()

        # Filter out non-numeric values before calculating the mean
        filtered_df = df[['latitude', 'longitude']].apply(pd.to_numeric, errors='coerce')

        # Display a map of crime locations for the selected time frame
        st.subheader("Crime Map for Selected Time Frame")
        st.map(filtered_df[['latitude', 'longitude']].dropna())

        # # Display the raw data for the selected time frame
        # st.subheader("Raw Data for Selected Time Frame")
        # st.write(df)

        # Display some basic statistics for the selected time frame
        st.subheader("Basic Statistics for Selected Time Frame")
        st.write(df.describe())

        # Display a bar chart of crime types for the selected time frame
        st.subheader("Crime Types for Selected Time Frame")
        crime_counts = df['primary_type'].value_counts()
        st.bar_chart(crime_counts)

        # Display the top 10 crime locations for the selected time frame
        st.subheader("Top 10 Crime Locations for Selected Time Frame")
        top_locations = df['location_description'].value_counts().head(10)
        # st.write(top_locations)

        # Create a Plotly pie chart for the top 10 crime locations
        fig_top_locations = px.pie(top_locations, names=top_locations.index, values=top_locations.values,
                                   title="Top 10 Crime Locations for Selected Time Frame")

        # Display the Plotly pie chart using st.plotly_chart
        st.plotly_chart(fig_top_locations)

        # Display a bar chart of crime counts per day of the week for the selected time frame
        st.subheader("Crime Counts per Day of the Week for Selected Time Frame")
        day_of_week_counts = df['day_of_week'].value_counts()
        st.bar_chart(day_of_week_counts, color='#ffaa00')

        # Extract the time of the day and create a new column
        df['time_of_day'] = pd.cut(df['date'].dt.hour,
                                   bins=[0, 6, 12, 18, 24],
                                   labels=['Night', 'Morning', 'Afternoon', 'Evening'],
                                   right=False)

        # Display the crime counts per time of the day with corresponding hours
        st.subheader("Crime Counts per Time of the Day for Selected Time Frame")
        time_of_day_counts = df['time_of_day'].value_counts()
        st.bar_chart(time_of_day_counts, color='#00ffaa')

        # Display the corresponding hours for each time of day
        time_of_day_hours = {
            'Night': '0:00 - 5:59',
            'Morning': '6:00 - 11:59',
            'Afternoon': '12:00 - 17:59',
            'Evening': '18:00 - 23:59'
        }

        for time_of_day, hours in time_of_day_hours.items():
            st.write(f"{time_of_day}: {hours}")

        # Extract the time of the day and create a new column
        df['hour_of_day'] = df['date'].dt.hour

        # Display the crime counts per hour of the day
        st.subheader("Crime Counts per Hour of the Day for Selected Time Frame")
        hour_of_day_counts = df['hour_of_day'].value_counts().sort_index()

        # Create a line chart using Plotly
        fig_line_chart = px.line(x=hour_of_day_counts.index, y=hour_of_day_counts.values,
                                 labels={'x': 'Hour of the Day', 'y': 'Crime Count'},
                                 title="Crime Counts per Hour of the Day")

        # Display the Plotly line chart using st.plotly_chart
        st.plotly_chart(fig_line_chart)

        # Create a space before the dropdown
        st.markdown("&nbsp;")  # Add a non-breaking space using Markdown

        # Create a dropdown to select a day of the week
        selected_day = st.selectbox("Select a Day of the Week", df['day_of_week'].unique())

        # Filter data for the selected day of the week
        selected_day_data = df[df['day_of_week'] == selected_day]

        # Display the count for the top 5 crimes for the selected day
        st.subheader(f"Top 5 Crimes on {selected_day}")
        top_crimes = selected_day_data['primary_type'].value_counts().head(5)
        # st.write(top_crimes)

        # Create a Plotly bar chart
        fig = px.bar(top_crimes, x=top_crimes.index, y=top_crimes.values,
                     labels={'x': 'Crime Type', 'y': 'Crime Count'},
                     title=f"Top 5 Crimes on {selected_day}")

        # Display the Plotly bar chart using st.plotly_chart
        st.plotly_chart(fig)



else:
    st.warning("Please log in to access predictions and the map.")
