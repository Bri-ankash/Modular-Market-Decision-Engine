from mmde_engine.trade_memory import performance_stats

def adjust_confidence(base_confidence):
    stats = performance_stats()

    winrate = stats["winrate"]

    # adaptive scaling
    if winrate > 60:
        return min(base_confidence * 1.2, 1.0)

    if winrate < 45:
        return base_confidence * 0.7

    return base_confidence
