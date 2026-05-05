import time
import uuid

account = {
    "balance": 1000,
    "equity": 1000,
    "trades": []
}

def execute_order(symbol, direction, price, size):

    trade_id = str(uuid.uuid4())[:8]

    slippage = price * 0.0002

    fill_price = price + slippage if direction == "BUY" else price - slippage

    trade = {
        "id": trade_id,
        "symbol": symbol,
        "direction": direction,
        "entry": fill_price,
        "size": size,
        "status": "OPEN",
        "timestamp": time.time()
    }

    account["trades"].append(trade)

    return trade


def close_trade(trade, exit_price):

    slippage = exit_price * 0.0002

    fill_exit = exit_price - slippage if trade["direction"] == "BUY" else exit_price + slippage

    pnl = (fill_exit - trade["entry"]) * trade["size"] if trade["direction"] == "BUY" else (trade["entry"] - fill_exit) * trade["size"]

    account["balance"] += pnl
    account["equity"] = account["balance"]

    trade["exit"] = fill_exit
    trade["pnl"] = pnl
    trade["status"] = "CLOSED"

    return trade


def get_account():
    return account
