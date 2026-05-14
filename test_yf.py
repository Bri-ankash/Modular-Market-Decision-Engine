import yfinance as yf
import pandas as pd

def test():
    symbol = "EURUSD=X"
    print(f"Testing yfinance for {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m")
        if df.empty:
            print("❌ Empty dataframe returned.")
        else:
            print(f"✅ Success! Fetched {len(df)} candles.")
            print(df.tail(2))
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test()
