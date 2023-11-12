import streamlit as st
import folium
from streamlit_folium import folium_static

# Dummy user credentials (replace with actual authentication logic)
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

# Define the coordinates or shapes for each district (replace with actual data)
district_coordinates = {
    "Central": [(-87.6274, 41.8781), (-87.6266, 41.8781), (-87.6266, 41.8785), (-87.6274, 41.8785)],
    "Wentworth": [(-87.6315, 41.8525), (-87.6307, 41.8525), (-87.6307, 41.8529), (-87.6315, 41.8529)],
    "Grand Crossing": [(-87.6096, 41.7625), (-87.6088, 41.7625), (-87.6088, 41.7629), (-87.6096, 41.7629)],
    "South Chicago": [(-87.5642, 41.7284), (-87.5634, 41.7284), (-87.5634, 41.7288), (-87.5642, 41.7288)],
    "Calumet": [(-87.5974, 41.7301), (-87.5966, 41.7301), (-87.5966, 41.7305), (-87.5974, 41.7305)],
    "Gresham": [(-87.6562, 41.7517), (-87.6554, 41.7517), (-87.6554, 41.7521), (-87.6562, 41.7521)],
    "Englewood": [(-87.6415, 41.7784), (-87.6407, 41.7784), (-87.6407, 41.7788), (-87.6415, 41.7788)],
    "Chicago Lawn": [(-87.6952, 41.7725), (-87.6944, 41.7725), (-87.6944, 41.7729), (-87.6952, 41.7729)],
    "Deering": [(-87.6966, 41.8101), (-87.6958, 41.8101), (-87.6958, 41.8105), (-87.6966, 41.8105)],
    "Ogden": [(-87.6807, 41.8598), (-87.6799, 41.8598), (-87.6799, 41.8602), (-87.6807, 41.8602)],
    "Harrison": [(-87.6307, 41.8738), (-87.6299, 41.8738), (-87.6299, 41.8742), (-87.6307, 41.8742)],
    "Near West": [(-87.6749, 41.8804), (-87.6741, 41.8804), (-87.6741, 41.8808), (-87.6749, 41.8808)],
    "Wood": [(-87.6715, 41.9084), (-87.6707, 41.9084), (-87.6707, 41.9088), (-87.6715, 41.9088)],
    "Shakespeare": [(-87.6807, 41.9188), (-87.6799, 41.9188), (-87.6799, 41.9192), (-87.6807, 41.9192)],
    "Austin": [(-87.7743, 41.8885), (-87.7735, 41.8885), (-87.7735, 41.8889), (-87.7743, 41.8889)],
    "Jefferson Park": [(-87.7634, 41.9784), (-87.7626, 41.9784), (-87.7626, 41.9788), (-87.7634, 41.9788)],
    "Albany Park": [(-87.7197, 41.9688), (-87.7189, 41.9688), (-87.7189, 41.9692), (-87.7197, 41.9692)],
    "Near North": [(-87.6299, 41.9115), (-87.6291, 41.9115), (-87.6291, 41.9119), (-87.6299, 41.9119)],
    "Town Hall": [(-87.6537, 41.9738), (-87.6529, 41.9738), (-87.6529, 41.9742), (-87.6537, 41.9742)],
    "Morgan Park": [(-87.6715, 41.6892), (-87.6707, 41.6892), (-87.6707, 41.6896), (-87.6715, 41.6896)],
    "Rogers Park": [(-87.6691, 42.0125), (-87.6683, 42.0125), (-87.6683, 42.0129), (-87.6691, 42.0129)],
    "Pullman": [(-87.606, 41.7029), (-87.6052, 41.7029), (-87.6052, 41.7033), (-87.606, 41.7033)],
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

    # Create a folium map centered around Chicago
    chicago_map = folium.Map(location=[41.8781, -87.6298], zoom_start=10)

    # Add polygons for each district on the map
    for district, coordinates in district_coordinates.items():
        folium.GeoJson(
            {
                'type': 'Polygon',
                'coordinates': [coordinates],
            },
            style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.2},
        ).add_to(chicago_map)

    # Highlight the selected district in red using Marker
    if selected_location in district_coordinates:
        selected_coordinates = [sum(c[1] for c in coordinates) / len(coordinates),
                                sum(c[0] for c in coordinates) / len(coordinates)]
        folium.Marker(
            location=selected_coordinates,
            popup=f"{selected_location} (Selected)",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(chicago_map)

    # Display the map
    folium_static(chicago_map)

    # Predictions Button
    if st.button("See Predictions"):
        # Implement prediction logic and display results using st.write()
        st.write("Predictions for {} in {}".format(selected_date, selected_location))

else:
    st.warning("Please log in to access predictions and the map.")
