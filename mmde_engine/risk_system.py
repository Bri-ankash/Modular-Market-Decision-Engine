import numpy as np

MAX_DRAWDOWN = 0.20
BASE_RISK = 1.0

state = {
    "balance": 1000,
    "peak": 1000,
    "trades": 0
}


def risk_adjustment(candles):

    closes = [c["close"] for c in candles]
    returns = np.diff(closes)

    volatility = np.std(returns) if len(returns) > 2 else 0

    # adaptive scaling instead of blocking
    if volatility < 0.001:
        return 1.2, "LOW_VOL"
    elif volatility < 0.005:
        return 1.0, "NORMAL_VOL"
    elif volatility < 0.02:
        return 0.6, "HIGH_VOL"
    else:
        return 0.3, "EXTREME_VOL"


def drawdown_check(equity):

    if equity > state["peak"]:
        state["peak"] = equity

    dd = (state["peak"] - equity) / state["peak"]

    if dd > MAX_DRAWDOWN:
        return False, "DRAWDOWN_LIMIT"

    return True, "OK"


def register_trade():
    state["trades"] += 1
