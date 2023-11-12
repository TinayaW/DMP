import streamlit as st
import folium
from streamlit.components.v1 import html

# Dummy user credentials (replace with actual authentication logic)
from streamlit_folium import folium_static

valid_username = "user1"
valid_password = "123"

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
st.sidebar.title("Chicago CrimeWiz")
st.sidebar.subheader("Exploratory Data Analysis")

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

# Main Section - Predictions and Map
st.title("Chicago CrimeWiz")

# Check if the user is logged in before allowing access to predictions and map
if getattr(st.session_state, 'logged_in', False):
    # User Inputs
    selected_date = st.date_input("Select Date")
    selected_location = st.selectbox("Select Location", list_of_districts_in_chicago)

    # Map Section
    st.subheader("Chicago Districts Map")

    # Create a unique ID for the map div
    map_div_id = f"map-{selected_location}"

    # Display the map div
    html(f'<div id="{map_div_id}"></div>')

    # Create a Folium map
    m = folium.Map(location=district_coordinates[selected_location], zoom_start=12)

    # Add a marker to the map
    folium.Marker(district_coordinates[selected_location], popup=selected_location).add_to(m)

    # Display the map
    folium_static(m)

    # Predictions Button
    if st.button("See Predictions"):
        # Implement prediction logic and display results using st.write()
        st.write("Predictions for {} in {}".format(selected_date, selected_location))

else:
    st.warning("Please log in to access predictions and the map.")
