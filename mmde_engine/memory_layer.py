import json
import os
from collections import defaultdict

MEMORY_FILE = "mmde_memory.json"

class PerformanceMemory:
    def __init__(self):
        self.memory = {
            "trades": [],
            "stats": defaultdict(lambda: {
                "wins": 0,
                "losses": 0,
                "pnl": 0.0
            }),
            "regime_stats": defaultdict(lambda: {
                "trades": 0,
                "wins": 0
            })
        }
        self.load()

    def load(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                raw = json.load(f)
                self.memory["trades"] = raw.get("trades", [])
                self.memory["stats"] = defaultdict(dict, raw.get("stats", {}))
                self.memory["regime_stats"] = defaultdict(dict, raw.get("regime_stats", {}))

    def save(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump({
                "trades": self.memory["trades"],
                "stats": dict(self.memory["stats"]),
                "regime_stats": dict(self.memory["regime_stats"])
            }, f, indent=2)

    def record_trade(self, trade):
        self.memory["trades"].append(trade)

        symbol = trade["symbol"]
        pnl = trade.get("pnl", 0)
        regime = trade.get("regime", "UNKNOWN")

        stats = self.memory["stats"][symbol]
        stats["trades"] = stats.get("trades", 0) + 1
        stats["pnl"] = stats.get("pnl", 0) + pnl

        if pnl > 0:
            stats["wins"] = stats.get("wins", 0) + 1
        else:
            stats["losses"] = stats.get("losses", 0) + 1

        rstats = self.memory["regime_stats"][regime]
        rstats["trades"] = rstats.get("trades", 0) + 1
        if pnl > 0:
            rstats["wins"] = rstats.get("wins", 0) + 1

        self.save()

    def get_confidence_boost(self, symbol):
        stats = self.memory["stats"].get(symbol, {})
        trades = stats.get("trades", 0)

        if trades < 5:
            return 1.0

        winrate = stats.get("wins", 0) / trades

        if winrate > 0.6:
            return 1.2
        elif winrate < 0.4:
            return 0.8

        return 1.0


def adaptive_risk_modifier(memory, regime):
    stats = memory.memory["regime_stats"].get(regime, {})
    trades = stats.get("trades", 0)
    wins = stats.get("wins", 0)

    if trades < 10:
        return 1.0  # not enough data

    winrate = wins / trades

    # TOO STRICT BEFORE → relax slightly
    if winrate > 0.55:
        return 1.1  # allow more trades

    # LOSING REGIME → tighten
    if winrate < 0.4:
        return 0.7

    return 1.0
