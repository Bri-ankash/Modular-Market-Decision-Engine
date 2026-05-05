def size_position(balance, confidence, volatility):

    base = balance * 0.01

    adjusted = base * confidence * (1 / (1 + volatility))

    return max(0, adjusted)
