import numpy as np

def detect_regime(candles):
    closes = np.array([c["close"] for c in candles])
    returns = np.diff(closes)

    vol = np.std(returns)
    trend = (closes[-1] - closes[0]) / closes[0]

    if vol > 0.02:
        return "HIGH_VOL"
    if abs(trend) > 0.01:
        return "TREND"
    return "RANGE"


def edge_score(candles):
    closes = np.array([c["close"] for c in candles])
    returns = np.diff(closes)

    if len(returns) < 10:
        return 0

    momentum = returns[-5:].mean()
    mean_reversion = -np.mean(returns)

    volatility = np.std(returns)

    score = (momentum * 1.5 + mean_reversion * 0.5) - volatility

    return float(score)
