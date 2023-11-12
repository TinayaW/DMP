import streamlit as st
import folium
from streamlit_folium import folium_static

# Dummy user credentials (replace with actual authentication logic)
valid_username = "policeuser"
valid_password = "securepassword"

# Define a list of districts in Chicago
list_of_districts_in_chicago = [
    "Central", "Wentworth", "Grand Crossing", "South Chicago", "Calumet",
    "Gresham", "Englewood", "Chicago Lawn", "Deering", "Ogden",
    "Harrison", "Near West", "Wood", "Shakespeare", "Austin",
    "Jefferson Park", "Albany Park", "Near North", "Town Hall", "Morgan Park",
    "Rogers Park", "Pullman"
]

# Define the coordinates or shapes for each district (replace with actual data)
district_coordinates = {
    "Central": [(-87.6274, 41.8781), (-87.6266, 41.8781), (-87.6266, 41.8785), (-87.6274, 41.8785)],
    "Wentworth": [(-87.6315, 41.8525), (-87.6307, 41.8525), (-87.6307, 41.8529), (-87.6315, 41.8529)],
    "Grand Crossing": [(-87.6096, 41.7625), (-87.6088, 41.7625), (-87.6088, 41.7629), (-87.6096, 41.7629)],
    # ... coordinates for other districts ...
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

    # Predictions Button
    if st.button("See Predictions"):
        # Implement prediction logic and display results using st.write()
        st.write("Predictions for {} in {}".format(selected_date, selected_location))

    # Map Section
    st.subheader("Chicago Districts Map")

    # Create a folium map centered around Chicago
    chicago_map = folium.Map(location=[41.8781, -87.6298], zoom_start=10)

    # Add polygons for each district on the map
    for district, coordinates in district_coordinates.items():
        folium.Polygon(locations=coordinates, color='blue', fill=True, fill_color='blue', fill_opacity=0.2,
                       weight=2).add_to(chicago_map)

    # Highlight the selected district
    if selected_location in district_coordinates:
        selected_coordinates = district_coordinates[selected_location]
        folium.Polygon(locations=selected_coordinates, color='red', fill=True, fill_color='red', fill_opacity=0.4,
                       weight=2).add_to(chicago_map)

    # Display the map
    folium_static(chicago_map)
else:
    st.warning("Please log in to access predictions and the map.")
