from mmde_engine.data import get_candles
from mmde_engine.strategy import score_market
from mmde_engine.risk import risk_check
from mmde_engine.execution import execute_trade

def run_symbol(symbol):

    candles = get_candles(symbol)

    if not candles:
        return {"symbol": symbol, "status": "NO_DATA"}

    score = score_market(candles)

    if not risk_check(candles, score):
        return {"symbol": symbol, "status": "BLOCKED"}

    trade = execute_trade(symbol, candles, score)

    return trade
