import pandas as pd
from datetime import datetime, timedelta
import pickle
import matplotlib.pyplot as plt
import numpy as np

# Load the forecasting model
with open('forecaster_model.pkl', 'rb') as forecaster_file:
    forecaster_model = pickle.load(forecaster_file)

current_date = datetime.now().date()
future_dates = [current_date + timedelta(days=30 * i) for i in range(1, 7)]

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

    # Print the prediction to understand its structure
    print(f"Prediction for step {i}: {prediction}")

    # Flatten nested arrays or sequences
    if isinstance(prediction, (list, np.ndarray)):
        prediction = np.mean(prediction)  # Take the mean value for simplicity
    else:
        prediction = float(prediction)

    future_predictions.append(prediction)

# Assign the list of predictions to the 'predicted_crime_rate' column
future_df['predicted_crime_rate'] = future_predictions

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(future_df['date'], future_df['predicted_crime_rate'], marker='o', linestyle='-')
plt.title('Crime Rate Forecast')
plt.xlabel('Date')
plt.ylabel('Predicted Crime Rate')
plt.grid(True)
plt.show()
