"""
MMDE Decision Engine — As Claude would build it for real trading.
Robust. Never crashes. Always returns something useful.
"""
import time


def run(candles: list, symbol: str = 'UNKNOWN', selected_modules: list = None,
        entry_price: float = None, params: dict = None) -> dict:
    start = time.time()
    params = params or {}

    # ── SAFETY ──────────────────────────────────────────────
    if not candles or len(candles) < 3:
        return _empty_result(symbol, 'Need at least 3 candles', time.time()-start)

    # Clean and validate candles
    clean = []
    for c in candles:
        try:
            o = float(c.get('open',  c.get('o', 0)))
            h = float(c.get('high',  c.get('h', 0)))
            l = float(c.get('low',   c.get('l', 0)))
            cl= float(c.get('close', c.get('c', 0)))
            v = float(c.get('volume',c.get('v', 0)) or 0)
            ts= str(c.get('timestamp', c.get('time', len(clean)+1)))
            if o > 0 and h > 0 and l > 0 and cl > 0 and h >= l:
                clean.append({'open':o,'high':h,'low':l,'close':cl,'volume':v,'timestamp':ts})
        except:
            continue

    if len(clean) < 3:
        return _empty_result(symbol, 'Not enough valid candles after cleaning', time.time()-start)

    # ── PRICE INFO ───────────────────────────────────────────
    latest   = clean[-1]
    current  = entry_price or latest['close']
    closes   = [c['close'] for c in clean]
    highs    = [c['high']  for c in clean]
    lows     = [c['low']   for c in clean]
    opens    = [c['open']  for c in clean]
    volumes  = [c['volume']for c in clean]

    # ── RUN ALL MODULES ──────────────────────────────────────
    modules = selected_modules or [
        'structure','liquidity','trap','price_action',
        'imbalance','volume','momentum','volatility','session'
    ]

    signals   = []
    breakdown = []

    for mod in modules:
        try:
            result = _run_module(mod, clean, closes, highs, lows, opens, volumes, params)
            signals.append(result)
            breakdown.append(result)
        except Exception as e:
            breakdown.append({
                'module': mod, 'signal': 'NEUTRAL',
                'confidence': 0.3, 'strength': 'weak',
                'reason': f'Module error: {str(e)[:60]}'
            })

    # ── WEIGHTED DECISION ────────────────────────────────────
    weights = {
        'structure': 2.0, 'liquidity': 1.8, 'trap': 1.7,
        'price_action': 1.5, 'imbalance': 1.4,
        'volume': 1.2, 'momentum': 1.1,
        'volatility': 0.9, 'session': 0.8,
    }

    buy_score  = 0.0
    sell_score = 0.0
    total_w    = 0.0

    for s in signals:
        mod = s.get('module', '')
        w   = weights.get(mod, 1.0)
        c   = s.get('confidence', 0.5)
        sig = s.get('signal', 'NEUTRAL')
        if sig == 'BUY':
            buy_score  += w * c
        elif sig == 'SELL':
            sell_score += w * c
        total_w += w

    buy_pct  = buy_score  / total_w if total_w else 0
    sell_pct = sell_score / total_w if total_w else 0

    # ── MARKET STRUCTURE ─────────────────────────────────────
    structure = _market_structure(clean, closes, highs, lows)
    personality = structure['type']

    # Boost scores based on structure
    if personality == 'trending_up':   buy_pct  *= 1.15
    if personality == 'trending_down': sell_pct *= 1.15
    if personality == 'manipulation':
        buy_pct  *= 0.75
        sell_pct *= 0.75

    # ── FINAL DECISION ───────────────────────────────────────
    diff = abs(buy_pct - sell_pct)

    if buy_pct > sell_pct and buy_pct > 0.35 and diff > 0.08:
        action      = 'BUY'
        confidence  = min(0.95, buy_pct * 1.1)
    elif sell_pct > buy_pct and sell_pct > 0.35 and diff > 0.08:
        action      = 'SELL'
        confidence  = min(0.95, sell_pct * 1.1)
    elif diff < 0.05:
        action      = 'NO TRADE'
        confidence  = 0.30
    else:
        action      = 'WAIT'
        confidence  = 0.40

    # ── RISK ENGINE — Entry / SL / TP ────────────────────────
    risk = _risk_engine(clean, closes, highs, lows, current, action, symbol)

    # ── REASONS ──────────────────────────────────────────────
    reasons = [s['reason'] for s in signals
               if s.get('signal') == action and s.get('reason') and s['confidence'] > 0.5]
    if not reasons:
        reasons = [s['reason'] for s in signals if s.get('reason')]
    reasons = reasons[:4]

    # ── KEY LEVELS ───────────────────────────────────────────
    levels = _key_levels(highs, lows, closes, current)

    duration_ms = round((time.time() - start) * 1000)

    return {
        'action':           action,
        'confidence':       round(confidence, 3),
        'confidence_pct':   f'{round(confidence * 100)}%',
        'symbol':           symbol,
        'current_price':    current,
        'entry_zone':       risk['entry'],
        'stop_loss':        risk['sl'],
        'take_profit':      [risk['tp1'], risk['tp2']],
        'risk_reward':      risk['rr'],
        'pips_to_sl':       risk['pips_sl'],
        'pips_to_tp1':      risk['pips_tp1'],
        'market_personality': structure,
        'key_levels':       levels,
        'reasons':          reasons,
        'module_signals':   breakdown,
        'modules_run':      len(signals),
        'data_points':      len(clean),
        'buy_score':        round(buy_pct, 3),
        'sell_score':       round(sell_pct, 3),
        'conflict':         {'reason': _conflict_reason(buy_pct, sell_pct, action)},
        'duration_ms':      duration_ms,
        'warning':          '' if action in ['WAIT','NO TRADE'] else
                            '⚠ Verify on your chart before executing. Manage risk — 1-2% max per trade.',
    }


# ══════════════════════════════════════════════════════
# MODULES
# ══════════════════════════════════════════════════════

def _run_module(name, candles, closes, highs, lows, opens, volumes, params):
    if name == 'structure':    return _structure(candles, closes, highs, lows)
    if name == 'liquidity':    return _liquidity(candles, closes, highs, lows)
    if name == 'trap':         return _trap(candles, closes, highs, lows)
    if name == 'trap_detection': return _trap(candles, closes, highs, lows)
    if name == 'price_action': return _price_action(candles)
    if name == 'imbalance':    return _imbalance(candles)
    if name == 'volume':       return _volume(candles, closes, volumes)
    if name == 'momentum':     return _momentum(closes)
    if name == 'volatility':   return _volatility(candles, closes)
    if name == 'session':      return _session(params)
    return {'module': name, 'signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Unknown module'}


def _structure(candles, closes, highs, lows):
    n = len(candles)
    if n < 6:
        trend = 'up' if closes[-1] > closes[0] else 'down'
        sig   = 'BUY' if trend == 'up' else 'SELL'
        return {'module':'structure','signal':sig,'confidence':0.45,'strength':'weak',
                'reason':f'Short data — simple trend: price {"rose" if trend=="up" else "fell"} over {n} candles'}

    # HH/HL or LH/LL detection over last 10 candles
    w = min(10, n)
    h_slice = highs[-w:]
    l_slice  = lows[-w:]

    hh = sum(1 for i in range(1,len(h_slice)) if h_slice[i] > h_slice[i-1])
    hl = sum(1 for i in range(1,len(l_slice)) if l_slice[i] > l_slice[i-1])
    lh = sum(1 for i in range(1,len(h_slice)) if h_slice[i] < h_slice[i-1])
    ll = sum(1 for i in range(1,len(l_slice)) if l_slice[i] < l_slice[i-1])

    bull_score = (hh + hl) / (2*(w-1))
    bear_score = (lh + ll) / (2*(w-1))

    # BOS — break of structure
    recent_high = max(highs[-5:-1]) if n >= 5 else max(highs[:-1])
    recent_low  = min(lows[-5:-1])  if n >= 5 else min(lows[:-1])
    bos_bull = closes[-1] > recent_high
    bos_bear = closes[-1] < recent_low

    if bos_bull:
        return {'module':'structure','signal':'BUY','confidence':0.78,'strength':'strong',
                'reason':f'Bullish BOS — price closed above recent high ({recent_high:.5f}). Uptrend confirmed.'}
    if bos_bear:
        return {'module':'structure','signal':'SELL','confidence':0.78,'strength':'strong',
                'reason':f'Bearish BOS — price closed below recent low ({recent_low:.5f}). Downtrend confirmed.'}
    if bull_score > 0.6:
        return {'module':'structure','signal':'BUY','confidence':0.65,'strength':'medium',
                'reason':f'Higher highs & higher lows pattern — bullish market structure ({round(bull_score*100)}% bull candles)'}
    if bear_score > 0.6:
        return {'module':'structure','signal':'SELL','confidence':0.65,'strength':'medium',
                'reason':f'Lower highs & lower lows pattern — bearish market structure ({round(bear_score*100)}% bear candles)'}

    return {'module':'structure','signal':'NEUTRAL','confidence':0.35,'strength':'weak',
            'reason':'Mixed structure — no clear HH/HL or LH/LL pattern. Market is consolidating.'}


def _liquidity(candles, closes, highs, lows):
    if len(candles) < 6:
        return {'module':'liquidity','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Not enough data for liquidity analysis'}

    last  = candles[-1]
    prev  = candles[-2]
    h20   = highs[-min(20,len(highs)):]
    l20   = lows[-min(20,len(lows)):]

    # Equal highs/lows — liquidity pools
    tol = last['close'] * 0.0003
    eq_highs = sum(1 for h in h20[:-1] if abs(h - h20[-1]) < tol)
    eq_lows  = sum(1 for l in l20[:-1] if abs(l - l20[-1]) < tol)

    # Stop hunt: wick beyond recent extreme but closed back
    last_range = last['high'] - last['low']
    upper_wick = last['high'] - max(last['open'], last['close'])
    lower_wick = min(last['open'], last['close']) - last['low']

    swept_high = (last['high'] > max(h20[:-1]) and
                  last['close'] < max(h20[:-1]) and
                  upper_wick > last_range * 0.45)
    swept_low  = (last['low']  < min(l20[:-1]) and
                  last['close'] > min(l20[:-1]) and
                  lower_wick > last_range * 0.45)

    if swept_high:
        return {'module':'liquidity','signal':'SELL','confidence':0.82,'strength':'strong',
                'reason':f'Stop hunt above equal highs ({max(h20[:-1]):.5f}) — liquidity taken, reversal likely'}
    if swept_low:
        return {'module':'liquidity','signal':'BUY','confidence':0.82,'strength':'strong',
                'reason':f'Stop hunt below equal lows ({min(l20[:-1]):.5f}) — liquidity taken, reversal likely'}
    if eq_highs >= 2:
        return {'module':'liquidity','signal':'SELL','confidence':0.58,'strength':'medium',
                'reason':f'{eq_highs+1} equal highs at {h20[-1]:.5f} — sell-side liquidity cluster, watch for sweep'}
    if eq_lows >= 2:
        return {'module':'liquidity','signal':'BUY','confidence':0.58,'strength':'medium',
                'reason':f'{eq_lows+1} equal lows at {l20[-1]:.5f} — buy-side liquidity cluster, watch for sweep'}

    return {'module':'liquidity','signal':'NEUTRAL','confidence':0.38,'strength':'weak',
            'reason':'No significant liquidity pools or stop hunts detected'}


def _trap(candles, closes, highs, lows):
    if len(candles) < 5:
        return {'module':'trap','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Not enough candles for trap detection'}

    last    = candles[-1]
    h_prev  = max(highs[-5:-1])
    l_prev  = min(lows[-5:-1])
    body    = abs(last['close'] - last['open'])
    rng     = last['high'] - last['low']
    wick_up = last['high'] - max(last['open'], last['close'])
    wick_dn = min(last['open'], last['close']) - last['low']

    # Bull trap: broke high but rejected
    if last['high'] > h_prev and last['close'] < h_prev:
        return {'module':'trap','signal':'SELL','confidence':0.80,'strength':'strong',
                'reason':f'Bull trap — wick above {h_prev:.5f} but closed below. Sellers in control.'}
    # Bear trap: broke low but recovered
    if last['low'] < l_prev and last['close'] > l_prev:
        return {'module':'trap','signal':'BUY','confidence':0.80,'strength':'strong',
                'reason':f'Bear trap — wick below {l_prev:.5f} but closed above. Buyers defended.'}
    # Long upper wick rejection
    if rng > 0 and wick_up > body * 2.2 and wick_up / rng > 0.55:
        return {'module':'trap','signal':'SELL','confidence':0.65,'strength':'medium',
                'reason':f'Long upper wick ({round(wick_up/rng*100)}% of range) — strong rejection at highs'}
    # Long lower wick support
    if rng > 0 and wick_dn > body * 2.2 and wick_dn / rng > 0.55:
        return {'module':'trap','signal':'BUY','confidence':0.65,'strength':'medium',
                'reason':f'Long lower wick ({round(wick_dn/rng*100)}% of range) — strong rejection at lows'}

    return {'module':'trap','signal':'NEUTRAL','confidence':0.38,'strength':'weak',
            'reason':'No trap or fake breakout pattern detected'}


def _price_action(candles):
    if len(candles) < 3:
        return {'module':'price_action','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Need 3+ candles'}

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    bull1 = c1['close'] > c1['open']
    bull2 = c2['close'] > c2['open']
    bull3 = c3['close'] > c3['open']
    b1 = abs(c1['close']-c1['open'])
    b2 = abs(c2['close']-c2['open'])
    b3 = abs(c3['close']-c3['open'])

    # Bullish engulfing
    if not bull2 and bull3 and b3 > b2 * 1.1 and c3['close'] > c2['open']:
        return {'module':'price_action','signal':'BUY','confidence':0.74,'strength':'strong',
                'reason':f'Bullish engulfing candle — buyers absorbed all selling pressure'}

    # Bearish engulfing
    if bull2 and not bull3 and b3 > b2 * 1.1 and c3['close'] < c2['open']:
        return {'module':'price_action','signal':'SELL','confidence':0.74,'strength':'strong',
                'reason':f'Bearish engulfing candle — sellers absorbed all buying pressure'}

    # Hammer (bullish reversal)
    rng3 = c3['high'] - c3['low']
    if rng3 > 0:
        lower_wick = min(c3['open'],c3['close']) - c3['low']
        upper_wick = c3['high'] - max(c3['open'],c3['close'])
        if lower_wick > rng3*0.55 and upper_wick < rng3*0.2:
            return {'module':'price_action','signal':'BUY','confidence':0.67,'strength':'medium',
                    'reason':f'Hammer candle — strong lower wick showing buyer rejection at lows'}
        # Shooting star (bearish reversal)
        if upper_wick > rng3*0.55 and lower_wick < rng3*0.2:
            return {'module':'price_action','signal':'SELL','confidence':0.67,'strength':'medium',
                    'reason':f'Shooting star — strong upper wick showing seller rejection at highs'}

    # 3 bull candles
    if bull1 and bull2 and bull3:
        return {'module':'price_action','signal':'BUY','confidence':0.60,'strength':'medium',
                'reason':f'Three consecutive bullish candles — momentum building'}
    # 3 bear candles
    if not bull1 and not bull2 and not bull3:
        return {'module':'price_action','signal':'SELL','confidence':0.60,'strength':'medium',
                'reason':f'Three consecutive bearish candles — momentum building'}

    return {'module':'price_action','signal':'NEUTRAL','confidence':0.40,'strength':'weak',
            'reason':'No clear candlestick pattern on last 3 candles'}


def _imbalance(candles):
    if len(candles) < 4:
        return {'module':'imbalance','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Need 4+ candles for FVG'}

    fvgs = []
    for i in range(1, len(candles)-1):
        c1, c2, c3 = candles[i-1], candles[i], candles[i+1]
        # Bullish FVG: gap between c1 high and c3 low
        if c1['high'] < c3['low']:
            gap = c3['low'] - c1['high']
            fvgs.append(('BUY', gap, i, c1['high'], c3['low']))
        # Bearish FVG: gap between c1 low and c3 high
        elif c1['low'] > c3['high']:
            gap = c1['low'] - c3['high']
            fvgs.append(('SELL', gap, i, c3['high'], c1['low']))

    if not fvgs:
        return {'module':'imbalance','signal':'NEUTRAL','confidence':0.35,'strength':'weak',
                'reason':'No Fair Value Gaps (FVG) detected in current data'}

    # Most recent FVG
    last_fvg = fvgs[-1]
    sig, gap, idx, lvl1, lvl2 = last_fvg
    age     = len(candles) - 1 - idx
    conf    = max(0.45, 0.76 - age * 0.04)
    midpt   = round((lvl1 + lvl2) / 2, 5)

    return {
        'module':'imbalance',
        'signal': sig,
        'confidence': round(conf, 2),
        'strength': 'strong' if conf > 0.65 else 'medium',
        'reason': f'{"Bullish" if sig=="BUY" else "Bearish"} FVG between {lvl1:.5f}–{lvl2:.5f} (mid: {midpt}). Price may retrace to fill this gap. {age} candles ago.'
    }


def _volume(candles, closes, volumes):
    if len(volumes) < 5 or max(volumes) == 0:
        return {'module':'volume','signal':'NEUTRAL','confidence':0.3,'strength':'weak',
                'reason':'No volume data — using price action only'}

    avg_vol  = sum(volumes[:-1]) / max(len(volumes)-1, 1)
    last_vol = volumes[-1]
    ratio    = last_vol / avg_vol if avg_vol > 0 else 1
    price_up = len(closes) >= 2 and closes[-1] > closes[-2]
    change   = abs(closes[-1]-closes[-2])/closes[-2]*100 if len(closes)>=2 else 0

    if ratio > 2.0:
        sig  = 'BUY' if price_up else 'SELL'
        return {'module':'volume','signal':sig,'confidence':min(0.82,0.55+ratio*0.06),'strength':'strong',
                'reason':f'Volume spike {ratio:.1f}x average with {"bullish" if price_up else "bearish"} price move ({change:.3f}%). Institutional activity.'}
    if ratio > 1.5:
        sig  = 'BUY' if price_up else 'SELL'
        return {'module':'volume','signal':sig,'confidence':0.60,'strength':'medium',
                'reason':f'Above-average volume ({ratio:.1f}x) confirms {"bullish" if price_up else "bearish"} move'}
    if ratio < 0.5:
        return {'module':'volume','signal':'NEUTRAL','confidence':0.35,'strength':'weak',
                'reason':f'Low volume ({ratio:.1f}x average) — no conviction. Avoid trading in this environment.'}

    return {'module':'volume','signal':'NEUTRAL','confidence':0.42,'strength':'weak',
            'reason':f'Normal volume ({ratio:.1f}x average) — no volume signal'}


def _momentum(closes):
    if len(closes) < 8:
        return {'module':'momentum','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Need 8+ closes for momentum'}

    # RSI (simplified)
    gains  = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
    ag     = sum(gains)  / len(gains)
    al     = sum(losses) / len(losses) or 0.0001
    rs     = ag / al
    rsi    = 100 - (100 / (1 + rs))

    # ROC
    roc5 = (closes[-1]-closes[-5])/closes[-5]*100 if closes[-5] else 0
    roc3 = (closes[-1]-closes[-3])/closes[-3]*100 if closes[-3] else 0

    if rsi > 72 and roc3 < 0:
        return {'module':'momentum','signal':'SELL','confidence':0.68,'strength':'strong',
                'reason':f'RSI overbought at {rsi:.0f} with momentum decelerating (ROC3: {roc3:.3f}%). Reversal risk high.'}
    if rsi < 28 and roc3 > 0:
        return {'module':'momentum','signal':'BUY','confidence':0.68,'strength':'strong',
                'reason':f'RSI oversold at {rsi:.0f} with momentum recovering (ROC3: +{roc3:.3f}%). Reversal likely.'}
    if rsi > 60 and roc5 > 0.2:
        return {'module':'momentum','signal':'BUY','confidence':0.58,'strength':'medium',
                'reason':f'RSI {rsi:.0f} with positive 5-bar momentum (+{roc5:.3f}%). Trend still strong.'}
    if rsi < 40 and roc5 < -0.2:
        return {'module':'momentum','signal':'SELL','confidence':0.58,'strength':'medium',
                'reason':f'RSI {rsi:.0f} with negative 5-bar momentum ({roc5:.3f}%). Downtrend momentum intact.'}

    return {'module':'momentum','signal':'NEUTRAL','confidence':0.40,'strength':'weak',
            'reason':f'RSI at {rsi:.0f} — neutral zone, no momentum signal'}


def _volatility(candles, closes):
    if len(candles) < 8:
        return {'module':'volatility','signal':'NEUTRAL','confidence':0.3,'strength':'weak','reason':'Need 8+ candles for ATR'}

    def tr(c, p): return max(c['high']-c['low'], abs(c['high']-p['close']), abs(c['low']-p['close']))
    trs    = [tr(candles[i], candles[i-1]) for i in range(1, len(candles))]
    atr14  = sum(trs[-min(14,len(trs)):]) / min(14,len(trs))
    atr3   = sum(trs[-3:]) / 3
    ratio  = atr3 / atr14 if atr14 > 0 else 1

    price  = closes[-1]
    atr_pct = atr14 / price * 100

    if ratio > 1.8:
        return {'module':'volatility','signal':'NEUTRAL','confidence':0.50,'strength':'medium',
                'reason':f'Volatility expanding ({ratio:.1f}x ATR). Widen stops or wait for settlement. ATR: {atr14:.5f} ({atr_pct:.2f}% of price)'}
    if ratio < 0.55:
        sig   = 'BUY' if closes[-1] > closes[-3] else 'SELL'
        return {'module':'volatility','signal':sig,'confidence':0.62,'strength':'medium',
                'reason':f'Volatility compression ({ratio:.1f}x ATR) — breakout imminent. ATR: {atr14:.5f}. Trade the direction of the break.'}

    return {'module':'volatility','signal':'NEUTRAL','confidence':0.42,'strength':'weak',
            'reason':f'Normal volatility (ATR: {atr14:.5f}, {atr_pct:.2f}% of price). Market breathing normally.'}


def _session(params):
    import time as t
    hour = t.gmtime().tm_hour
    # London 07-16, NY 13-22, Asia 00-08, Overlap 13-16
    if 13 <= hour < 16:
        return {'module':'session','signal':'BUY','confidence':0.60,'strength':'medium',
                'reason':f'London/NY overlap (hour {hour}:xx UTC) — peak liquidity window. Best time to trade breakouts.'}
    if 7 <= hour < 13:
        return {'module':'session','signal':'NEUTRAL','confidence':0.55,'strength':'medium',
                'reason':f'London session (hour {hour}:xx UTC) — high liquidity, trend moves common. Good session to trade.'}
    if 13 <= hour < 22:
        return {'module':'session','signal':'NEUTRAL','confidence':0.50,'strength':'medium',
                'reason':f'New York session (hour {hour}:xx UTC) — trend continuation likely. Watch USD pairs.'}
    if 0 <= hour < 7:
        return {'module':'session','signal':'NEUTRAL','confidence':0.30,'strength':'weak',
                'reason':f'Asian session (hour {hour}:xx UTC) — low volatility, ranging market. Avoid breakout trades.'}
    return {'module':'session','signal':'NEUTRAL','confidence':0.35,'strength':'weak',
            'reason':f'Off-peak hours ({hour}:xx UTC). Reduced liquidity — be careful.'}


# ══════════════════════════════════════════════════════
# MARKET STRUCTURE + RISK ENGINE + KEY LEVELS
# ══════════════════════════════════════════════════════

def _market_structure(candles, closes, highs, lows):
    n = len(candles)
    if n < 5:
        return {'type':'unknown','confidence':0.3,'description':'Not enough data to classify market type'}

    # ATR
    trs = [candles[i]['high']-candles[i]['low'] for i in range(n)]
    atr = sum(trs[-min(10,n):]) / min(10,n)

    # Trend strength
    price_range  = max(closes) - min(closes)
    avg_close    = sum(closes) / len(closes)
    trend_str    = price_range / avg_close if avg_close > 0 else 0

    # Wick ratio (manipulation indicator)
    wick_ratios = []
    for c in candles[-min(15,n):]:
        body  = abs(c['close']-c['open'])
        total = c['high']-c['low']
        if total > 0:
            wick_ratios.append((total-body)/total)
    avg_wick = sum(wick_ratios)/len(wick_ratios) if wick_ratios else 0

    # Determine type
    if avg_wick > 0.68:
        return {'type':'manipulation','confidence':0.72,
                'description':'High wick ratio — stop hunts active. Smart money sweeping liquidity. Wait for clear direction after sweep.'}

    # Trend check
    h1, h2 = highs[-2] if n>1 else highs[-1], highs[-1]
    l1, l2 = lows[-2]  if n>1 else lows[-1],  lows[-1]

    trs_recent  = trs[-3:]
    atr3        = sum(trs_recent)/len(trs_recent) if trs_recent else atr
    vol_ratio   = atr3/atr if atr > 0 else 1

    if vol_ratio > 1.7:
        return {'type':'volatile','confidence':0.65,
                'description':'High volatility expansion. Use wider stops. High risk — smaller position sizes recommended.'}

    if trend_str > 0.008:
        direction = 'up' if closes[-1] > closes[0] else 'down'
        return {'type':f'trending_{direction}','confidence':0.70,
                'description':f'Trending {"up — buy pullbacks to support" if direction=="up" else "down — sell rallies to resistance"}. Follow the trend, do not fight it.'}

    return {'type':'ranging','confidence':0.62,
            'description':'Price ranging between support and resistance. Fade extremes — buy lows, sell highs. Avoid breakout trades.'}


def _risk_engine(candles, closes, highs, lows, current, action, symbol):
    """Calculate precise entry, SL, TP based on ATR and key levels"""
    n   = len(candles)
    trs = [candles[i]['high']-candles[i]['low'] for i in range(n)]
    atr = sum(trs[-min(14,n):]) / min(14,n) if trs else current * 0.001

    # Detect if forex (price < 50) or crypto/index/stock
    is_forex  = current < 50
    is_gold   = 1500 < current < 4000
    is_index  = current > 4000
    is_crypto = 'BTC' in symbol.upper() or 'ETH' in symbol.upper() or current > 10000

    # SL distance: 1.5 × ATR (giving room)
    sl_dist = atr * 1.5
    tp_dist = atr * 2.5   # TP1: 2.5R
    tp2_dist= atr * 4.0   # TP2: 4R (let winners run)

    # Round to sensible decimals
    dec = 5 if is_forex else (2 if is_gold else (0 if is_index or is_crypto else 2))

    if action == 'BUY':
        # Entry: current price or slight pullback
        entry = round(current, dec)
        sl    = round(current - sl_dist, dec)
        tp1   = round(current + tp_dist, dec)
        tp2   = round(current + tp2_dist, dec)
        # Better SL: just below recent swing low
        recent_low = min(lows[-min(5,n):])
        if recent_low < current and (current - recent_low) < sl_dist * 1.5:
            sl = round(recent_low - atr * 0.3, dec)
    elif action == 'SELL':
        entry = round(current, dec)
        sl    = round(current + sl_dist, dec)
        tp1   = round(current - tp_dist, dec)
        tp2   = round(current - tp2_dist, dec)
        # Better SL: just above recent swing high
        recent_high = max(highs[-min(5,n):])
        if recent_high > current and (recent_high - current) < sl_dist * 1.5:
            sl = round(recent_high + atr * 0.3, dec)
    else:
        return {
            'entry': str(round(current, dec)),
            'sl':    '— (Wait for clear signal)',
            'tp1':   '— (Wait for clear signal)',
            'tp2':   '— (Wait for clear signal)',
            'rr':    '—',
            'pips_sl':  0,
            'pips_tp1': 0,
        }

    # Risk:Reward
    risk   = abs(entry - float(str(sl).replace('—',str(entry))))
    reward = abs(float(str(tp1).replace('—',str(entry))) - entry)
    rr     = round(reward/risk, 2) if risk > 0 else 0

    # Pips (for forex)
    pip_size  = 0.0001 if is_forex else (0.01 if is_gold else 1)
    pips_sl   = round(abs(entry - float(str(sl)))  / pip_size) if risk > 0 else 0
    pips_tp1  = round(abs(float(str(tp1)) - entry) / pip_size) if reward > 0 else 0

    return {
        'entry': str(entry),
        'sl':    str(sl),
        'tp1':   str(tp1),
        'tp2':   str(tp2),
        'rr':    f'{rr}:1',
        'pips_sl':  pips_sl,
        'pips_tp1': pips_tp1,
    }


def _key_levels(highs, lows, closes, current):
    """Find nearest support, resistance and recent high/low"""
    n  = len(closes)
    rh = max(highs[-min(20,len(highs)):])
    rl = min(lows[-min(20,len(lows)):])
    # Nearest resistance above
    resistances = sorted([h for h in highs if h > current])
    supports    = sorted([l for l in lows  if l < current], reverse=True)
    return {
        'recent_high':   round(rh, 5),
        'recent_low':    round(rl, 5),
        'nearest_resistance': round(resistances[0], 5) if resistances else None,
        'nearest_support':    round(supports[0],    5) if supports    else None,
        'current':       round(current, 5),
    }


def _conflict_reason(buy_pct, sell_pct, action):
    diff = abs(buy_pct - sell_pct)
    if action == 'NO TRADE':
        return f'Signals evenly split (buy {round(buy_pct*100)}% vs sell {round(sell_pct*100)}%) — no edge detected. Stay out.'
    if action == 'WAIT':
        return f'Slight {("buy" if buy_pct>sell_pct else "sell")} lean but not enough confluence ({round(diff*100)}% margin). Wait for stronger setup.'
    dominant = 'buy' if buy_pct > sell_pct else 'sell'
    return f'{"Buy" if dominant=="buy" else "Sell"} confluence: {round(max(buy_pct,sell_pct)*100)}% of weighted module score. Margin: {round(diff*100)}%.'


def _empty_result(symbol, reason, duration):
    return {
        'action':'NO TRADE','confidence':0,'confidence_pct':'0%',
        'symbol':symbol,'current_price':0,
        'entry_zone':'—','stop_loss':'—','take_profit':['—','—'],
        'risk_reward':'—','pips_to_sl':0,'pips_to_tp1':0,
        'market_personality':{'type':'unknown','description':reason},
        'key_levels':{},'reasons':[reason],'module_signals':[],
        'modules_run':0,'data_points':0,'buy_score':0,'sell_score':0,
        'conflict':{'reason':reason},'duration_ms':round(duration*1000),
        'warning':'',
    }
