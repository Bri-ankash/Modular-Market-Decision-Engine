import numpy as np

def compute_alpha(candles, score, regime):

    closes = np.array([c["close"] for c in candles])
    returns = np.diff(closes)

    momentum = np.mean(returns[-5:]) if len(returns) > 5 else 0
    volatility = np.std(returns) if len(returns) > 1 else 0

    trend_strength = (closes[-1] - closes[0]) / closes[0]

    # Base alpha
    alpha = score * 2 + momentum + trend_strength

    # Regime adjustment
    if regime == "TREND":
        alpha *= 1.5
    elif regime == "RANGE":
        alpha *= 1.1
    elif regime == "HIGH_VOL":
        alpha *= 0.2  # punish chaos

    # Risk penalty
    alpha = alpha / (1 + volatility)

    return float(alpha)
