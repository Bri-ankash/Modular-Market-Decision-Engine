"""Resolves conflicts between module signals"""
from typing import List

def resolve(signals: list) -> dict:
    """
    Rules:
    - Strong agreement (>70%) → trade
    - Mixed (<50% agreement) → WAIT
    - Structural conflict (Structure + Liquidity disagree) → NO TRADE
    """
    if not signals:
        return {'resolved_signal': 'WAIT', 'conflict_level': 'high', 'reason': 'No signals'}

    buys  = [s for s in signals if s['signal'] == 'BUY']
    sells = [s for s in signals if s['signal'] == 'SELL']
    total = len(signals)

    buy_pct  = len(buys) / total
    sell_pct = len(sells) / total

    # Check structural conflict
    structure_sig = next((s for s in signals if s.get('module') == 'structure'), None)
    liquidity_sig = next((s for s in signals if s.get('module') == 'liquidity'), None)

    if structure_sig and liquidity_sig:
        if structure_sig['signal'] != 'NEUTRAL' and liquidity_sig['signal'] != 'NEUTRAL':
            if structure_sig['signal'] != liquidity_sig['signal']:
                return {
                    'resolved_signal': 'NO TRADE',
                    'conflict_level': 'structural',
                    'reason': f"Structure says {structure_sig['signal']}, Liquidity says {liquidity_sig['signal']} — structural conflict"
                }

    if buy_pct >= 0.65:
        return {'resolved_signal': 'BUY', 'conflict_level': 'low', 'reason': f'{len(buys)}/{total} modules agree BUY'}
    elif sell_pct >= 0.65:
        return {'resolved_signal': 'SELL', 'conflict_level': 'low', 'reason': f'{len(sells)}/{total} modules agree SELL'}
    elif buy_pct >= 0.50 or sell_pct >= 0.50:
        dominant = 'BUY' if buy_pct > sell_pct else 'SELL'
        return {'resolved_signal': 'WAIT', 'conflict_level': 'medium', 'reason': f'Mixed signals — slight {dominant} lean but not enough conviction'}
    else:
        return {'resolved_signal': 'WAIT', 'conflict_level': 'high', 'reason': 'Signals evenly split — no edge detected'}
