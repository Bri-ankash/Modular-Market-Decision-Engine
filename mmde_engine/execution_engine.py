import uuid
from mmde_engine.trade_memory import save_trade
from mmde_engine.market_realism import apply_execution_price

active_trades = []

def open_trade(symbol, signal, price, confidence, volatility=1.0):

    exec_price = apply_execution_price(symbol, price, signal, volatility)

    trade = {
        "id": str(uuid.uuid4())[:8],
        "symbol": symbol,
        "direction": signal,
        "entry": exec_price,
        "raw_entry": price,
        "confidence": confidence,
        "status": "OPEN"
    }

    active_trades.append(trade)
    return trade


def close_trade(trade, exit_price, volatility=1.0):
    exec_exit = apply_execution_price(
        trade["symbol"],
        exit_price,
        "SELL" if trade["direction"] == "BUY" else "BUY",
        volatility
    )

    pnl = 0
    if trade["direction"] == "BUY":
        pnl = exec_exit - trade["entry"]
    else:
        pnl = trade["entry"] - exec_exit

    trade["exit"] = exec_exit
    trade["raw_exit"] = exit_price
    trade["pnl"] = pnl
    trade["status"] = "CLOSED"

    save_trade({
        **trade,
        "result": "WIN" if pnl > 0 else "LOSS"
    })

    return trade
