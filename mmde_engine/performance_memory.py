class PerformanceMemory:
    def __init__(self):
        self.trades = []
        self.pnl_curve = []

    def log_trade(self, trade):
        self.trades.append(trade)

        pnl = trade.get("pnl", 0)
        self.pnl_curve.append(pnl)

    def winrate(self):
        if not self.trades:
            return 0

        wins = sum(1 for t in self.trades if t.get("pnl", 0) > 0)
        return wins / len(self.trades)

    def equity_curve(self):
        equity = 0
        curve = []

        for pnl in self.pnl_curve:
            equity += pnl
            curve.append(equity)

        return curve
