from mmde_engine.portfolio_engine import allocate

def run_research(symbols_data):
    allocations, scores = allocate(symbols_data)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return {
        "allocations": allocations,
        "ranking": ranked[:10]
    }
