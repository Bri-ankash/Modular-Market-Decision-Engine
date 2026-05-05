from mmde_engine.paper_broker import execute_order, close_trade

def execute_trade(symbol, candles, score):

    price = candles[-1]["close"]

    direction = "BUY" if score > 0 else "SELL"

    size = 1  # can be upgraded later

    trade = execute_order(symbol, direction, price, size)

    return trade
