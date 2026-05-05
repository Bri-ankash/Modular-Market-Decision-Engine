import yfinance as yf
from mmde_engine.research_engine import run_research

symbols = ["EURUSD=X", "BTC-USD", "AAPL", "NVDA"]

data = {}

for s in symbols:
    df = yf.download(s, period="5d", interval="1h", progress=False)
    data[s] = [{"close": float(x)} for x in df["Close"].dropna().tolist()]

result = run_research(data)

print("\n📊 ALLOCATIONS")
print(result["allocations"])

print("\n🏆 RANKING")
print(result["ranking"])
