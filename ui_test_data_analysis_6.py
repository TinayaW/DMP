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

# Convert the 'latitude' and 'longitude' columns to numeric, filtering out non-numeric values
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Extract month and year from the 'date' column
df['month_year'] = df['date'].dt.to_period('M')

# Aggregate crime counts on a monthly basis
monthly_crime_counts = df['month_year'].value_counts().sort_index().reset_index()
monthly_crime_counts.columns = ['Month-Year', 'Crime Count']

# Convert 'Period' to string for serialization
monthly_crime_counts['Month-Year'] = monthly_crime_counts['Month-Year'].astype(str)

# Display a bar chart for temporal trends
st.subheader("Temporal Trends: Monthly Crime Counts")
fig = px.bar(monthly_crime_counts, x='Month-Year', y='Crime Count', labels={'Month-Year': 'Month-Year', 'Crime Count': 'Crime Count'}, title="Monthly Crime Counts Over Time")
st.plotly_chart(fig)
