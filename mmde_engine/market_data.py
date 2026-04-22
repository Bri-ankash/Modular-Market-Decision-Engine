"""
MMDE Market Data Fetcher
Sources: yfinance (primary) → Alpha Vantage (fallback) → demo
"""
import os

# Symbol map to yfinance tickers
SYMBOL_MAP = {
    # Forex
    'EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'JPY=X',
    'AUDUSD':'AUDUSD=X','USDCHF':'CHF=X','NZDUSD':'NZDUSD=X',
    'USDCAD':'CAD=X','EURGBP':'EURGBP=X','EURJPY':'EURJPY=X',
    'GBPJPY':'GBPJPY=X','EURAUD':'EURAUD=X','GBPCAD':'GBPCAD=X',
    # Gold & metals
    'XAUUSD':'GC=F','GOLD':'GC=F','XAGUSD':'SI=F','XAUEUR':'GC=F',
    # Indices
    'US30':'YM=F','DJ30':'YM=F','DOW':'YM=F',
    'NAS100':'NQ=F','NASDAQ':'NQ=F',
    'SPX500':'ES=F','SP500':'ES=F',
    'GER40':'GDAXI','UK100':'FTSE','JPN225':'NKY=F',
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

# yfinance interval map (MMDE → yfinance)
INTERVAL_MAP = {
    'M1':'1m','M5':'5m','M15':'15m','M30':'30m',
    'H1':'1h','H4':'1h','D1':'1d','W1':'1wk',
    '1m':'1m','5m':'5m','15m':'15m','30m':'30m',
    '1h':'1h','4h':'1h','1d':'1d','1w':'1wk',
}

# Period to use per interval
PERIOD_MAP = {
    '1m':'1d','5m':'5d','15m':'30d','30m':'30d',
    '1h':'60d','1d':'180d','1wk':'730d',
}


def fetch(symbol: str, interval: str = 'H1', limit: int = 50) -> dict:
    """Main entry — tries yfinance first, then fallback"""
    ticker_sym = SYMBOL_MAP.get(symbol.upper(), symbol)
    yf_interval = INTERVAL_MAP.get(interval, '1h')

    try:
        return _fetch_yfinance(ticker_sym, symbol, yf_interval, limit)
    except Exception as e:
        print(f'[yfinance FAIL] {ticker_sym} {yf_interval}: {e}')

    # Fallback to demo
    return _demo_data(symbol, interval, limit)


def _fetch_yfinance(ticker_sym, symbol, yf_interval, limit):
    import yfinance as yf

    period = PERIOD_MAP.get(yf_interval, '60d')

    ticker = yf.Ticker(ticker_sym)
    df = ticker.history(period=period, interval=yf_interval)

    if df is None or df.empty:
        raise ValueError(f'No data returned for {ticker_sym}')

    # Handle MultiIndex columns (new yfinance versions)
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.droplevel(1)

    # Normalise column names
    df.columns = [c.lower() for c in df.columns]

    required = {'open', 'high', 'low', 'close'}
    if not required.issubset(set(df.columns)):
        raise ValueError(f'Missing OHLC columns. Got: {list(df.columns)}')

    df = df.tail(limit)
    candles = []
    for idx, row in df.iterrows():
        ts = idx.strftime('%Y-%m-%d %H:%M') if hasattr(idx, 'strftime') else str(idx)
        candles.append({
            'timestamp': ts,
            'open':   round(float(row['open']),  5),
            'high':   round(float(row['high']),  5),
            'low':    round(float(row['low']),   5),
            'close':  round(float(row['close']), 5),
            'volume': int(row.get('volume', 0) or 0),
        })

    return {
        'candles':    candles,
        'symbol':     symbol,
        'interval':   yf_interval,
        'source':     'Yahoo Finance',
        'count':      len(candles),
        'last_price': candles[-1]['close'] if candles else None,
    }


def _demo_data(symbol, interval, limit):
    import random
    starts = {
        'EURUSD':1.0850,'GBPUSD':1.2650,'XAUUSD':2340.0,
        'BTCUSD':67000.0,'US30':39500.0,'NAS100':17800.0,
        'USDJPY':149.50,'TSLA':215.0,'AAPL':185.0,
    }
    price = starts.get(symbol.upper(), 1.0850)
    candles = []
    for i in range(limit):
        o = round(price, 5)
        change = (random.random() - 0.495) * price * 0.002
        c = round(o + change, 5)
        h = round(max(o, c) + random.random() * price * 0.001, 5)
        l = round(min(o, c) - random.random() * price * 0.001, 5)
        v = random.randint(800, 18000)
        candles.append({'timestamp': f'C{i+1}', 'open':o,'high':h,'low':l,'close':c,'volume':v})
        price = c
    return {
        'candles':candles,'symbol':symbol,'interval':interval,
        'source':'Demo (offline)','count':len(candles),
        'last_price': round(price, 5),
    }
