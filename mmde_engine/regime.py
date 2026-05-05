import numpy as np

def detect_regime(candles):

    closes = np.array([c["close"] for c in candles])

    returns = np.diff(closes)

    volatility = np.std(returns)
    trend = (closes[-1] - closes[0]) / closes[0]

    if volatility > 0.02:
        return "HIGH_VOL"

    if abs(trend) > 0.01:
        return "TREND"

    return "RANGE"
