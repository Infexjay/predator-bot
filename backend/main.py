import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI()

# --- Supabase Initialization ---
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in the environment variables.")

supabase: Client = create_client(url, key)

# --- Pydantic Models ---
class Trade(BaseModel):
    user_id: uuid.UUID
    symbol: str
    action: str  # "BUY" or "SELL"
    quantity: float
    price: float
    confidence_score: Optional[float] = None

from backend.market_data import get_market_data
from backend.xgboost_predictor import get_xgboost_prediction

class PredictionRequest(BaseModel):
    symbol: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    """Root endpoint to check API status."""
    return {"message": "Predator Trading Bot API is running"}

@app.get("/market/{symbol}")
def fetch_market_data(symbol: str, period: str = "1d", interval: str = "15m"):
    """Fetches historical market data for a given symbol."""
    return get_market_data(symbol, period, interval)

@app.post("/trades", status_code=201)
def log_trade(trade: Trade):
    """Logs a new trade into the database."""
    try:
        # The .dict() method is deprecated, using .model_dump() instead
        data, count = supabase.table('trades').insert(trade.model_dump()).execute()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trades/{user_id}", response_model=List[Trade])
def get_trades(user_id: uuid.UUID):
    """Fetches all trades for a specific user."""
    try:
        data, count = supabase.table('trades').select('*').eq('user_id', str(user_id)).execute()
        return data[1] if data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/{user_id}")
def get_portfolio(user_id: uuid.UUID):
    """Fetches portfolio data and holdings for a specific user."""
    try:
        # Fetch main portfolio data
        portfolio_res = supabase.table('portfolio').select('*').eq('user_id', str(user_id)).single().execute()

        if not portfolio_res.data:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        portfolio_data = portfolio_res.data
        portfolio_id = portfolio_data['id']

        # Fetch associated holdings
        holdings_res = supabase.table('portfolio_holdings').select('*').eq('portfolio_id', portfolio_id).execute()

        portfolio_data['holdings'] = holdings_res.data if holdings_res.data else []

        return {"status": "success", "data": portfolio_data}
    except Exception as e:
        # Check for specific Supabase error for "single() result contains 0 rows"
        if "PGRST116" in str(e):
            raise HTTPException(status_code=404, detail="Portfolio not found for this user.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(request: PredictionRequest):
    """Generates a trading prediction for a given symbol using the XGBoost model."""
    prediction = get_xgboost_prediction(request.symbol)
    if "error" in prediction:
        raise HTTPException(status_code=500, detail=prediction["error"])
    return prediction