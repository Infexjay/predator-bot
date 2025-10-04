import xgboost as xgb
import pandas as pd
import yfinance as yf
import os

# Build a robust path to the model file, relative to this script's location
# This avoids issues with the current working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "xgboost_model.json")

# Load the trained model
model = xgb.XGBClassifier()

# Check if the model file exists before loading
if os.path.exists(MODEL_PATH):
    model.load_model(MODEL_PATH)
else:
    # This is a fallback for environments where the model isn't trained yet.
    print(f"Warning: Model file not found at {MODEL_PATH}. Predictions will be random.")
    model = None

def get_prediction(symbol: str):
    """
    Generates a trading prediction using a trained XGBoost model.
    """
    if model is None:
        return {
            "symbol": symbol,
            "signal": "MODEL_NOT_FOUND",
            "confidence": 0.0
        }

    # 1. Fetch latest data
    data = yf.download(symbol, period="1mo", interval="1d")

    if data.empty:
        return {
            "symbol": symbol,
            "signal": "NO_DATA",
            "confidence": 0.0
        }

    # 2. Feature Engineering
    data['ma5'] = data['Close'].rolling(window=5).mean()
    data['ma20'] = data['Close'].rolling(window=20).mean()
    data.dropna(inplace=True)

    if data.empty:
        return {
            "symbol": symbol,
            "signal": "INSUFFICIENT_DATA",
            "confidence": 0.0
        }

    # 3. Define features
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'ma5', 'ma20']
    latest_data = data[features].iloc[-1].to_frame().T

    # 4. Make prediction
    prediction_proba = model.predict_proba(latest_data)[0]
    signal_index = prediction_proba.argmax()
    confidence = prediction_proba[signal_index]

    signal = "BUY" if signal_index == 1 else "SELL" # Based on our label creation in training

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(float(confidence), 2)
    }