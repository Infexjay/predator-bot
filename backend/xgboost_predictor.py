import os
import pandas as pd
import xgboost as xgb
from market_data import get_market_data

MODEL_PATH = "xgboost_model.json"
model = None

def load_model():
    """Loads the trained XGBoost model from file."""
    global model
    if os.path.exists(MODEL_PATH):
        model = xgb.XGBClassifier()
        model.load_model(MODEL_PATH)
        print("XGBoost model loaded successfully.")
    else:
        print("Model file not found. Please train the model first.")
        # In a production scenario, you might want to handle this more gracefully
        # For now, the predictor will fail until the model is trained.

def get_xgboost_prediction(symbol: str):
    """
    Generates a prediction using the trained XGBoost model.
    """
    if model is None:
        return {"error": "Model not loaded. Please train the model first."}

    # 1. Fetch recent market data to engineer features
    # We need enough data to calculate moving averages and RSI. 30 days should be sufficient.
    data_list = get_market_data(symbol, period="30d", interval="1d")
    if not data_list:
        return {"error": f"Could not fetch market data for {symbol}."}

    df = pd.DataFrame(data_list)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)

    # 2. Engineer features (must be identical to training)
    df['SMA_7'] = df['Close'].rolling(window=7).mean()
    df['SMA_21'] = df['Close'].rolling(window=21).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Drop rows with NaN values resulting from rolling calculations
    df.dropna(inplace=True)

    if df.empty:
        return {"error": "Not enough data to generate features for prediction."}

    # 3. Get the most recent data point for prediction
    last_row = df.iloc[-1:]
    features = ['Close', 'Volume', 'SMA_7', 'SMA_21', 'RSI']
    X_pred = last_row[features]

    # 4. Make prediction
    prediction_numeric = model.predict(X_pred)[0]
    prediction_proba = model.predict_proba(X_pred)[0]

    # Map numeric prediction to a signal
    signal = "BUY" if prediction_numeric == 1 else "SELL"
    confidence = float(max(prediction_proba)) # The probability of the predicted class

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(confidence, 4)
    }

# Load the model when the module is imported
load_model()