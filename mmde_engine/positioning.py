def position_size(balance, confidence, volatility, drawdown=0):

    base_risk = 0.01

    drawdown_factor = max(0.2, 1 - drawdown)

    size = balance * base_risk * confidence * drawdown_factor / (1 + volatility)

    return max(0, size)
