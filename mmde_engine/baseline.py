import random

def random_strategy(candles):

    equity = 1.0

    for i in range(20, len(candles)):

        entry = candles[i-1]["close"]
        exit_price = candles[i]["close"]

        direction = random.choice([-1, 1])

        pnl = (exit_price - entry) * direction
        equity += pnl

    return equity
