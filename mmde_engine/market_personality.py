"""Classifies market regime: trend, range, manipulation, volatile"""
from typing import Literal

MarketType = Literal['trend','range','manipulation','volatile']

def detect(candles: list) -> dict:
    if not candles or len(candles) < 20:
        return {'type': 'unknown', 'confidence': 0.3, 'description': 'Insufficient data'}

    highs  = [c.get('high',0) for c in candles[-20:]]
    lows   = [c.get('low',0) for c in candles[-20:]]
    closes = [c.get('close',0) for c in candles[-20:]]
    volumes= [c.get('volume',0) for c in candles[-20:]]

    if not closes: return {'type':'unknown','confidence':0.3,'description':'No close data'}

    # Trend detection (ADX-like)
    price_range = max(closes) - min(closes) if closes else 0
    avg_close = sum(closes) / len(closes) if closes else 1
    trend_strength = price_range / avg_close if avg_close > 0 else 0

    # Range detection: small range relative to candle sizes
    avg_candle = sum(highs[i]-lows[i] for i in range(len(highs))) / len(highs) if highs else 0
    is_ranging = price_range < avg_candle * 3

    # Volatility: ATR expansion
    trs = [highs[i]-lows[i] for i in range(len(highs))]
    atr = sum(trs[-5:]) / 5 if len(trs) >= 5 else 0
    atr_long = sum(trs) / len(trs) if trs else 0
    vol_ratio = atr / atr_long if atr_long > 0 else 1

    # Manipulation: large wicks relative to body
    def wick_ratio(c):
        body = abs(c.get('close',0)-c.get('open',0))
        total = c.get('high',0)-c.get('low',0)
        return (total - body) / total if total > 0 else 0

    avg_wick = sum(wick_ratio(c) for c in candles[-20:]) / 20

    if avg_wick > 0.65:
        return {'type': 'manipulation', 'confidence': 0.70, 'description': 'High wick ratio — stop hunts and liquidity grabs active. Avoid entries, wait for sweep+reversal.'}
    elif vol_ratio > 1.8:
        return {'type': 'volatile', 'confidence': 0.65, 'description': 'Volatility expansion — wide stops required. High risk period.'}
    elif is_ranging:
        return {'type': 'range', 'confidence': 0.65, 'description': 'Market is ranging. Trade from extremes only. Fade breakouts.'}
    elif trend_strength > 0.01:
        direction = 'up' if closes[-1] > closes[0] else 'down'
        return {'type': 'trend', 'confidence': 0.70, 'description': f'Trending {direction}. Follow trend, buy dips (up) or sell rallies (down).'}
    else:
        return {'type': 'range', 'confidence': 0.50, 'description': 'Low conviction — consolidating.'}
