import streamlit as st
import pandas as pd
from sodapy import Socrata
from datetime import datetime

# Socrata API endpoint for Chicago crime data
socrata_domain = "data.cityofchicago.org"
socrata_dataset_identifier = "ijzp-q8t2"

# Create a Socrata client
client = Socrata(socrata_domain, None)

# Add date input options
start_date = st.date_input("Start Date", datetime(2022, 1, 1))
end_date = st.date_input("End Date", datetime.today())

# Convert the selected dates to strings
start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

# Build the query for the Socrata API
query = f"date between '{start_date_str}' and '{end_date_str}'"

# Fetch the data from the Socrata API
results = client.get(socrata_dataset_identifier, where=query, limit=50000)

# Convert the data to a DataFrame
df = pd.DataFrame.from_records(results)

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Display the raw data for the selected time frame
st.subheader("Raw Data for Selected Time Frame")
st.write(df)

# Display some basic statistics for the selected time frame
st.subheader("Basic Statistics for Selected Time Frame")
st.write(df.describe())

# Display a bar chart of crime types for the selected time frame
st.subheader("Crime Types for Selected Time Frame")
crime_counts = df['primary_type'].value_counts()
st.bar_chart(crime_counts)

# Extract the day of the week and create a new column
df['day_of_week'] = df['date'].dt.day_name()

# Display a bar chart of crime counts per day of the week for the selected time frame
st.subheader("Crime Counts per Day of the Week for Selected Time Frame")
day_of_week_counts = df['day_of_week'].value_counts()
st.bar_chart(day_of_week_counts)

# Display a map of crime locations for the selected time frame
st.subheader("Crime Map for Selected Time Frame")
st.map(df[['latitude', 'longitude']].dropna())
