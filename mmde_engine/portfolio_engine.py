from mmde_engine.strategy_score import score_strategy

def allocate(symbols_data):
    allocations = {}
    total_score = 0

    scores = {}

    for symbol, candles in symbols_data.items():
        s = score_strategy(candles)
        scores[symbol] = s
        total_score += max(s, 0)

    for symbol, s in scores.items():
        if total_score > 0:
            allocations[symbol] = max(s, 0) / total_score
        else:
            allocations[symbol] = 0

    return allocations, scores
