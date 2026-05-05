def momentum(c):
    closes = [x["close"] for x in c]
    if len(closes) < 6:
        return 0
    return (closes[-1] - closes[-5]) / closes[-5]


def mean_reversion(c):
    closes = [x["close"] for x in c]
    if len(closes) < 10:
        return 0
    avg = sum(closes[-10:]) / 10
    return (avg - closes[-1]) / avg


def breakout(c):
    closes = [x["close"] for x in c]
    if len(closes) < 10:
        return 0
    return (closes[-1] - min(closes[-10:])) / min(closes[-10:])


def ensemble(candles):
    m = momentum(candles)
    r = mean_reversion(candles)
    b = breakout(candles)

    score = (m * 0.5) + (r * 0.3) + (b * 0.2)

    confidence = min(abs(score) * 8, 1.0)

    if score > 0.002:
        return {"signal": "BUY", "score": score, "confidence": confidence}

    if score < -0.002:
        return {"signal": "SELL", "score": score, "confidence": confidence}

    return {"signal": "HOLD", "score": score, "confidence": confidence}
