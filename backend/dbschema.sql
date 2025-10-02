-- Trades Table
-- Stores a log of every trade executed by the bot
CREATE TABLE trades (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id UUID REFERENCES auth.users NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL, -- "BUY" or "SELL"
    quantity DECIMAL NOT NULL,
    price DECIMAL NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence_score REAL,
    pnl REAL -- Profit and Loss
);

-- Portfolio Table
-- Tracks the user's current holdings and overall portfolio value
CREATE TABLE portfolio (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id UUID REFERENCES auth.users NOT NULL UNIQUE,
    balance DECIMAL NOT NULL DEFAULT 10000.00, -- Simulated starting balance
    equity DECIMAL NOT NULL DEFAULT 10000.00,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Portfolio Holdings Table
-- A join table to track the assets within each portfolio
CREATE TABLE portfolio_holdings (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    portfolio_id BIGINT REFERENCES portfolio(id) NOT NULL,
    symbol TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    average_price DECIMAL NOT NULL,
    UNIQUE(portfolio_id, symbol)
);

-- Logs Table
-- For storing application logs, errors, and debug information
CREATE TABLE logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    level TEXT NOT NULL, -- e.g., "INFO", "WARN", "ERROR"
    message TEXT NOT NULL,
    context JSONB
);

-- Enable Row-Level Security (RLS) for user-specific data
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;

-- Policies to ensure users can only access their own data
CREATE POLICY "Users can only see their own trades"
    ON trades FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own trades"
    ON trades FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can only see their own portfolio"
    ON portfolio FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only see their own portfolio holdings"
    ON portfolio_holdings FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM portfolio
        WHERE portfolio.id = portfolio_holdings.portfolio_id
        AND portfolio.user_id = auth.uid()
    ));