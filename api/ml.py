import os
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend suitable for scripts

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from django.conf import settings
from sklearn.metrics import mean_squared_error, r2_score

def load_lstm_model():
    model_path = getattr(settings, 'MODEL_PATH', 'stock_prediction_model.keras')
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model file not found.")
    return load_model(model_path)

def predict_stock_and_generate_plots(ticker):
    model = load_lstm_model()
    df = yf.download(ticker, period="10y")

    if df.empty:
        raise ValueError("No data found for ticker.")

    data = df[['Close']]
    dataset = data.values

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(dataset)

    # Create test sequence
    sequence_length = 60
    X_test = [scaled_data[i - sequence_length:i, 0] for i in range(sequence_length, len(scaled_data))]
    X_test = np.array(X_test).reshape(-1, sequence_length, 1)

    # Predictions
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    actual = dataset[sequence_length:]

    mse = mean_squared_error(actual, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(actual, predictions)

    # Next-day forecast
    next_input = scaled_data[-60:].reshape(1, 60, 1)
    next_pred = model.predict(next_input)
    next_day_price = scaler.inverse_transform(next_pred)[0][0]

    # Plot 1: Closing price history
    plot_dir = os.path.join(settings.MEDIA_ROOT, 'plots')
    os.makedirs(plot_dir, exist_ok=True)
    plot1_path = os.path.join(plot_dir, f'{ticker}_plot1.png')
    data.plot(title=f"{ticker} - Closing Price History")
    plt.savefig(plot1_path)
    plt.close()

    # Plot 2: Actual vs Predicted
    plt.figure()
    plt.plot(actual, label='Actual')
    plt.plot(predictions, label='Predicted')
    plt.legend()
    plt.title("Actual vs Predicted")
    plot2_path = os.path.join(plot_dir, f'{ticker}_plot2.png')
    plt.savefig(plot2_path)
    plt.close()

    return next_day_price, mse, rmse, r2, plot1_path, plot2_path
