import json
import os

FILE = "mmde_trade_memory.json"

def load_memory():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def save_trade(trade):
    memory = load_memory()
    memory.append(trade)

    with open(FILE, "w") as f:
        json.dump(memory[-500:], f)  # keep last 500 trades

def performance_stats():
    memory = load_memory()
    if not memory:
        return {"winrate": 0, "trades": 0}

    wins = sum(1 for t in memory if t.get("result") == "WIN")
    total = len(memory)

    return {
        "winrate": (wins / total) * 100,
        "trades": total
    }
