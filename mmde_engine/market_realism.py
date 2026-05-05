import random

def get_spread(symbol):
    # simplified realistic spreads
    if "BTC" in symbol:
        return 8.0
    if "EUR" in symbol or "GBP" in symbol:
        return 0.0002
    if "AAPL" in symbol:
        return 0.05
    return 0.01


def slippage(symbol, volatility=1.0):
    base = get_spread(symbol)

    # randomness simulating liquidity gaps
    slip = base * random.uniform(0.5, 2.5) * volatility
    return slip


def apply_execution_price(symbol, price, direction, volatility=1.0):
    slip = slippage(symbol, volatility)

    if direction == "BUY":
        return price + slip
    elif direction == "SELL":
        return price - slip
    return price
