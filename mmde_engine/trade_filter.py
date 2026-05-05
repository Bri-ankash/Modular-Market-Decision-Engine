from mmde_engine.regime import detect_regime

def should_trade(candles, score):

    regime = detect_regime(candles)

    # BLOCK unstable markets
    if regime == "HIGH_VOL":
        return False, regime

    # BLOCK weak signals
    if abs(score) < 0.002:
        return False, regime

    return True, regime
