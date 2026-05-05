import numpy as np

def score_market(candles):

    closes = np.array([c["close"] for c in candles])

    returns = np.diff(closes)

    momentum = returns[-5:].mean() if len(returns) > 5 else returns.mean()
    trend = (closes[-1] - closes[0]) / closes[0]

    volatility = np.std(returns) if len(returns) > 1 else 0

    score = (momentum * 2) + trend - (volatility * 0.5)

    return float(score)
