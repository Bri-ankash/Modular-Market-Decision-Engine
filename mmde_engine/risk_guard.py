def risk_gate(candles, score):

    closes = [c["close"] for c in candles]

    volatility = abs(closes[-1] - closes[0]) / closes[0]

    # HARD SURVIVAL RULES
    if volatility > 0.05:
        return False, "TOO_VOLATILE"

    if abs(score) < 0.002:
        return False, "NO_EDGE"

    return True, "OK"
