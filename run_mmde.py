from mmde_engine.core import run_symbol

symbols = ["EURUSD=X", "BTC-USD", "AAPL"]

results = []

for s in symbols:
    r = run_symbol(s)
    results.append(r)
    print(r)

print("\nDONE")
