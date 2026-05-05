import yfinance as yf

from mmde_engine.backtest_engine import run_backtest
from mmde_engine.metrics import sharpe, max_drawdown
from mmde_engine.baseline import random_strategy

symbols = ["EURUSD=X", "BTC-USD", "AAPL"]

for s in symbols:

    df = yf.download(s, period="10d", interval="1h", progress=False)

    close_series = df["Close"]
    if hasattr(close_series, "iloc") and len(getattr(close_series, "shape", [])) > 1:
        close_series = close_series.iloc[:, 0]
    candles = [{"close": float(x)} for x in close_series.dropna().tolist()]

    result = run_backtest(candles)

    returns = [
        result["equity_curve"][i] - result["equity_curve"][i-1]
        for i in range(1, len(result["equity_curve"]))
    ]

    print("\n======================")
    print("SYMBOL:", s)
    print("FINAL EQUITY:", result["final_equity"])
    print("WINS:", result["wins"])
    print("LOSSES:", result["losses"])
    print("SHARPE:", sharpe(returns))
    print("MAX DRAWDOWN:", max_drawdown(result["equity_curve"]))

    baseline = random_strategy(candles)
    print("RANDOM BASELINE:", baseline)
