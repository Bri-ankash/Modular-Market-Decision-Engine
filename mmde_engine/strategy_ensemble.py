def ensemble_vote(candles):
    """
    Unified strategy output contract:
    ALWAYS returns (signal, confidence)
    """

    # simple placeholder logic (safe deterministic fallback)
    if not candles or len(candles) < 2:
        return "HOLD", 0.0

    last = candles[-1]["close"]
    prev = candles[-2]["close"]

    if last > prev:
        return "BUY", 0.6
    elif last < prev:
        return "SELL", 0.6

    return "HOLD", 0.5
