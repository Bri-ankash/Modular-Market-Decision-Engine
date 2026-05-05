from mmde_engine.intelligence import detect_regime, edge_score
from mmde_engine.risk_guard import risk_gate
from mmde_engine.trade_controller import can_open_trade, register_trade
from mmde_engine.kill_switch import should_stop_trading, update_equity
from mmde_engine.analytics import save
from mmde_engine.execution import execute_trade


def run(symbol, candles, balance=1000):

    stop, reason = should_stop_trading()
    if stop:
        return {"symbol": symbol, "status": "KILLED", "reason": reason}

    regime = detect_regime(candles)
    score = edge_score(candles)

    allowed, r = risk_gate(candles, score)
    if not allowed:
        return {"symbol": symbol, "status": "NO_TRADE", "reason": r}

    can_trade, reason2 = can_open_trade(symbol)
    if not can_trade:
        return {"symbol": symbol, "status": "BLOCKED", "reason": reason2}

    trade = execute_trade(symbol, candles, score)

    register_trade(symbol, trade)
    save(trade)

    update_equity(balance)

    return trade
