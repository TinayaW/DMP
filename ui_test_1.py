import streamlit as st
import folium
from streamlit_folium import folium_static


# Dummy user credentials (replace with actual authentication logic)
valid_username = "user1"
valid_password = "123"

# Define a list of districts in Chicago
list_of_districts_in_chicago = ["District 1", "District 2", "District 3", "District 4", ...]

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

    # Add markers or polygons for each district on the map
    # Replace this with actual coordinates or shapes for each district
    for district in list_of_districts_in_chicago:
        folium.Marker(location=[41.8781, -87.6298], popup=district).add_to(chicago_map)

    # Display the map
    folium_static(chicago_map)
else:
    st.warning("Please log in to access predictions and the map.")
