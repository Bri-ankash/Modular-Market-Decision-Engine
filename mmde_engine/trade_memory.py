open_positions = {}

def can_trade(symbol):
    return symbol not in open_positions

def register_trade(symbol, trade):
    open_positions[symbol] = trade

def save_trade(trade):
    """
    Simple trade logger (compat layer for execution engine)
    """
    # minimal safe storage (in-memory fallback)
    if not hasattr(save_trade, "history"):
        save_trade.history = []

    save_trade.history.append(trade)
    return True
