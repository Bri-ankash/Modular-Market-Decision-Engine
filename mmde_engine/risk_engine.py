"""Validates trade parameters: risk%, RR ratio, stop loss validity"""

MAX_RISK_PCT = 0.02  # 2%

def validate_trade(entry: float, stop_loss: float, take_profits: list, account_balance: float, position_size: float = None) -> dict:
    if not entry or not stop_loss:
        return {'valid': False, 'reason': 'Missing entry or stop loss', 'risk_pct': None, 'rr_ratio': None}

    risk_pips = abs(entry - stop_loss)
    if risk_pips == 0:
        return {'valid': False, 'reason': 'Stop loss equals entry — invalid', 'risk_pct': None, 'rr_ratio': None}

    risk_pct = (risk_pips / entry) * 100 if entry > 0 else 0

    if risk_pct > MAX_RISK_PCT * 100:
        return {'valid': False, 'reason': f'Risk {risk_pct:.2f}% exceeds max {MAX_RISK_PCT*100:.0f}%', 'risk_pct': risk_pct, 'rr_ratio': None}

    # RR ratio
    if take_profits:
        tp = take_profits[0]
        reward = abs(tp - entry)
        rr = reward / risk_pips if risk_pips > 0 else 0
        if rr < 1.5:
            return {'valid': False, 'reason': f'RR ratio {rr:.2f} below minimum 1.5:1', 'risk_pct': risk_pct, 'rr_ratio': rr}
    else:
        rr = None

    return {
        'valid': True,
        'reason': 'Trade parameters pass risk validation',
        'risk_pct': round(risk_pct, 3),
        'rr_ratio': round(rr, 2) if rr else None,
        'risk_pips': round(risk_pips, 5),
    }

def suggest_sl_tp(entry: float, signal: str, atr: float, rr: float = 2.0) -> dict:
    """Auto-suggest stop loss and take profit based on ATR"""
    if not atr or atr == 0:
        return {}
    sl_distance = atr * 1.5
    tp_distance = sl_distance * rr

    if signal == 'BUY':
        return {
            'entry': entry,
            'stop_loss': round(entry - sl_distance, 5),
            'take_profit_1': round(entry + tp_distance, 5),
            'take_profit_2': round(entry + tp_distance * 1.5, 5),
        }
    elif signal == 'SELL':
        return {
            'entry': entry,
            'stop_loss': round(entry + sl_distance, 5),
            'take_profit_1': round(entry - tp_distance, 5),
            'take_profit_2': round(entry - tp_distance * 1.5, 5),
        }
    return {}
