import yfinance as yf
from fastapi import HTTPException

def get_market_data(symbol: str, period: str = "1d", interval: str = "15m"):
    """
    Fetches historical market data for a given symbol.

    Args:
        symbol (str): The stock/crypto ticker symbol (e.g., "BTC-USD").
        period (str): The period to fetch data for (e.g., "1d", "5d", "1mo").
        interval (str): The data interval (e.g., "1m", "15m", "1h").

    Returns:
        dict: A dictionary containing the historical data.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        # Convert DataFrame to a more JSON-friendly format
        hist.reset_index(inplace=True)
        # Convert timestamp to string to avoid JSON serialization issues
        hist['Datetime'] = hist['Datetime'].astype(str)

        return hist.to_dict(orient="records")
    except Exception as e:
        # Catch potential errors from yfinance or other issues
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data for {symbol}: {str(e)}")