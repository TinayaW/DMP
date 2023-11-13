import sqlite3
import hashlib  # For hashing passwords
import streamlit as st

# SQLite connection
conn = sqlite3.connect('user_credentials.db')
cursor = conn.cursor()

# Create a table to store user credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify passwords
def verify_password(entered_password, hashed_password):
    return hashlib.sha256(entered_password.encode()).hexdigest() == hashed_password

# Sidebar - EDA and Login
st.sidebar.title(":blue[Chicago CrimeWiz] 👮")
# ... (Remaining sidebar code remains unchanged)

# Login and Registration Section in the Sidebar
login_option = st.sidebar.radio("Select Option", ["Login", "Register"])

if login_option == "Login":
    # Login
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')

    if st.sidebar.button("Login"):
        select_query = "SELECT password FROM users WHERE username = ?"
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()

        if result:
            hashed_password_from_db = result[0]

            if verify_password(password, hashed_password_from_db):
                st.sidebar.success("Logged in as {}".format(username))
                st.session_state.logged_in = True
            else:
                st.sidebar.error("Invalid password. Please try again.")
        else:
            st.sidebar.error("Username not found. Please register.")

elif login_option == "Register":
    # Registration
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')

    if st.sidebar.button("Register"):
        hashed_password = hash_password(new_password)

        insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
        values = (new_username, hashed_password)

        cursor.execute(insert_query, values)
        conn.commit()

        st.sidebar.success("Registration successful. You can now log in.")

# ... (Remaining code remains unchanged)

# Main Section - Predictions and Map
st.title(":blue[Chicago CrimeWiz] 👮")

# Check if the user is logged in before allowing access to predictions and map
if getattr(st.session_state, 'logged_in', False):
    st.write("You are logged in.")

# Close the SQLite connection when done
conn.close()
