from mmde_engine.data import get_candles
from mmde_engine.intelligence import detect_regime, edge_score
from mmde_engine.risk_guard import risk_gate
from mmde_engine.positioning import position_size
from mmde_engine.learning import adjust_confidence
from mmde_engine.execution import execute_trade

def run_symbol(symbol, balance=1000):

    candles = get_candles(symbol)

    if not candles:
        return {"symbol": symbol, "status": "NO_DATA"}

    regime = detect_regime(candles)
    score = edge_score(candles)

    allowed, reason = risk_gate(candles, score)

    if not allowed:
        return {
            "symbol": symbol,
            "status": "NO_TRADE",
            "reason": reason,
            "regime": regime
        }

    confidence = adjust_confidence(abs(score))

    size = position_size(balance, confidence, abs(score))

    trade = execute_trade(symbol, candles, score)

    trade["regime"] = regime
    trade["confidence"] = confidence
    trade["size"] = size

    return trade
