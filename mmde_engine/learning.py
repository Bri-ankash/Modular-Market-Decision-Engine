import json
import os

FILE = "trade_memory.json"

def load_memory():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))


def save_trade(trade):
    memory = load_memory()
    memory.append(trade)
    json.dump(memory, open(FILE, "w"))


def adjust_confidence(base_confidence):
    memory = load_memory()

    if len(memory) < 20:
        return base_confidence

    wins = sum(1 for t in memory[-50:] if t["pnl"] > 0)
    total = min(50, len(memory))

    winrate = wins / total

    # adaptive scaling
    if winrate < 0.45:
        return base_confidence * 0.6
    if winrate > 0.55:
        return base_confidence * 1.2

    return base_confidence
