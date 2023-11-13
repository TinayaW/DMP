# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
#
# # Load the forecasting model
# with open('forecaster_model.pkl', 'rb') as forecaster_file:
#     forecaster_model = pickle.load(forecaster_file)
#
#
# def generate_forecast(future_dates):
#     # Create a DataFrame for future dates
#     future_df = pd.DataFrame({'date': future_dates})
#
#     fh_values = len(future_dates)
#
#     # Initialize an empty list to store predictions
#     future_predictions = []
#
#     for i in range(0, fh_values):
#         prediction = forecaster_model.predict(fh=i)
#
#         # Extract numerical value from DataFrame
#         if isinstance(prediction, pd.DataFrame):
#             # Assuming your DataFrame has a numerical column, adjust 'your_column_name' accordingly
#             prediction = prediction['y'].iloc[0]
#
#         # Flatten nested arrays or sequences
#         if isinstance(prediction, (list, np.ndarray)):
#             prediction = np.mean(prediction)  # Take the mean value for simplicity
#         else:
#             prediction = float(prediction)
#
#         future_predictions.append(prediction)
#
#     # Assign the list of predictions to the 'predicted_crime_rate' column
#     future_df['predicted_crime_rate'] = future_predictions
#
#     return future_df
#
#
# # Streamlit App
# st.title('Crime Rate Forecasting App')
#
# # Date Selection
# selected_date = st.date_input('Select a future date:', datetime.now().date() + timedelta(days=30))
#
# # Generate future dates
# future_dates = pd.date_range(start=datetime.now().date(), end=selected_date, freq='30D')[1:]
#
# # Generate and display forecast
# forecast_df = generate_forecast(future_dates)
#
# st.write("### Forecasted Crime Rates:")
# st.write(forecast_df)
#
# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(forecast_df['date'], forecast_df['predicted_crime_rate'], marker='o', linestyle='-')
# plt.title('Crime Rate Forecast')
# plt.xlabel('Date')
# plt.ylabel('Predicted Crime Rate')
# plt.grid(True)
# st.pyplot(plt)


import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
from datetime import datetime, timedelta

# Load the forecasting model
with open('forecaster_model.pkl', 'rb') as forecaster_file:
    forecaster_model = pickle.load(forecaster_file)


def generate_forecast(future_dates):
    # Create a DataFrame for future dates
    future_df = pd.DataFrame({'date': future_dates})

    fh_values = len(future_dates)

    # Initialize an empty list to store predictions
    future_predictions = []

    for i in range(0, fh_values):
        prediction = forecaster_model.predict(fh=i)

        # Extract numerical value from DataFrame
        if isinstance(prediction, pd.DataFrame):
            # Assuming your DataFrame has a numerical column, adjust 'your_column_name' accordingly
            prediction = prediction['y'].iloc[0]

        # Flatten nested arrays or sequences
        if isinstance(prediction, (list, np.ndarray)):
            prediction = np.mean(prediction)  # Take the mean value for simplicity
        else:
            prediction = float(prediction)

        future_predictions.append(prediction)

    # Assign the list of predictions to the 'predicted_crime_rate' column
    future_df['predicted_crime_rate'] = future_predictions

    return future_df


# Streamlit App
st.title('Crime Rate Forecasting App')

# Date Selection
selected_date = st.date_input('Select a future date:', datetime.now().date() + timedelta(days=30))

# Generate future dates
future_dates = pd.date_range(start=datetime.now().date(), end=selected_date, freq='30D')[1:]

# Generate and display forecast
forecast_df = generate_forecast(future_dates)

st.write("### Forecasted Crime Rates:")
st.write(forecast_df)

# Plotting with Plotly
fig = px.line(forecast_df, x='date', y='predicted_crime_rate', title='Crime Rate Forecast')
fig.update_layout(xaxis_title='Date', yaxis_title='Predicted Crime Rate')

st.plotly_chart(fig)
