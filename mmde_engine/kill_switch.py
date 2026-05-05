drawdown_peak = 1000
current_equity = 1000


def update_equity(equity):
    global drawdown_peak, current_equity

    current_equity = equity

    if equity > drawdown_peak:
        drawdown_peak = equity


def should_stop_trading():

    drawdown = (drawdown_peak - current_equity) / drawdown_peak

    if drawdown > 0.1:
        return True, "DRAWDOWN_LIMIT"

    return False, "OK"
