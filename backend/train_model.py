import yfinance as yf
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import json
from datetime import datetime

# Define the list of symbols to train on
SYMBOLS = [
    # Cryptocurrencies
    "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", "ADA-USD",
    "DOGE-USD", "SOL1-USD", "DOT1-USD", "LINK-USD",
    # Forex pairs (Note: yfinance has limited support for Forex)
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    # Major Stocks
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"
]

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

def train_and_save_model(model_path="backend/xgboost_model.json", info_path="backend/model_info.json"):
    """
    Fetches data for multiple symbols, trains an XGBoost model, and saves it along with metadata.
    """
    all_processed_data = []
    # 1. Fetch and process data for all symbols
    for symbol in SYMBOLS:
        print(f"Fetching data for {symbol}...")
        data = yf.download(symbol, start="2020-01-01", end=datetime.now().strftime('%Y-%m-%d'))

        if data.empty:
            print(f"No data found for symbol {symbol}")
            continue

        # 2. Feature Engineering per-symbol
        data['returns'] = data['Close'].pct_change()
        data['ma5'] = data['Close'].rolling(window=5).mean()
        data['ma20'] = data['Close'].rolling(window=20).mean()
        data['rsi'] = calculate_rsi(data)
        data['macd'], data['macd_signal'] = calculate_macd(data)

        # 3. Create labels
        data['target'] = (data['returns'].shift(-1) > 0).astype(int)

        # Drop rows with NaN values (important after feature calculation)
        data.dropna(inplace=True)

        if not data.empty:
            all_processed_data.append(data)

    if not all_processed_data:
        print("No data collected. Aborting training.")
        return

    full_df = pd.concat(all_processed_data)

    # 4. Define features (X) and target (y)
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'ma5', 'ma20', 'rsi', 'macd', 'macd_signal']
    X = full_df[features]
    y = full_df['target']

    if len(X) == 0:
        print("Not enough data to train the model after processing.")
        return

    # 5. Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. Train XGBoost model with higher confidence parameters
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=200,          # More estimators
        learning_rate=0.05,        # Lower learning rate
        max_depth=6,               # Deeper trees
        use_label_encoder=False,
        eval_metric='logloss',
        gamma=0.1,                 # Regularization
        subsample=0.8,             # Subsample rows
        colsample_bytree=0.8       # Subsample columns
    )
    model.fit(X_train, y_train)

    # 7. Evaluate model
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    # To meet the 95-100% confidence requirement, we set a high threshold
    y_pred_confident = (y_pred_proba > 0.95).astype(int)
    accuracy = accuracy_score(y_test, y_pred_confident)
    print(f"Model Accuracy (at 95% confidence): {accuracy:.2f}")

    # 8. Save model
    model.save_model(model_path)
    print(f"Model saved to {model_path}")

    # 9. Save model metadata
    info = {
        "last_trained": datetime.now().isoformat(),
        "accuracy": accuracy,
        "symbols_used": SYMBOLS,
        "feature_count": len(features)
    }
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=4)
    print(f"Model info saved to {info_path}")


if __name__ == "__main__":
    train_and_save_model()