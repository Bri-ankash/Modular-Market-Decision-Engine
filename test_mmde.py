import sys
sys.path.insert(0, '.')

from mmde_engine.market_data import fetch, get_price

print("=" * 65)
print("MMDE MARKET DATA — FULL TEST")
print("=" * 65)

tests = [
    ('EURUSD',  'H1',  30, 'Major Forex'),
    ('GBPJPY',  'H1',  20, 'Minor Forex'),
    ('XAUUSD',  'H1',  20, 'Gold'),
    ('XAGUSD',  'D1',  15, 'Silver'),
    ('WTI',     'D1',  15, 'Oil'),
    ('BTCUSD',  'H1',  20, 'Crypto'),
    ('ETHUSD',  'D1',  15, 'Crypto'),
    ('US30',    'H1',  20, 'Index'),
    ('NAS100',  'H1',  20, 'Index'),
    ('AAPL',    'D1',  20, 'Stock'),
    ('NVDA',    'D1',  15, 'Stock'),
    ('TSLA',    'H1',  20, 'Stock'),
]

ok = 0
fail = 0

for sym, tf, n, desc in tests:
    try:
        data = fetch(sym, tf, n)

        if not data or len(data) < 2:
            print(f"{sym:10} | ❌ No data")
            fail += 1
            continue

        last = get_price(sym)

        closes = [c['close'] for c in data if 'close' in c]

        if len(closes) < 2:
            print(f"{sym:10} | ❌ Not enough close data")
            fail += 1
            continue

        chg = ((closes[-1] - closes[0]) / closes[0]) * 100
        sign = "+" if chg >= 0 else ""

        print(f"{sym:10} | {len(data):3} candles | {str(last):>12} | {sign}{chg:.3f}% | {desc}")

        ok += 1

    except Exception as e:
        print(f"{sym:10} | ❌ ERROR: {e}")
        fail += 1

print("=" * 65)
print(f"RESULTS → OK: {ok} | FAIL: {fail}")
print("=" * 65)
