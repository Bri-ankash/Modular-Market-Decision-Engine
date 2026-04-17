"""
Real market data fetcher.
Primary: yfinance (free, no key needed)
Secondary: Alpha Vantage (free tier, key needed)
Returns list of OHLCV dicts for MMDE engine.
"""
import os
from datetime import datetime, timedelta

ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')

# Symbol mappings to yfinance tickers
SYMBOL_MAP = {
    # Forex
    'EURUSD': 'EURUSD=X', 'GBPUSD': 'GBPUSD=X', 'USDJPY': 'JPY=X',
    'AUDUSD': 'AUDUSD=X', 'USDCHF': 'CHF=X', 'NZDUSD': 'NZDUSD=X',
    'USDCAD': 'CAD=X', 'EURGBP': 'EURGBP=X', 'EURJPY': 'EURJPY=X',
    # Gold
    'XAUUSD': 'GC=F', 'GOLD': 'GC=F', 'XAGUSD': 'SI=F',
    # Indices
    'US30': 'YM=F', 'SPX500': 'ES=F', 'NAS100': 'NQ=F',
    'DAX': 'DAX=F', 'FTSE100': 'Z=F', 'US500': 'ES=F',
    # Crypto
    'BTCUSD': 'BTC-USD', 'ETHUSD': 'ETH-USD', 'BNBUSD': 'BNB-USD',
    'SOLUSD': 'SOL-USD', 'XRPUSD': 'XRP-USD',
    # Stocks
    'AAPL': 'AAPL', 'TSLA': 'TSLA', 'GOOGL': 'GOOGL',
    'MSFT': 'MSFT', 'AMZN': 'AMZN', 'NVDA': 'NVDA',
    'META': 'META', 'SAFCOM': 'SCOM.NR',
}

INTERVALS = {
    '1m': '1m', '5m': '5m', '15m': '15m',
    '30m': '30m', '1h': '60m', '4h': '1d',
    '1d': '1d', '1w': '1wk',
}

def fetch(symbol: str, interval: str = '1h', limit: int = 50) -> dict:
    """
    Returns {'candles': [...], 'symbol': ..., 'interval': ..., 'source': ...}
    candles: [{open, high, low, close, volume, timestamp}]
    """
    ticker_sym = SYMBOL_MAP.get(symbol.upper(), symbol)

    # Try yfinance first (free, no key)
    try:
        return _fetch_yfinance(ticker_sym, symbol, interval, limit)
    except Exception as e:
        print(f'[yfinance] {e}')

    # Fallback: Alpha Vantage
    try:
        return _fetch_alpha_vantage(symbol, interval, limit)
    except Exception as e:
        print(f'[AlphaVantage] {e}')

    # Last resort: demo synthetic data
    return _demo_data(symbol, interval, limit)

def _fetch_yfinance(ticker_sym, symbol, interval, limit):
    import yfinance as yf

    yf_interval = INTERVALS.get(interval, '1h')
    # Period based on interval
    period_map = {
        '1m':'1d', '5m':'5d', '15m':'7d', '30m':'14d',
        '60m':'30d', '1d':'90d', '1wk':'1y'
    }
    period = period_map.get(yf_interval, '30d')

    ticker = yf.Ticker(ticker_sym)
    df = ticker.history(period=period, interval=yf_interval)

    if df.empty:
        raise ValueError('No data returned from yfinance')

    candles = []
    for idx, row in df.tail(limit).iterrows():
        candles.append({
            'timestamp': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
            'open': round(float(row['Open']), 5),
            'high': round(float(row['High']), 5),
            'low': round(float(row['Low']), 5),
            'close': round(float(row['Close']), 5),
            'volume': int(row.get('Volume', 0)),
        })

    return {
        'candles': candles,
        'symbol': symbol,
        'interval': interval,
        'source': 'yfinance',
        'count': len(candles),
        'last_price': candles[-1]['close'] if candles else None,
        'last_update': str(datetime.utcnow()),
    }

def _fetch_alpha_vantage(symbol, interval, limit):
    import requests

    interval_map = {
        '1m':'1min', '5m':'5min', '15m':'15min',
        '30m':'30min', '1h':'60min',
    }
    av_interval = interval_map.get(interval, '60min')

    # Forex
    if len(symbol) == 6 and symbol.upper() not in ['XAUUSD','XAGUSD']:
        from_sym = symbol[:3]
        to_sym = symbol[3:]
        url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={from_sym}&to_symbol={to_sym}&interval={av_interval}&apikey={ALPHA_VANTAGE_KEY}&outputsize=compact"
        r = requests.get(url, timeout=10).json()
        key = f"Time Series FX ({av_interval})"
    else:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={av_interval}&apikey={ALPHA_VANTAGE_KEY}&outputsize=compact"
        r = requests.get(url, timeout=10).json()
        key = f"Time Series ({av_interval})"

    if key not in r:
        raise ValueError(f'Alpha Vantage: {r.get("Note", r.get("Information","No data"))}')

    ts = r[key]
    candles = []
    for time_str, values in sorted(ts.items())[-limit:]:
        candles.append({
            'timestamp': time_str,
            'open': float(values.get('1. open', values.get('open', 0))),
            'high': float(values.get('2. high', values.get('high', 0))),
            'low': float(values.get('3. low', values.get('low', 0))),
            'close': float(values.get('4. close', values.get('close', 0))),
            'volume': int(float(values.get('5. volume', values.get('volume', 0)))),
        })

    return {
        'candles': candles,
        'symbol': symbol,
        'interval': interval,
        'source': 'alpha_vantage',
        'count': len(candles),
        'last_price': candles[-1]['close'] if candles else None,
    }

def _demo_data(symbol, interval, limit):
    """Synthetic demo data when all sources fail"""
    import random, math
    candles = []
    price = {'EURUSD': 1.0850, 'XAUUSD': 2330.0, 'BTCUSD': 67000.0,
             'US30': 39500.0, 'TSLA': 215.0}.get(symbol.upper(), 1.0000)
    for i in range(limit):
        o = price
        change = (random.random() - 0.49) * price * 0.002
        c = round(o + change, 5)
        h = round(max(o, c) + random.random() * price * 0.001, 5)
        l = round(min(o, c) - random.random() * price * 0.001, 5)
        v = random.randint(500, 15000)
        candles.append({'timestamp': str(i), 'open': o, 'high': h, 'low': l, 'close': c, 'volume': v})
        price = c
    return {'candles': candles, 'symbol': symbol, 'interval': interval, 'source': 'demo', 'count': limit, 'last_price': price}

def get_current_price(symbol: str) -> float:
    """Quick current price fetch"""
    try:
        result = fetch(symbol, '1m', 2)
        return result['last_price']
    except:
        return 0.0

def get_supported_symbols() -> list:
    return list(SYMBOL_MAP.keys())
