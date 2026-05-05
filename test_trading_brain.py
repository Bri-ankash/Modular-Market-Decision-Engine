import sys
sys.path.insert(0, '.')

import yfinance as yf
from mmde_engine.signal_engine import generate_signal
from mmde_engine.execution_engine import close_trade, active_trades

symbols = ["EURUSD=X", "BTC-USD", "AAPL"]

for s in symbols:
    data = yf.download(s, period="5d", interval="1h", progress=False)

    # ---------------- SAFE NORMALIZATION ----------------
    close_series = data["Close"]

    # handle weird Yahoo structures
    if hasattr(close_series, "iloc") and hasattr(close_series, "shape") and len(close_series.shape) > 1:
        close_series = close_series.iloc[:, 0]

    close_series = close_series.dropna().to_numpy()

    candles = [{"close": float(x)} for x in close_series]
    # ----------------------------------------------------

    result = generate_signal(s, candles)
    print(result)

# simulate closing trades (last price)
if candles:
    for t in active_trades:
        close_trade(t, candles[-1]["close"])

print("\nACTIVE TRADES:", active_trades)
