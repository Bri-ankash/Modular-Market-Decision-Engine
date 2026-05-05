from mmde_engine.opportunity_ranker import compute_alpha
from mmde_engine.expected_value import expected_value

def select_trade(symbol, candles, score, regime):

    alpha = compute_alpha(candles, score, regime)

    confidence = abs(score)

    ev = expected_value(alpha, confidence)

    if ev <= 0:
        return {
            "symbol": symbol,
            "decision": "NO_TRADE",
            "reason": "NEGATIVE_EV",
            "ev": ev
        }

    direction = "BUY" if alpha > 0 else "SELL"

    return {
        "symbol": symbol,
        "decision": "TRADE",
        "direction": direction,
        "alpha": alpha,
        "ev": ev,
        "confidence": confidence
    }
