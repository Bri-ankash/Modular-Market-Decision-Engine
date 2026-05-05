import json
import os

FILE = "performance.json"


def load():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))


def save(trade):
    data = load()
    data.append(trade)
    json.dump(data, open(FILE, "w"))


def expectancy():
    data = load()

    if len(data) < 20:
        return 0

    wins = sum(1 for t in data if t.get("pnl", 0) > 0)
    losses = sum(1 for t in data if t.get("pnl", 0) <= 0)

    return wins / (wins + losses)
