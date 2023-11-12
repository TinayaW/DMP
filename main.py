import streamlit as st

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

# Main Section - Predictions
st.title("Crime Predictions")

# Check if the user is logged in before allowing access to predictions
if getattr(st.session_state, 'logged_in', False):
    # User Inputs
    selected_date = st.date_input("Select Date")
    selected_location = st.selectbox("Select Location", list_of_districts_in_chicago)

    # Predictions Button
    if st.button("See Predictions"):
        # Implement prediction logic and display results using st.write()
        st.write("Predictions for {} in {}".format(selected_date, selected_location))
else:
    st.warning("Please log in to access predictions.")
