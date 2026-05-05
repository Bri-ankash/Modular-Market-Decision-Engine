import uuid

trades = []

def execute_trade(symbol, candles, score):

    entry = candles[-1]["close"]

    direction = "BUY" if score > 0 else "SELL"

    exit_price = candles[-2]["close"] if len(candles) > 1 else entry

    pnl = (exit_price - entry) if direction == "BUY" else (entry - exit_price)

    trade = {
        "id": str(uuid.uuid4())[:8],
        "symbol": symbol,
        "direction": direction,
        "entry": entry,
        "exit": exit_price,
        "pnl": pnl,
        "score": score
    }

    trades.append(trade)

    return trade
