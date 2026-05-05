from mmde_engine.strategy_engine import ensemble
from mmde_engine.regime_detector import detect_regime
from mmde_engine.risk_manager import risk_pass, volatility
from mmde_engine.adaptive_confidence import adjust_confidence
from mmde_engine.execution_engine import open_trade

def generate_signal(symbol, candles):

    if not candles:
        return {"signal": "NO_DATA"}

    price = candles[-1]["close"]
    regime = detect_regime(candles)

    if not risk_pass(candles, regime):
        return {"symbol": symbol, "signal": "BLOCKED", "regime": regime}

    signal = ensemble(candles)

    if signal["signal"] == "HOLD":
        return {"symbol": symbol, "signal": "HOLD", "regime": regime}

    confidence = adjust_confidence(signal["confidence"])

    vol = volatility(candles)

    trade = open_trade(symbol, signal["signal"], price, confidence, vol)

    return {
        "symbol": symbol,
        "signal": signal["signal"],
        "entry": trade["entry"],
        "confidence": confidence,
        "regime": regime,
        "slippage_model": True
    }
