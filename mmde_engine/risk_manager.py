import numpy as np

def volatility(candles):
    closes = [c["close"] for c in candles]
    if len(closes) < 5:
        return 1.0

    returns = np.diff(closes) / closes[:-1]
    return float(np.std(returns) * 100)


def liquidity_proxy(symbol, candles):
    # crude proxy: volume + smoothness
    return max(0.5, min(1.5, 1.0))


def risk_pass(candles, regime):

    vol = volatility(candles)

    # block extreme volatility
    if vol > 2.5:
        return False

    # block flat/illiquid conditions
    if regime == "RANGE" and vol < 0.2:
        return False

    return True
