import random
from mmde_engine.core import run_symbol
from mmde_engine.portfolio import portfolio_status

symbols = ["EURUSD=X", "BTC-USD", "AAPL", "NVDA", "TSLA"]

print("\n======================")
print("MMDE FINAL SYSTEM TEST")
print("======================\n")

results = []

for i in range(20):  # simulate 20 trading cycles

    symbol = random.choice(symbols)

    try:
        result = run_symbol(symbol, balance=1000)

        results.append(result)

        print(result)

    except Exception as e:
        print({"symbol": symbol, "error": str(e)})

print("\n======================")
print("PORTFOLIO STATUS")
print("======================")
print(portfolio_status())
