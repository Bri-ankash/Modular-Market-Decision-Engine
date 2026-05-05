import yfinance as yf

def get_candles(symbol, period="5d", interval="1h"):

    df = yf.download(symbol, period=period, interval=interval, progress=False)

    if df is None or df.empty:
        return None

    close = df["Close"]

    # normalize safely (fix all pandas issues)
    if hasattr(close, "iloc") and len(getattr(close, "shape", [])) > 1:
        close = close.iloc[:, 0]

    close = close.dropna().to_numpy()

    return [{"close": float(x)} for x in close]
