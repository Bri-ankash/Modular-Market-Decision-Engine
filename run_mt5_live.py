from mmde_engine.mmde_orchestrator import execute_live_trade

symbols = ["EURUSD", "BTCUSD", "AAPL"]

for s in symbols:
    trade = execute_live_trade(s, "BUY", 0.01)
    print(trade)
