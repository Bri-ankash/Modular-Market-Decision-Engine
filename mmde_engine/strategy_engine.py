def simple_strategy(candles):
    """
    Core trend + momentum strategy
    Returns: BUY / SELL / HOLD
    """

    if not candles or len(candles) < 10:
        return "HOLD"

    closes = [c["close"] for c in candles]

    short_ma = sum(closes[-3:]) / 3
    long_ma = sum(closes[-10:]) / 10

    momentum = closes[-1] - closes[-5]

    if short_ma > long_ma and momentum > 0:
        return "BUY"

    if short_ma < long_ma and momentum < 0:
        return "SELL"

    return "HOLD"
