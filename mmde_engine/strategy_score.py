import numpy as np

def score_strategy(candles):
    closes = np.array([c["close"] for c in candles])

    if len(closes) < 10:
        return 0.0

    returns = np.diff(closes)

    momentum = returns[-5:].mean()
    volatility = np.std(returns)

    trend_strength = (closes[-1] - closes[0]) / closes[0]

    score = (momentum * 2) + trend_strength - (volatility * 0.5)

    return float(score)
