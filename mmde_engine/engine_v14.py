from mmde_engine.intelligence import detect_regime, edge_score
from mmde_engine.risk_guard import risk_gate
from mmde_engine.selector import select_trade
from mmde_engine.trade_controller import can_open_trade, register_trade
from mmde_engine.execution import execute_trade


def run(symbol, candles):

    regime = detect_regime(candles)
    score = edge_score(candles)

    allowed, reason = risk_gate(candles, score)
    if not allowed:
        return {"symbol": symbol, "status": "BLOCKED", "reason": reason}

    can_trade, reason2 = can_open_trade(symbol)
    if not can_trade:
        return {"symbol": symbol, "status": "SKIPPED", "reason": reason2}

    decision = select_trade(symbol, candles, score, regime)

    if decision["decision"] == "NO_TRADE":
        return decision

    trade = execute_trade(symbol, candles, score)

    register_trade(symbol, trade)

    trade["alpha"] = decision["alpha"]
    trade["ev"] = decision["ev"]
    trade["regime"] = regime

    return trade
