import numpy as np
from mmde_engine.strategy import score_market

def run_backtest(candles, cost=0.0002):

    equity = 1.0
    equity_curve = []

    wins = 0
    losses = 0

    for i in range(20, len(candles)):

        window = candles[:i]
        future = candles[i]

        score = score_market(window)

        entry = window[-1]["close"]
        exit_price = future["close"]

        # signal
        direction = 1 if score > 0 else -1

        pnl = (exit_price - entry) * direction

        # realistic cost (spread + slippage proxy)
        pnl -= cost

        equity += pnl
        equity_curve.append(equity)

        if pnl > 0:
            wins += 1
        else:
            losses += 1

    return {
        "equity_curve": equity_curve,
        "wins": wins,
        "losses": losses,
        "final_equity": equity
    }
