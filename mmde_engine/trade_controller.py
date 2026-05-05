open_trades = {}
trade_count = 0

MAX_TRADES_PER_SYMBOL = 1
MAX_DAILY_TRADES = 20


def can_open_trade(symbol):

    global trade_count

    if trade_count >= MAX_DAILY_TRADES:
        return False, "DAILY_LIMIT"

    if symbol in open_trades:
        return False, "SYMBOL_LIMIT"

    return True, "OK"


def register_trade(symbol, trade):
    global trade_count

    open_trades[symbol] = trade
    trade_count += 1


def close_trade(symbol):
    if symbol in open_trades:
        del open_trades[symbol]
