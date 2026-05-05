from mmde_engine.strategy_engine import simple_strategy

def momentum_strategy(candles):
    return simple_strategy(candles)

def mean_reversion_strategy(candles):
    closes = [c["close"] for c in candles]
    avg = sum(closes) / len(closes)

    if closes[-1] < avg:
        return "BUY"
    if closes[-1] > avg:
        return "SELL"
    return "HOLD"

def volatility_strategy(candles):
    closes = [c["close"] for c in candles]
    returns = [closes[i] - closes[i-1] for i in range(1, len(closes))]

    vol = sum([abs(r) for r in returns]) / len(returns)

    if vol < 0.5:
        return simple_strategy(candles)
    return "HOLD"

def ensemble_vote(candles):

    signals = [
        momentum_strategy(candles),
        mean_reversion_strategy(candles),
        volatility_strategy(candles)
    ]

    buy = signals.count("BUY")
    sell = signals.count("SELL")

    if buy > sell:
        return "BUY"
    if sell > buy:
        return "SELL"

    return "HOLD"
