import json
import os
import numpy as np

FILE = "equity_curve.json"

class PerformanceDashboard:
    def __init__(self, initial_balance=1000):
        self.balance = initial_balance
        self.equity_curve = []
        self.trades = []

        if os.path.exists(FILE):
            with open(FILE, "r") as f:
                data = json.load(f)
                self.equity_curve = data.get("equity_curve", [])
                self.balance = self.equity_curve[-1] if self.equity_curve else initial_balance

    def record_trade(self, trade):
        pnl = trade.get("pnl", 0)

        self.balance += pnl
        self.equity_curve.append(self.balance)
        self.trades.append(trade)

        self.save()

    def save(self):
        with open(FILE, "w") as f:
            json.dump({
                "equity_curve": self.equity_curve,
                "final_balance": self.balance,
                "trades": len(self.trades)
            }, f, indent=2)

    def stats(self):
        if len(self.equity_curve) < 2:
            return {}

        returns = np.diff(self.equity_curve)

        wins = sum(1 for r in returns if r > 0)
        losses = sum(1 for r in returns if r <= 0)

        winrate = wins / len(returns) if returns.size > 0 else 0
        profit = self.balance - self.equity_curve[0]

        max_dd = self.max_drawdown()

        return {
            "final_balance": self.balance,
            "winrate": round(winrate, 3),
            "profit": round(profit, 3),
            "max_drawdown": round(max_dd, 3),
            "trades": len(self.trades)
        }

    def max_drawdown(self):
        peak = -float("inf")
        max_dd = 0

        for v in self.equity_curve:
            if v > peak:
                peak = v
            dd = peak - v
            max_dd = max(max_dd, dd)

        return max_dd
