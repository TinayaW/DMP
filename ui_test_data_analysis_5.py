import streamlit as st
import pandas as pd
from sodapy import Socrata
from datetime import datetime
import plotly.express as px

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

# Create a sidebar expander for raw data
with st.beta_expander("Raw Data for Selected Time Frame", expanded=True):
    st.write(df)

# Create a sidebar expander for basic statistics
with st.beta_expander("Basic Statistics for Selected Time Frame", expanded=True):
    st.write(df.describe())

# Display a bar chart of crime types for the selected time frame
st.subheader("Crime Types for Selected Time Frame")
crime_counts = df['primary_type'].value_counts()
st.bar_chart(crime_counts)

# Display a bar chart of crime counts per day of the week for the selected time frame
st.subheader("Crime Counts per Day of the Week for Selected Time Frame")
day_of_week_counts = df['day_of_week'].value_counts()
st.bar_chart(day_of_week_counts, color = 'green')

# Create a dropdown to select a day of the week
selected_day = st.selectbox("Select a Day of the Week", df['day_of_week'].unique())

# Filter data for the selected day of the week
selected_day_data = df[df['day_of_week'] == selected_day]

# Display the count for the top 5 crimes for the selected day
st.subheader(f"Top 5 Crimes on {selected_day}")
top_crimes = selected_day_data['primary_type'].value_counts().head(5)
st.write(top_crimes)

# Create a Plotly bar chart
fig = px.bar(top_crimes, x=top_crimes.index, y=top_crimes.values,
             labels={'x': 'Crime Type', 'y': 'Crime Count'},
             title=f"Top 5 Crimes on {selected_day}")

# Display the Plotly bar chart using st.plotly_chart
st.plotly_chart(fig)
