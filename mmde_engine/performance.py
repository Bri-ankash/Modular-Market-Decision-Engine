import numpy as np

def sharpe_ratio(returns):
    if len(returns) < 2:
        return 0

    mean = np.mean(returns)
    std = np.std(returns)

    if std == 0:
        return 0

    return mean / std


def max_drawdown(equity):
    peak = equity[0]
    max_dd = 0

    for x in equity:
        if x > peak:
            peak = x
        dd = (peak - x) / peak
        max_dd = max(max_dd, dd)

    return max_dd
