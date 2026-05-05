open_positions = {}

def can_trade(symbol):
    return symbol not in open_positions

def register_trade(symbol, trade):
    open_positions[symbol] = trade
