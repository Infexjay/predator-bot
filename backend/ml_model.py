import xgboost as xgb
import pandas as pd
import yfinance as yf
import os

# Build a robust path to the model file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "xgboost_model.json")

# Load the trained model
model = xgb.XGBClassifier()

if os.path.exists(MODEL_PATH):
    model.load_model(MODEL_PATH)
else:
    print(f"Warning: Model file not found at {MODEL_PATH}. Predictions will be unavailable.")
    model = None

def calculate_rsi(data, window=14):
    """Calculates the Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, fast_window=12, slow_window=26, signal_window=9):
    """Calculates the Moving Average Convergence Divergence (MACD)."""
    fast_ema = data['Close'].ewm(span=fast_window, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_window, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal_line

def get_prediction(symbol: str):
    """
    Generates a trading prediction using a trained XGBoost model.
    """
    if model is None:
        return {"symbol": symbol, "signal": "MODEL_NOT_FOUND", "confidence": 0.0}

    # 1. Fetch latest data
    data = yf.download(symbol, period="1mo", interval="1d")

    if data.empty:
        return {"symbol": symbol, "signal": "NO_DATA", "confidence": 0.0}

    # 2. Feature Engineering - MUST MATCH TRAINING SCRIPT
    data['ma5'] = data['Close'].rolling(window=5).mean()
    data['ma20'] = data['Close'].rolling(window=20).mean()
    data['rsi'] = calculate_rsi(data)
    data['macd'], data['macd_signal'] = calculate_macd(data)
    data.dropna(inplace=True)

    if data.empty:
        return {"symbol": symbol, "signal": "INSUFFICIENT_DATA", "confidence": 0.0}

    # 3. Define features - MUST MATCH TRAINING SCRIPT
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'ma5', 'ma20', 'rsi', 'macd', 'macd_signal']
    latest_data = data[features].iloc[-1].to_frame().T

    # 4. Make prediction
    try:
        prediction_proba = model.predict_proba(latest_data)[0]
        signal_index = prediction_proba.argmax()
        confidence = prediction_proba[signal_index]
        signal = "BUY" if signal_index == 1 else "SELL"
    except Exception as e:
        print(f"Error during prediction: {e}")
        return {"symbol": symbol, "signal": "PREDICTION_ERROR", "confidence": 0.0}

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": round(float(confidence), 2)
    }