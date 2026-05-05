from mmde_engine.strategy_engine import simple_strategy

def backtest(candles):
    wins = 0
    losses = 0

    for i in range(20, len(candles)):
        window = candles[:i]
        signal = simple_strategy(window)

        if signal["signal"] == "HOLD":
            continue

        entry = window[-1]["close"]
        future = candles[i]["close"]

        if signal["signal"] == "BUY" and future > entry:
            wins += 1
        elif signal["signal"] == "SELL" and future < entry:
            wins += 1
        else:
            losses += 1

    total = wins + losses
    winrate = (wins / total) * 100 if total > 0 else 0

    return {
        "winrate": winrate,
        "pass": winrate >= 55
    }
