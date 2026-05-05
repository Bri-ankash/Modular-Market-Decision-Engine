"""
MMDE Market Data Fetcher — Best Version
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Author:   Kaliworks Technologies
Version:  3.0 (full PC version)

Sources (in order of priority):
  1. yfinance  — most reliable, handles splits/dividends
  2. Yahoo HTTP — direct API, no yfinance overhead
  3. Demo data  — realistic synthetic, never crashes app

Covers:
  - 70+ Forex pairs
  - Gold, Silver, Platinum, Oil
  - US + EU + UK + JP + AU Indices
  - Top 15 Crypto pairs
  - 30+ Stocks
  - Timeframes: M1 to W1
"""

import time as time_mod
import random
import math
import logging

logger = logging.getLogger(_name_)

# ═══════════════════════════════════════════════════════
# SYMBOL MAP — MMDE name → Yahoo Finance ticker
# ═══════════════════════════════════════════════════════
SYMBOL_MAP = {

    # ── MAJOR FOREX ──
    'EURUSD':'EURUSD=X', 'GBPUSD':'GBPUSD=X', 'USDJPY':'JPY=X',
    'USDCHF':'CHF=X',    'AUDUSD':'AUDUSD=X', 'NZDUSD':'NZDUSD=X',
    'USDCAD':'CAD=X',

    # ── MINOR FOREX ──
    'EURGBP':'EURGBP=X', 'EURJPY':'EURJPY=X', 'EURAUD':'EURAUD=X',
    'EURCAD':'EURCAD=X', 'EURCHF':'EURCHF=X', 'EURNZD':'EURNZD=X',
    'GBPJPY':'GBPJPY=X', 'GBPAUD':'GBPAUD=X', 'GBPCAD':'GBPCAD=X',
    'GBPCHF':'GBPCHF=X', 'GBPNZD':'GBPNZD=X',
    'AUDJPY':'AUDJPY=X', 'AUDCAD':'AUDCAD=X', 'AUDCHF':'AUDCHF=X',
    'AUDNZD':'AUDNZD=X', 'CADJPY':'CADJPY=X', 'CHFJPY':'CHFJPY=X',
    'NZDJPY':'NZDJPY=X', 'NZDCAD':'NZDCAD=X', 'NZDCHF':'NZDCHF=X',

    # ── EXOTIC FOREX ──
    'USDZAR':'ZAR=X', 'USDMXN':'MXN=X', 'USDTRY':'TRY=X',
    'USDSEK':'SEK=X', 'USDNOK':'NOK=X', 'USDDKK':'DKK=X',
    'USDSGD':'SGD=X', 'USDHKD':'HKD=X', 'USDKES':'KES=X',

    # ── GOLD & METALS ──
    'XAUUSD':'GC=F',  'GOLD':'GC=F',
    'XAGUSD':'SI=F',  'SILVER':'SI=F',
    'XPTUSD':'PL=F',  'PLATINUM':'PL=F',
    'XPDUSD':'PA=F',  'COPPER':'HG=F',

    # ── OIL & ENERGY ──
    'USOIL':'CL=F',  'WTI':'CL=F',  'BRENT':'BZ=F',
    'NATGAS':'NG=F',

    # ── US INDICES ──
    'US30':'YM=F',    'DOW':'YM=F',   'DJ30':'YM=F',
    'NAS100':'NQ=F',  'NASDAQ':'NQ=F','US100':'NQ=F',
    'SPX500':'ES=F',  'SP500':'ES=F', 'US500':'ES=F',
    'US2000':'RTY=F', 'VIX':'^VIX',

    # ── GLOBAL INDICES ──
    'GER40':'^GDAXI',  'DAX':'^GDAXI',
    'UK100':'^FTSE',   'FTSE':'^FTSE',
    'JPN225':'^N225',  'NIKKEI':'^N225',
    'AUS200':'^AXJO',  'FRA40':'^FCHI',
    'ESP35':'^IBEX',   'ITA40':'FTSEMIB.MI',
    'HK50':'^HSI',     'CHN50':'000300.SS',

    # ── CRYPTO ──
    'BTCUSD':'BTC-USD',   'BITCOIN':'BTC-USD',
    'ETHUSD':'ETH-USD',   'ETHEREUM':'ETH-USD',
    'BNBUSD':'BNB-USD',   'SOLUSD':'SOL-USD',
    'XRPUSD':'XRP-USD',   'ADAUSD':'ADA-USD',
    'DOTUSD':'DOT-USD',   'AVAXUSD':'AVAX-USD',
    'MATICUSD':'MATIC-USD','LINKUSD':'LINK-USD',
    'LTCUSD':'LTC-USD',   'ETCUSD':'ETC-USD',
    'DOGEUSD':'DOGE-USD',

    # ── US STOCKS ──
    'AAPL':'AAPL',   'MSFT':'MSFT',  'GOOGL':'GOOGL',
    'GOOG':'GOOG',   'AMZN':'AMZN',  'META':'META',
    'TSLA':'TSLA',   'NVDA':'NVDA',  'AMD':'AMD',
    'NFLX':'NFLX',   'UBER':'UBER',  'COIN':'COIN',
    'BABA':'BABA',   'V':'V',        'JPM':'JPM',
    'BAC':'BAC',     'WMT':'WMT',    'DIS':'DIS',
    'PYPL':'PYPL',   'INTC':'INTC',  'ORCL':'ORCL',
    'SHOP':'SHOP',   'SQ':'SQ',      'PLTR':'PLTR',
    'RBLX':'RBLX',   'SNAP':'SNAP',  'TWTR':'TWTR',
}

# ═══════════════════════════════════════════════════════
# INTERVAL MAP — MMDE timeframe → (yfinance interval, period)
# ═══════════════════════════════════════════════════════
INTERVAL_MAP = {
    'M1':  ('1m',  '1d'),     # 1 minute — last 1 day
    'M5':  ('5m',  '5d'),     # 5 minutes — last 5 days
    'M15': ('15m', '30d'),    # 15 minutes — last 30 days
    'M30': ('30m', '30d'),    # 30 minutes — last 30 days
    'H1':  ('1h',  '60d'),    # 1 hour — last 60 days
    'H4':  ('1h',  '60d'),    # 4 hour — yfinance has no 4h, use 1h
    'D1':  ('1d',  '365d'),   # Daily — last 1 year
    'W1':  ('1wk', '730d'),   # Weekly — last 2 years
    # lowercase aliases
    '1m':  ('1m',  '1d'),
    '5m':  ('5m',  '5d'),
    '15m': ('15m', '30d'),
    '30m': ('30m', '30d'),
    '1h':  ('1h',  '60d'),
    '4h':  ('1h',  '60d'),
    '1d':  ('1d',  '365d'),
    '1w':  ('1wk', '730d'),
}

# ═══════════════════════════════════════════════════════
# REALISTIC BASE PRICES for demo mode
# ═══════════════════════════════════════════════════════
BASE_PRICES = {
    'EURUSD':1.0850, 'GBPUSD':1.2650, 'USDJPY':149.50,
    'AUDUSD':0.6550, 'USDCHF':0.9050, 'NZDUSD':0.6020,
    'USDCAD':1.3650, 'EURGBP':0.8580, 'EURJPY':162.10,
    'GBPJPY':189.20, 'XAUUSD':2340.0, 'GOLD':2340.0,
    'XAGUSD':29.50,  'WTI':78.50,     'BRENT':82.50,
    'BTCUSD':67000., 'ETHUSD':3500.,  'BNBUSD':590.,
    'SOLUSD':145.,   'XRPUSD':0.52,   'ADAUSD':0.45,
    'US30':39500.,   'NAS100':17800., 'SPX500':5200.,
    'GER40':18200.,  'UK100':8350.,   'JPN225':38500.,
    'TSLA':215.,     'AAPL':185.,     'NVDA':870.,
    'MSFT':415.,     'GOOGL':175.,    'META':520.,
    'AMZN':195.,     'AMD':165.,      'NFLX':640.,
}


# ═══════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════

def fetch(symbol: str, interval: str = 'H1', limit: int = 50) -> dict:
    """
    Fetch OHLCV market data.

    Args:
        symbol:   e.g. 'EURUSD', 'XAUUSD', 'BTCUSD', 'AAPL'
        interval: e.g. 'M1','M5','M15','M30','H1','H4','D1','W1'
        limit:    number of candles to return (max 500)

    Returns:
        {
            candles:    list of {open, high, low, close, volume, timestamp}
            symbol:     str
            interval:   str
            source:     str  (where data came from)
            count:      int
            last_price: float
            currency:   str
            change_pct: float  (% change last candle)
        }
    """
    limit      = max(3, min(limit, 500))
    ticker_sym = SYMBOL_MAP.get(symbol.upper(), symbol)
    yf_int, yf_period = INTERVAL_MAP.get(interval, ('1h', '60d'))

    # ── Source 1: yfinance (best quality) ──
    try:
        result = _fetch_yfinance(ticker_sym, symbol, yf_int, yf_period, limit)
        if result['count'] > 0:
            logger.info(f"[yfinance] {symbol} {interval}: {result['count']} candles")
            return result
    except Exception as e:
        logger.warning(f"[yfinance] {ticker_sym}: {e}")

    # ── Source 2: Yahoo direct HTTP ──
    try:
        result = _fetch_http(ticker_sym, symbol, yf_int, yf_period, limit)
        if result['count'] > 0:
            logger.info(f"[Yahoo HTTP] {symbol} {interval}: {result['count']} candles")
            return result
    except Exception as e:
        logger.warning(f"[Yahoo HTTP] {ticker_sym}: {e}")

    # ── Source 3: Demo data ──
    logger.warning(f"[market_data] All sources failed for {symbol} — using demo data")
    return _fetch_demo(symbol, interval, limit)


# ═══════════════════════════════════════════════════════
# SOURCE 1 — yfinance (full pandas processing)
# ═══════════════════════════════════════════════════════

def _fetch_yfinance(ticker_sym, symbol, yf_interval, yf_period, limit):
    import yfinance as yf
    import pandas as pd
    import numpy as np

    ticker = yf.Ticker(ticker_sym)
    df     = ticker.history(
        period       = yf_period,
        interval     = yf_interval,
        auto_adjust  = True,
        back_adjust  = False,
        repair       = True,
    )

    if df is None or df.empty:
        raise ValueError(f'Empty dataframe returned for {ticker_sym}')

    # ── Flatten MultiIndex columns (yfinance >= 0.2.40 returns MultiIndex) ──
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ── Normalise column names ──
    df.columns = [str(c).lower().strip() for c in df.columns]

    # ── Ensure required columns exist ──
    required = {'open', 'high', 'low', 'close'}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {missing}. Got: {list(df.columns)}')

    # ── Add volume if missing ──
    if 'volume' not in df.columns:
        df['volume'] = 0

    # ── Drop NaN rows ──
    df = df.dropna(subset=['open', 'high', 'low', 'close'])

    # ── Remove bad rows (high < low, zero prices) ──
    df = df[
        (df['high'] >= df['low']) &
        (df['open'] > 0) &
        (df['close'] > 0)
    ]

    # ── Take last limit candles ──
    df = df.tail(limit).copy()

    if df.empty:
        raise ValueError('No valid rows after cleaning')

    # ── Convert to candle list ──
    candles = []
    for idx, row in df.iterrows():
        try:
            o  = float(row['open'])
            h  = float(row['high'])
            l  = float(row['low'])
            c  = float(row['close'])
            v  = float(row.get('volume', 0) or 0)

            # Format timestamp
            if hasattr(idx, 'strftime'):
                ts = idx.strftime('%Y-%m-%d %H:%M')
            else:
                ts = str(idx)

            # Determine decimal precision
            decimals = _get_decimals(c)

            candles.append({
                'timestamp': ts,
                'open':   round(o, decimals),
                'high':   round(h, decimals),
                'low':    round(l, decimals),
                'close':  round(c, decimals),
                'volume': int(v),
            })
        except Exception:
            continue

    if not candles:
        raise ValueError('All rows failed conversion')

    # ── Calculate change % ──
    change_pct = 0.0
    if len(candles) >= 2:
        prev  = candles[-2]['close']
        last  = candles[-1]['close']
        change_pct = round(((last - prev) / prev) * 100, 4) if prev > 0 else 0.0

    return {
        'candles':    candles,
        'symbol':     symbol.upper(),
        'interval':   yf_interval,
        'source':     'Yahoo Finance (yfinance)',
        'count':      len(candles),
        'last_price': candles[-1]['close'],
        'change_pct': change_pct,
        'currency':   '',
    }


# ═══════════════════════════════════════════════════════
# SOURCE 2 — Direct Yahoo Finance HTTP API
# ═══════════════════════════════════════════════════════

def _fetch_http(ticker_sym, symbol, yf_interval, yf_period, limit):
    import requests

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept':          'application/json, text/plain, /',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer':         'https://finance.yahoo.com',
    }

    last_error = None
    for base in ['query1', 'query2']:
        url = (
            f'https://{base}.finance.yahoo.com/v8/finance/chart/{ticker_sym}'
            f'?interval={yf_interval}&range={yf_period}'
            f'&includePrePost=false&events=none'
        )
        try:
            resp = requests.get(url, headers=headers, timeout=15)

            # Detect HTML error page
            ct = resp.headers.get('Content-Type', '')
            if 'text/html' in ct or resp.text.strip().startswith('<!'):
                last_error = f'{base}: Got HTML (likely rate limited)'
                continue

            if resp.status_code != 200:
                last_error = f'{base}: HTTP {resp.status_code}'
                continue

            data    = resp.json()
            chart   = data.get('chart', {})
            err_msg = chart.get('error')
            if err_msg:
                desc      = err_msg.get('description', 'Unknown') if isinstance(err_msg, dict) else str(err_msg)
                last_error = f'{base}: Yahoo error: {desc}'
                continue

            results = chart.get('result', [])
            if not results:
                last_error = f'{base}: Empty result'
                continue

            block  = results[0]
            times  = block.get('timestamp', [])
            quote  = block.get('indicators', {}).get('quote', [{}])[0]

            opens  = quote.get('open',   [])
            highs  = quote.get('high',   [])
            lows   = quote.get('low',    [])
            closes = quote.get('close',  [])
            vols   = quote.get('volume', [])

            if not times or not closes:
                last_error = f'{base}: No timestamp/close data'
                continue

            candles = []
            for i in range(len(times)):
                try:
                    o = opens[i]  if i < len(opens)  else None
                    h = highs[i]  if i < len(highs)  else None
                    l = lows[i]   if i < len(lows)   else None
                    c = closes[i] if i < len(closes)  else None
                    v = vols[i]   if i < len(vols)    else 0

                    if any(x is None for x in [o, h, l, c]):
                        continue
                    if c != c:  # NaN check
                        continue
                    if float(h) < float(l) or float(c) <= 0:
                        continue

                    ts  = time_mod.strftime('%Y-%m-%d %H:%M', time_mod.gmtime(times[i]))
                    dec = _get_decimals(float(c))

                    candles.append({
                        'timestamp': ts,
                        'open':   round(float(o), dec),
                        'high':   round(float(h), dec),
                        'low':    round(float(l), dec),
                        'close':  round(float(c), dec),
                        'volume': int(v or 0),
                    })
                except Exception:
                    continue

            candles = candles[-limit:]

            if not candles:
                last_error = f'{base}: No valid candles after parsing'
                continue

            change_pct = 0.0
            if len(candles) >= 2:
                prev = candles[-2]['close']
                last = candles[-1]['close']
                change_pct = round(((last - prev) / prev) * 100, 4) if prev > 0 else 0.0

            return {
                'candles':    candles,
                'symbol':     symbol.upper(),
                'interval':   yf_interval,
                'source':     f'Yahoo Finance (HTTP/{base})',
                'count':      len(candles),
                'last_price': candles[-1]['close'],
                'change_pct': change_pct,
                'currency':   '',
            }

        except Exception as e:
            last_error = f'{base}: {str(e)}'
            continue

    raise ValueError(f'All HTTP endpoints failed. Last: {last_error}')


# ═══════════════════════════════════════════════════════
# SOURCE 3 — Realistic Demo Data
# ═══════════════════════════════════════════════════════

def _fetch_demo(symbol, interval, limit):
    """
    Generates realistic OHLCV data that mimics real market behaviour:
    - Trending phases (up and down)
    - Ranging / consolidation phases
    - Realistic wicks and bodies
    - Volume correlated with price movement
    Used only when internet is unavailable.
    """
    base       = BASE_PRICES.get(symbol.upper(), 1.0)
    decimals   = _get_decimals(base)
    volatility = base * 0.0015

    candles  = []
    price    = base
    trend    = random.choice([1, -1])
    phase    = 'trend'
    phase_len= random.randint(8, 18)
    phase_cnt= 0

    for i in range(limit):
        phase_cnt += 1

        # Switch between trend and range phases
        if phase_cnt >= phase_len:
            phase     = 'range' if phase == 'trend' else 'trend'
            trend     = random.choice([1, -1])
            phase_len = random.randint(6, 20)
            phase_cnt = 0

        # Generate candle
        if phase == 'trend':
            body_mean = volatility * 0.4 * trend
            body      = random.gauss(body_mean, volatility * 0.3)
        else:
            body = random.gauss(0, volatility * 0.2)

        o = round(price, decimals)
        c = round(o + body, decimals)

        # Realistic wicks — larger on reversals
        wick_factor = random.uniform(0.1, 0.7)
        upper_wick  = abs(random.gauss(0, volatility * wick_factor))
        lower_wick  = abs(random.gauss(0, volatility * wick_factor))

        h = round(max(o, c) + upper_wick, decimals)
        l = round(min(o, c) - lower_wick, decimals)

        # Volume: higher on big moves
        move_pct = abs(body) / price if price > 0 else 0
        base_vol = 10000
        v = int(base_vol * (1 + move_pct * 50) * random.uniform(0.5, 1.5))

        candles.append({
            'timestamp': f'C{i+1:03d}',
            'open':   o,
            'high':   h,
            'low':    l,
            'close':  c,
            'volume': v,
        })
        price = c

    return {
        'candles':    candles,
        'symbol':     symbol.upper(),
        'interval':   interval,
        'source':     'Demo data (no internet — for testing only)',
        'count':      len(candles),
        'last_price': round(price, decimals),
        'change_pct': 0.0,
        'currency':   '',
        'warning':    'This is synthetic demo data. Paste real candles from your broker for actual analysis.',
    }


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def _get_decimals(price: float) -> int:
    """
    Determine appropriate decimal places based on price magnitude.
    Forex pairs: 5 decimals (e.g. 1.08524)
    Gold:        2 decimals (e.g. 2341.50)
    BTC:         2 decimals (e.g. 67450.00)
    Indices:     0 decimals (e.g. 39512)
    Stocks:      2 decimals (e.g. 185.42)
    """
    if price < 10:      return 5   # Forex
    if price < 100:     return 4   # Low-priced forex / some crypto
    if price < 1000:    return 2   # Gold, Silver, stocks
    if price < 10000:   return 1   # High-priced indices
    return 0                       # BTC, high indices


def get_price(symbol: str) -> float:
    """Fetch just the current price of a symbol."""
    try:
        r = fetch(symbol, 'M5', 3)
        return r.get('last_price', 0.0)
    except Exception:
        return 0.0


def supported_symbols() -> list:
    """Return all supported symbol names."""
    return sorted(SYMBOL_MAP.keys())


def symbol_info(symbol: str) -> dict:
    """Return metadata about a symbol."""
    ticker_sym = SYMBOL_MAP.get(symbol.upper())
    category   = _get_category(symbol.upper())
    base_price = BASE_PRICES.get(symbol.upper(), 0)
    return {
        'symbol':       symbol.upper(),
        'yahoo_ticker': ticker_sym,
        'category':     category,
        'supported':    ticker_sym is not None,
        'decimals':     _get_decimals(base_price) if base_price else 5,
    }


def _get_category(symbol: str) -> str:
    forex_pairs = {s for s in SYMBOL_MAP if
                   len(s) == 6 and s not in
                   {'XAUUSD','XAGUSD','XPTUSD','XPDUSD','BTCUSD','ETHUSD',
                    'BNBUSD','SOLUSD','XRPUSD','ADAUSD','DOTUSD','AVAXUSD',
                    'LTCUSD','ETCUSD','DOGEUSD','MATICUSD','LINKUSD'}}
    if symbol in forex_pairs:              return 'forex'
    if symbol in {'XAUUSD','GOLD','XAGUSD','SILVER','XPTUSD','COPPER'}: return 'gold'
    if symbol in {'USOIL','WTI','BRENT','NATGAS'}:  return 'energy'
    if 'USD' in symbol and symbol not in forex_pairs: return 'crypto'
    if symbol in {'US30','NAS100','SPX500','GER40','UK100','JPN225',
                  'AUS200','US500','US2000','VIX'}:  return 'indices'
    return 'stocks'
