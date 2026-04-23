"""
MMDE Market Data — Pure requests, zero pandas/yfinance.
Hits Yahoo Finance JSON API directly. Works on Termux + Render.
"""
import requests
import json
import time as time_mod

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://finance.yahoo.com',
}

# MMDE symbol → Yahoo Finance ticker
SYMBOL_MAP = {
    # Forex
    'EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'JPY=X',
    'AUDUSD':'AUDUSD=X','USDCHF':'CHF=X','NZDUSD':'NZDUSD=X',
    'USDCAD':'CAD=X','EURGBP':'EURGBP=X','EURJPY':'EURJPY=X',
    'GBPJPY':'GBPJPY=X','EURAUD':'EURAUD=X','GBPCAD':'GBPCAD=X',
    'USDZAR':'ZAR=X','USDMXN':'MXN=X','USDTRY':'TRY=X',
    # Gold & metals
    'XAUUSD':'GC=F','GOLD':'GC=F','XAGUSD':'SI=F','XAUEUR':'GC=F',
    # Indices
    'US30':'YM=F','DJ30':'YM=F','DOW':'YM=F',
    'NAS100':'NQ=F','NASDAQ':'NQ=F',
    'SPX500':'ES=F','SP500':'ES=F','US500':'ES=F',
    'GER40':'DAX=F','UK100':'^FTSE',
    # Crypto
    'BTCUSD':'BTC-USD','BITCOIN':'BTC-USD',
    'ETHUSD':'ETH-USD','BNBUSD':'BNB-USD',
    'SOLUSD':'SOL-USD','XRPUSD':'XRP-USD',
    'ADAUSD':'ADA-USD','DOTUSD':'DOT-USD',
    # Stocks
    'AAPL':'AAPL','TSLA':'TSLA','GOOGL':'GOOGL',
    'MSFT':'MSFT','AMZN':'AMZN','NVDA':'NVDA',
    'META':'META','NFLX':'NFLX','AMD':'AMD',
}

# interval → (yahoo_interval, yahoo_range)
INTERVAL_CFG = {
    'M1' :('1m' ,'1d' ),
    'M5' :('5m' ,'5d' ),
    'M15':('15m','30d'),
    'M30':('30m','30d'),
    'H1' :('60m','60d'),
    'H4' :('60m','60d'),
    'D1' :('1d' ,'1y' ),
    'W1' :('1wk','5y' ),
    # lowercase aliases
    '1m' :('1m' ,'1d' ),
    '5m' :('5m' ,'5d' ),
    '15m':('15m','30d'),
    '30m':('30m','30d'),
    '1h' :('60m','60d'),
    '4h' :('60m','60d'),
    '1d' :('1d' ,'1y' ),
    '1w' :('1wk','5y' ),
}


def fetch(symbol: str, interval: str = 'H1', limit: int = 50) -> dict:
    """
    Returns dict:
      candles   — list of {open,high,low,close,volume,timestamp}
      symbol    — original symbol
      interval  — interval used
      source    — where data came from
      count     — number of candles
      last_price— latest close
    """
    yahoo_sym = SYMBOL_MAP.get(symbol.upper(), symbol)
    yf_int, yf_range = INTERVAL_CFG.get(interval, ('60m', '60d'))

    # Try both Yahoo query endpoints
    for base in ['query1', 'query2']:
        try:
            result = _call_yahoo(base, yahoo_sym, symbol, yf_int, yf_range, limit)
            if result and result['count'] > 0:
                return result
        except Exception as e:
            print(f'[{base}] {yahoo_sym}: {e}')
            continue

    # All failed — return demo
    print(f'[market_data] Yahoo unavailable, using demo for {symbol}')
    return _demo(symbol, interval, limit)


def _call_yahoo(base, yahoo_sym, original_sym, yf_int, yf_range, limit):
    url = (
        f'https://{base}.finance.yahoo.com/v8/finance/chart/{yahoo_sym}'
        f'?interval={yf_int}&range={yf_range}'
        f'&includePrePost=false&events=none'
    )

    resp = requests.get(url, headers=HEADERS, timeout=12)

    # Check we got JSON not HTML
    ct = resp.headers.get('Content-Type', '')
    if 'text/html' in ct or resp.text.strip().startswith('<!'):
        raise ValueError('Got HTML instead of JSON — Yahoo blocked or redirected')

    if resp.status_code != 200:
        raise ValueError(f'HTTP {resp.status_code}')

    data = resp.json()
    chart = data.get('chart', {})
    err   = chart.get('error')
    if err:
        raise ValueError(f"Yahoo error: {err.get('description','unknown')}")

    results = chart.get('result', [])
    if not results:
        raise ValueError('Empty result from Yahoo')

    block      = results[0]
    meta       = block.get('meta', {})
    timestamps = block.get('timestamp', [])
    indicators = block.get('indicators', {})
    quote      = indicators.get('quote', [{}])[0]

    opens  = quote.get('open',   [])
    highs  = quote.get('high',   [])
    lows   = quote.get('low',    [])
    closes = quote.get('close',  [])
    vols   = quote.get('volume', [])

    if not timestamps or not closes:
        raise ValueError('No OHLCV data in response')

    candles = []
    for i in range(len(timestamps)):
        try:
            o = opens[i]  if i < len(opens)  else None
            h = highs[i]  if i < len(highs)  else None
            l = lows[i]   if i < len(lows)   else None
            c = closes[i] if i < len(closes) else None
            v = vols[i]   if i < len(vols)   else 0

            # Skip NaN / None candles (gaps, holidays)
            if any(x is None for x in [o, h, l, c]):
                continue
            if c != c:  # NaN check
                continue

            ts = time_mod.strftime(
                '%Y-%m-%d %H:%M',
                time_mod.gmtime(timestamps[i])
            )
            candles.append({
                'timestamp': ts,
                'open':   round(float(o), 5),
                'high':   round(float(h), 5),
                'low':    round(float(l), 5),
                'close':  round(float(c), 5),
                'volume': int(v or 0),
            })
        except Exception:
            continue

    candles = candles[-limit:]

    return {
        'candles':    candles,
        'symbol':     original_sym.upper(),
        'interval':   yf_int,
        'source':     f'Yahoo Finance (live) via {base}',
        'count':      len(candles),
        'last_price': candles[-1]['close'] if candles else 0,
        'currency':   meta.get('currency', ''),
    }


def _demo(symbol, interval, limit):
    """
    Generates realistic synthetic candles when Yahoo is unreachable.
    Uses real-world price ranges so analysis makes sense.
    """
    import random

    base_prices = {
        'EURUSD':1.0850,'GBPUSD':1.2650,'USDJPY':149.50,
        'AUDUSD':0.6550,'USDCHF':0.9050,'XAUUSD':2340.0,
        'GOLD':2340.0,'BTCUSD':67000.,'ETHUSD':3500.,
        'US30':39500.,'NAS100':17800.,'SPX500':5200.,
        'TSLA':215.,'AAPL':185.,'NVDA':870.,'MSFT':415.,
    }
    price    = base_prices.get(symbol.upper(), 1.0)
    volatility = price * 0.0012

    candles = []
    # Simulate a realistic trending + ranging market
    trend = 1
    for i in range(limit):
        if i % 15 == 0:  # change trend every 15 candles
            trend = random.choice([1, -1, 1])

        o = round(price, 5)
        body   = random.random() * volatility * trend
        wick_h = random.random() * volatility * 0.5
        wick_l = random.random() * volatility * 0.5
        c = round(o + body, 5)
        h = round(max(o, c) + wick_h, 5)
        l = round(min(o, c) - wick_l, 5)
        v = random.randint(3000, 25000)

        candles.append({
            'timestamp': f'C{i+1}',
            'open':o, 'high':h, 'low':l, 'close':c, 'volume':v,
        })
        price = c

    return {
        'candles':    candles,
        'symbol':     symbol.upper(),
        'interval':   interval,
        'source':     'Demo data (Yahoo unreachable — paste your own or use TradingView)',
        'count':      len(candles),
        'last_price': round(price, 5),
    }
