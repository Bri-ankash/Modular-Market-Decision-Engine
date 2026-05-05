"""
MMDE Market Data Fetcher
Primary:  yfinance + pandas
Fallback: Direct Yahoo Finance HTTP
Demo:     Synthetic data if all sources fail
"""
import time as time_mod

SYMBOL_MAP = {
    # Forex
    'EURUSD':'EURUSD=X','GBPUSD':'GBPUSD=X','USDJPY':'JPY=X',
    'AUDUSD':'AUDUSD=X','USDCHF':'CHF=X','NZDUSD':'NZDUSD=X',
    'USDCAD':'CAD=X','EURGBP':'EURGBP=X','EURJPY':'EURJPY=X',
    'GBPJPY':'GBPJPY=X','EURAUD':'EURAUD=X','GBPCAD':'GBPCAD=X',
    'USDZAR':'ZAR=X','USDMXN':'MXN=X','EURCAD':'EURCAD=X',
    # Gold & metals
    'XAUUSD':'GC=F','GOLD':'GC=F','XAGUSD':'SI=F','SILVER':'SI=F',
    # Indices
    'US30':'YM=F','DOW':'YM=F','NAS100':'NQ=F','NASDAQ':'NQ=F',
    'SPX500':'ES=F','SP500':'ES=F','US500':'ES=F',
    'GER40':'DAX=F','UK100':'^FTSE','JPN225':'^N225',
    # Crypto
    'BTCUSD':'BTC-USD','BITCOIN':'BTC-USD','ETHUSD':'ETH-USD',
    'BNBUSD':'BNB-USD','SOLUSD':'SOL-USD','XRPUSD':'XRP-USD',
    'ADAUSD':'ADA-USD',
    # Stocks
    'AAPL':'AAPL','TSLA':'TSLA','GOOGL':'GOOGL','MSFT':'MSFT',
    'AMZN':'AMZN','NVDA':'NVDA','META':'META','NFLX':'NFLX','AMD':'AMD',
}

INTERVAL_MAP = {
    'M1':('1m','1d'),   'M5':('5m','5d'),
    'M15':('15m','30d'),'M30':('30m','30d'),
    'H1':('1h','60d'),  'H4':('1h','60d'),
    'D1':('1d','365d'), 'W1':('1wk','730d'),
    # lowercase
    '1m':('1m','1d'),   '5m':('5m','5d'),
    '15m':('15m','30d'),'30m':('30m','30d'),
    '1h':('1h','60d'),  '4h':('1h','60d'),
    '1d':('1d','365d'), '1w':('1wk','730d'),
}


def fetch(symbol: str, interval: str = 'H1', limit: int = 50) -> dict:
    ticker_sym = SYMBOL_MAP.get(symbol.upper(), symbol)
    yf_interval, yf_period = INTERVAL_MAP.get(interval, ('1h','60d'))

    try:
        return _yfinance(ticker_sym, symbol, yf_interval, yf_period, limit)
    except Exception as e:
        print(f'[yfinance] {ticker_sym}: {e}')

    try:
        return _http(ticker_sym, symbol, yf_interval, yf_period, limit)
    except Exception as e:
        print(f'[HTTP] {ticker_sym}: {e}')

    return _demo(symbol, interval, limit)


def _yfinance(ticker_sym, symbol, yf_interval, yf_period, limit):
    import yfinance as yf
    import pandas as pd

    ticker = yf.Ticker(ticker_sym)
    df = ticker.history(period=yf_period, interval=yf_interval, auto_adjust=True)

    if df is None or df.empty:
        raise ValueError(f'Empty dataframe')

    # Flatten MultiIndex (yfinance >= 0.2.40)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower().strip() for c in df.columns]
    df = df.dropna(subset=['open','high','low','close'])
    df = df.tail(limit)

    candles = []
    for idx, row in df.iterrows():
        try:
            o = float(row['open']); h = float(row['high'])
            l = float(row['low']);  c = float(row['close'])
            v = float(row.get('volume', 0) or 0)
            if h < l or o <= 0 or c <= 0: continue
            ts = idx.strftime('%Y-%m-%d %H:%M') if hasattr(idx,'strftime') else str(idx)
            candles.append({'timestamp':ts,'open':round(o,5),'high':round(h,5),
                           'low':round(l,5),'close':round(c,5),'volume':int(v)})
        except: continue

    if not candles:
        raise ValueError('No valid candles')

    return {'candles':candles,'symbol':symbol.upper(),'interval':yf_interval,
            'source':'Yahoo Finance (yfinance)','count':len(candles),
            'last_price':candles[-1]['close']}


def _http(ticker_sym, symbol, yf_interval, yf_period, limit):
    import requests
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept':'application/json','Referer':'https://finance.yahoo.com',
    }
    for base in ['query1','query2']:
        try:
            url = (f'https://{base}.finance.yahoo.com/v8/finance/chart/{ticker_sym}'
                   f'?interval={yf_interval}&range={yf_period}&includePrePost=false')
            r = requests.get(url, headers=headers, timeout=12)
            ct = r.headers.get('Content-Type','')
            if 'text/html' in ct or r.text.strip().startswith('<!'): continue
            if r.status_code != 200: continue
            data   = r.json()
            result = data.get('chart',{}).get('result',[])
            if not result: continue
            block  = result[0]
            times  = block.get('timestamp',[])
            quote  = block.get('indicators',{}).get('quote',[{}])[0]
            candles = []
            for i in range(len(times)):
                try:
                    o=quote['open'][i]; h=quote['high'][i]
                    l=quote['low'][i];  c=quote['close'][i]
                    v=quote['volume'][i] if i<len(quote.get('volume',[])) else 0
                    if any(x is None for x in [o,h,l,c]): continue
                    if c!=c: continue
                    ts=time_mod.strftime('%Y-%m-%d %H:%M',time_mod.gmtime(times[i]))
                    candles.append({'timestamp':ts,'open':round(float(o),5),'high':round(float(h),5),
                                   'low':round(float(l),5),'close':round(float(c),5),'volume':int(v or 0)})
                except: continue
            candles=candles[-limit:]
            if candles:
                return {'candles':candles,'symbol':symbol.upper(),'interval':yf_interval,
                        'source':f'Yahoo Finance (HTTP/{base})','count':len(candles),
                        'last_price':candles[-1]['close']}
        except: continue
    raise ValueError('All HTTP endpoints failed')


def _demo(symbol, interval, limit):
    import random
    base = {'EURUSD':1.0850,'GBPUSD':1.2650,'USDJPY':149.50,'XAUUSD':2340.0,
            'BTCUSD':67000.,'US30':39500.,'NAS100':17800.,'TSLA':215.,'AAPL':185.}.get(symbol.upper(),1.0)
    price=base; vol=base*0.0012; candles=[]; trend=1
    for i in range(limit):
        if i%12==0: trend=random.choice([1,-1,1])
        o=round(price,5); body=random.gauss(0,vol)+(trend*vol*0.3)
        c=round(o+body,5); wick=vol*random.uniform(0.1,0.5)
        h=round(max(o,c)+wick,5); l=round(min(o,c)-wick,5)
        candles.append({'timestamp':f'C{i+1}','open':o,'high':h,'low':l,'close':c,'volume':random.randint(3000,20000)})
        price=c
    return {'candles':candles,'symbol':symbol.upper(),'interval':interval,
            'source':'Demo (offline — paste your own data for real analysis)','count':len(candles),'last_price':round(price,5)}
