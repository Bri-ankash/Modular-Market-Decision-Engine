"""
MMDE Market Data — Zero pandas, zero yfinance.
Pure requests → Yahoo Finance JSON API.
Works on Termux, Render, anywhere.
"""
import requests, json, time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# MMDE symbol → Yahoo Finance symbol
SYMBOL_MAP = {
    # Forex
    'EURUSD':'EURUSD=X', 'GBPUSD':'GBPUSD=X', 'USDJPY':'JPY=X',
    'AUDUSD':'AUDUSD=X', 'USDCHF':'CHF=X',    'NZDUSD':'NZDUSD=X',
    'USDCAD':'CAD=X',    'EURGBP':'EURGBP=X', 'EURJPY':'EURJPY=X',
    'GBPJPY':'GBPJPY=X', 'EURAUD':'EURAUD=X', 'GBPCAD':'GBPCAD=X',
    'USDZAR':'ZAR=X',    'USDKES':'KES=X',
    # Gold & metals
    'XAUUSD':'GC=F', 'GOLD':'GC=F', 'XAGUSD':'SI=F',
    # Indices
    'US30':'YM=F',   'DOW':'YM=F',
    'NAS100':'NQ=F', 'NASDAQ':'NQ=F',
    'SPX500':'ES=F', 'SP500':'ES=F',
    'GER40':'DAX=F', 'UK100':'^FTSE',
    # Crypto
    'BTCUSD':'BTC-USD', 'BITCOIN':'BTC-USD',
    'ETHUSD':'ETH-USD', 'BNBUSD':'BNB-USD',
    'SOLUSD':'SOL-USD', 'XRPUSD':'XRP-USD',
    'ADAUSD':'ADA-USD',
    # Stocks
    'AAPL':'AAPL', 'TSLA':'TSLA', 'GOOGL':'GOOGL',
    'MSFT':'MSFT', 'AMZN':'AMZN', 'NVDA':'NVDA',
    'META':'META', 'NFLX':'NFLX', 'AMD':'AMD',
}

# MMDE interval → Yahoo interval + range
INTERVAL_CONFIG = {
    'M1':  ('1m',  '1d'),
    'M5':  ('5m',  '5d'),
    'M15': ('15m', '30d'),
    'M30': ('30m', '30d'),
    'H1':  ('1h',  '60d'),
    'H4':  ('1h',  '60d'),   # Yahoo has no 4h, use 1h
    'D1':  ('1d',  '180d'),
    'W1':  ('1wk', '2y'),
    # also accept lowercase
    '1m':  ('1m',  '1d'),
    '5m':  ('5m',  '5d'),
    '15m': ('15m', '30d'),
    '30m': ('30m', '30d'),
    '1h':  ('1h',  '60d'),
    '4h':  ('1h',  '60d'),
    '1d':  ('1d',  '180d'),
    '1w':  ('1wk', '2y'),
}


def fetch(symbol: str, interval: str = 'H1', limit: int = 50) -> dict:
    """
    Fetch OHLCV candles. Returns dict with 'candles' list.
    Falls back to demo data if network fails.
    """
    yahoo_sym  = SYMBOL_MAP.get(symbol.upper(), symbol)
    yf_int, yf_range = INTERVAL_CONFIG.get(interval, ('1h', '60d'))

    try:
        return _yahoo_direct(yahoo_sym, symbol, yf_int, yf_range, limit)
    except Exception as e:
        print(f'[Yahoo HTTP] {yahoo_sym}: {e}')
        return _demo(symbol, interval, limit)


def _yahoo_direct(yahoo_sym, original_sym, interval, range_, limit):
    """
    Calls Yahoo Finance chart API directly — no pandas, pure JSON.
    """
    url = (
        f'https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}'
        f'?interval={interval}&range={range_}&includePrePost=false'
    )

    r = requests.get(url, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        raise ValueError(f'Yahoo returned {r.status_code}')

    data = r.json()

    result  = data.get('chart', {}).get('result', [])
    if not result:
        err = data.get('chart', {}).get('error', {})
        raise ValueError(f'No data: {err}')

    block     = result[0]
    meta      = block.get('meta', {})
    timestamps= block.get('timestamp', [])
    quote     = block.get('indicators', {}).get('quote', [{}])[0]

    opens  = quote.get('open',   [])
    highs  = quote.get('high',   [])
    lows   = quote.get('low',    [])
    closes = quote.get('close',  [])
    vols   = quote.get('volume', [])

    if not closes:
        raise ValueError('Empty OHLCV arrays')

    candles = []
    for i in range(len(timestamps)):
        o = opens[i]  if i < len(opens)  else None
        h = highs[i]  if i < len(highs)  else None
        l = lows[i]   if i < len(lows)   else None
        c = closes[i] if i < len(closes) else None
        v = vols[i]   if i < len(vols)   else 0

        # Skip None/NaN candles (market closed gaps)
        if None in (o, h, l, c) or c != c:  # c!=c catches NaN
            continue

        ts = time.strftime('%Y-%m-%d %H:%M', time.gmtime(timestamps[i]))
        candles.append({
            'timestamp': ts,
            'open':   round(float(o), 5),
            'high':   round(float(h), 5),
            'low':    round(float(l), 5),
            'close':  round(float(c), 5),
            'volume': int(v or 0),
        })

    # Return last `limit` candles
    candles = candles[-limit:]

    return {
        'candles':    candles,
        'symbol':     original_sym,
        'interval':   interval,
        'source':     'Yahoo Finance (live)',
        'count':      len(candles),
        'last_price': candles[-1]['close'] if candles else None,
        'currency':   meta.get('currency', ''),
    }


def _demo(symbol, interval, limit):
    """Offline fallback — synthetic data so UI never breaks."""
    import random
    base = {
        'EURUSD':1.0850,'GBPUSD':1.2650,'XAUUSD':2340.0,
        'BTCUSD':67000.,'US30':39500.,'NAS100':17800.,
        'USDJPY':149.50,'TSLA':215.,'AAPL':185.,'NVDA':870.,
    }.get(symbol.upper(), 1.0850)

    candles, price = [], base
    for i in range(limit):
        o = round(price, 5)
        move = (random.random() - 0.495) * base * 0.0015
        c = round(o + move, 5)
        h = round(max(o,c) + random.random() * base * 0.0008, 5)
        l = round(min(o,c) - random.random() * base * 0.0008, 5)
        candles.append({'timestamp':f'C{i+1}','open':o,'high':h,'low':l,'close':c,'volume':random.randint(500,15000)})
        price = c

    return {
        'candles':candles,'symbol':symbol,'interval':interval,
        'source':'Demo (network unavailable)','count':len(candles),
        'last_price':round(price,5),
    }


def get_price(symbol: str) -> float:
    """Quick single price fetch."""
    try:
        r = fetch(symbol, 'M1', 2)
        return r.get('last_price', 0)
    except:
        return 0.0
