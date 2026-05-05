def risk_gate(candles, score):

    closes = [c["close"] for c in candles]

    volatility = abs(closes[-1] - closes[0]) / closes[0]

    if volatility > 0.03:
        return False, "HIGH_VOL_BLOCK"

    if abs(score) < 0.002:
        return False, "NO_EDGE"

    return True, "OK"
