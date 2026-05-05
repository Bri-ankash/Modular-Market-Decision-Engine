from mmde_engine.performance_memory import PerformanceMemory

memory = PerformanceMemory()

def score_signal(signal, base_confidence):
    winrate = memory.winrate()

    # adaptive boost/penalty
    if winrate > 0.6:
        return base_confidence * 1.2

    if winrate < 0.4:
        return base_confidence * 0.7

    return base_confidence
