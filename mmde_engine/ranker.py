import numpy as np

def rank_opportunity(score, volatility, regime):

    base = abs(score)

    if regime == "HIGH_VOL":
        return 0

    if regime == "TREND":
        return base * 1.5

    if regime == "RANGE":
        return base * 1.2

    return base - volatility
