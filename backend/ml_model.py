import random

def get_prediction(symbol: str):
    """
    Generates a placeholder trading prediction.

    In a real application, this function would accept market data
    and use a machine learning model to generate a prediction.
    For now, it returns a random signal.

    Args:
        symbol (str): The stock/crypto ticker symbol (e.g., "BTC-USD").

    Returns:
        dict: A dictionary containing the prediction signal and a confidence score.
    """
    signals = ["BUY", "SELL", "HOLD"]
    prediction = {
        "symbol": symbol,
        "signal": random.choice(signals),
        "confidence": round(random.uniform(0.5, 1.0), 2)
    }
    return prediction