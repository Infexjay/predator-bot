import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from market_data import get_market_data

def prepare_data(symbol: str, period: str = "1y", interval: str = "1d"):
    """
    Fetches market data and engineers features for model training.
    """
    # Fetch data and convert to DataFrame
    data_list = get_market_data(symbol, period, interval)
    if not data_list:
        print("No data fetched. Exiting.")
        return None, None

    df = pd.DataFrame(data_list)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)

    # --- Feature Engineering ---
    # Simple Moving Averages
    df['SMA_7'] = df['Close'].rolling(window=7).mean()
    df['SMA_21'] = df['Close'].rolling(window=21).mean()

    # Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- Target Variable ---
    # Predict if the price will go up (1) or down (0) in the next period
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    # Clean up data
    df.dropna(inplace=True)

    features = ['Close', 'Volume', 'SMA_7', 'SMA_21', 'RSI']
    target = 'target'

    X = df[features]
    y = df[target]

    return X, y

def train_model(X, y):
    """
    Trains an XGBoost classifier and saves it to a file.
    """
    if X is None or y is None:
        print("Cannot train model on empty data.")
        return

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Initialize and train the XGBoost model
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    print("Training XGBoost model...")
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")

    # Save the model
    model_filename = "xgboost_model.json"
    model.save_model(model_filename)
    print(f"Model saved to {model_filename}")

if __name__ == "__main__":
    # Configuration
    SYMBOL_TO_TRAIN = "BTC-USD"

    print(f"Starting model training process for {SYMBOL_TO_TRAIN}...")

    # 1. Prepare data
    X_data, y_data = prepare_data(SYMBOL_TO_TRAIN)

    # 2. Train model
    if X_data is not None and y_data is not None:
        train_model(X_data, y_data)
    else:
        print("Failed to prepare data. Model training aborted.")