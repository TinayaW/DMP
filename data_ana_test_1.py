import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load Chicago crime data from the CSV file
data_url = "https://data.cityofchicago.org/resource/ijzp-q8t2.csv"
df = pd.read_csv(data_url)

# Convert the 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Display the title and a brief description
st.title("Chicago Crime Data EDA")
st.write("Exploratory Data Analysis of Chicago Crime Data")

# Add date input options
start_date = st.date_input("Start Date", min(df['date'])).strftime('%Y-%m-%d')
end_date = st.date_input("End Date", max(df['date'])).strftime('%Y-%m-%d')

# Convert the selected dates to Pandas Timestamp objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter the data based on the selected time frame
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Extract the day of the week and create a new column
filtered_df['day_of_week'] = filtered_df['date'].dt.day_name()

# Display the raw data for the selected time frame
st.subheader("Raw Data for Selected Time Frame")
st.write(filtered_df)

# Display some basic statistics for the selected time frame
st.subheader("Basic Statistics for Selected Time Frame")
st.write(filtered_df.describe())

# Display a bar chart of crime types for the selected time frame
st.subheader("Crime Types for Selected Time Frame")
crime_counts = filtered_df['primary_type'].value_counts()
st.bar_chart(crime_counts)

# Create a DataFrame with all days of the week
all_days_of_week = pd.DataFrame({'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})

# Merge with calculated crime counts
day_of_week_counts = all_days_of_week.merge(filtered_df['day_of_week'].value_counts().reset_index(), how='left', left_on='day_of_week', right_on='index').rename(columns={'day_of_week_x': 'day_of_week', 0: 'crime_count'}).fillna(0)

# Display a bar chart of crime counts per day of the week for the selected time frame
st.subheader("Crime Counts per Day of the Week for Selected Time Frame")
st.bar_chart(day_of_week_counts.set_index('day_of_week')['crime_count'])

# Display a map of crime locations for the selected time frame
st.subheader("Crime Map for Selected Time Frame")
st.map(filtered_df[['latitude', 'longitude']].dropna())
