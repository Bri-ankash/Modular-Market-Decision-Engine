from mmde_engine.trade_memory import load_memory

def equity_curve():
    trades = load_memory()

    equity = 0
    curve = []

    for t in trades:
        pnl = t.get("pnl", 0)
        equity += pnl
        curve.append(equity)

    return curve


def stats():
    trades = load_memory()
    if not trades:
        return {}

    wins = [t for t in trades if t.get("pnl", 0) > 0]
    losses = [t for t in trades if t.get("pnl", 0) <= 0]

    total_pnl = sum(t.get("pnl", 0) for t in trades)

    avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["pnl"] for t in losses) / len(losses) if losses else 0

    winrate = len(wins) / len(trades) * 100

    expectancy = (winrate/100 * avg_win) + ((1 - winrate/100) * avg_loss)

    return {
        "trades": len(trades),
        "winrate": round(winrate, 2),
        "total_pnl": round(total_pnl, 4),
        "avg_win": round(avg_win, 4),
        "avg_loss": round(avg_loss, 4),
        "expectancy": round(expectancy, 4)
    }
