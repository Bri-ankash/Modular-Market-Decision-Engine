import pandas as pd

def extract_close(df):
    close = df["Close"]

    if hasattr(close, "iloc") and len(getattr(close, "shape", [])) > 1:
        close = close.iloc[:, 0]

    return close.dropna().tolist()
