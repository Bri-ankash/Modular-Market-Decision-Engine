from mmde_engine.trade_memory import performance_stats

def get_thresholds():
    stats = performance_stats()
    winrate = stats["winrate"]

    if winrate > 60:
        return {
            "signal_threshold": 0.0015,
            "risk_multiplier": 1.2
        }

    if winrate < 45:
        return {
            "signal_threshold": 0.003,
            "risk_multiplier": 0.7
        }

    return {
        "signal_threshold": 0.002,
        "risk_multiplier": 1.0
    }
