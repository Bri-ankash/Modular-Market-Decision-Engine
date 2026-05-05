import numpy as np

def sharpe(returns):

    if len(returns) < 2:
        return 0

    mean = np.mean(returns)
    std = np.std(returns)

    if std == 0:
        return 0

    return mean / std


def max_drawdown(equity_curve):

    peak = equity_curve[0]
    max_dd = 0

    for x in equity_curve:
        if x > peak:
            peak = x

        dd = (peak - x) / peak
        max_dd = max(max_dd, dd)

    return max_dd


def expectancy(wins, losses):

    total = wins + losses
    if total == 0:
        return 0

    return (wins - losses) / total
