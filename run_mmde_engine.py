import yfinance as yf
from mmde_engine.mmde_orchestrator import MMDEEngine


def get_data(symbol):

    df = yf.download(symbol, period="5d", interval="1h", progress=False)

    if df is None or df.empty:
        return []

    # FIX: handle MultiIndex / Series / DataFrame safely
    close = df["Close"]

    # if it's a DataFrame (multi-ticker edge case)
    if hasattr(close, "values") and len(close.shape) > 1:
        close = close.iloc[:, 0]

    closes = close.dropna().astype(float).tolist()

    return [{"close": float(x)} for x in closes]


symbols = ["EURUSD=X", "BTC-USD", "AAPL", "NVDA", "TSLA"]

market_data = {s: get_data(s) for s in symbols}

engine = MMDEEngine()

results = engine.run_cycle(market_data)

print("\n======================")
print("MMDE LIVE CYCLE RESULT")
print("======================")

for r in results:
    print(r)
