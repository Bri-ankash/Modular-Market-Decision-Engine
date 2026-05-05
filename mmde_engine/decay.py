from mmde_engine.analytics import load

def detect_decay():

    data = load()

    if len(data) < 50:
        return False

    recent = data[-25:]
    older = data[-50:-25]

    if not older:
        return False

    recent_winrate = sum(1 for t in recent if t["pnl"] > 0) / len(recent)
    older_winrate = sum(1 for t in older if t["pnl"] > 0) / len(older)

    if recent_winrate < older_winrate - 0.1:
        return True

    return False
