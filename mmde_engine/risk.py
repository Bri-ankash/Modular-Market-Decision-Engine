def risk_check(candles, score):

    closes = [c["close"] for c in candles]

    if len(closes) < 10:
        return False

    volatility = abs(closes[-1] - closes[0]) / closes[0]

    # hard safety filters
    if volatility > 0.05:
        return False

    if abs(score) < 0.001:
        return False

    return True
