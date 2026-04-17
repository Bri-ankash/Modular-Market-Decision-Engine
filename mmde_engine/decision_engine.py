"""
MMDE Decision Engine — Core orchestrator.
Runs all modules, applies weights, resolves conflicts>
"""
import time

# FIXED / COMPLETED IMPORTS (ONLY ADDITIONS, NOTHING REMOVED)
from . import market_personality, conflict_engine, risk_engine

from .modules import (
    structure,
    volume,
    price_action,
    liquidity,
    volatility,
    momentum,
    session,
    imbalance,
    trap_detection
)

# MODULE REGISTRY (UNCHANGED STRUCTURE, ONLY ENSURED SAFE REFERENCES)
MODULES = {
    'structure':       structure,
    'volume':          volume,
    'price_action':    price_action,
    'liquidity':       liquidity,
    'volatility':      volatility,
    'momentum':        momentum,
    'session':         session,
    'imbalance':       imbalance,
    'trap_detection':  trap_detection,
}

# Base weights — high-impact modules weighted higher
BASE_WEIGHTS = {
    'structure':      1.8,
    'liquidity':      1.7,
    'trap_detection': 1.6,
    'price_action':   1.4,
    'imbalance':      1.3,
    'volume':         1.2,
    'momentum':       1.1,
    'volatility':     0.9,
    'session':        0.8,
}

def adjust_weights(market_type: str) -> dict:
    """Adapt weights based on market personality"""
    weights = BASE_WEIGHTS.copy()
    if market_type == 'trend':
        weights['momentum'] = 1.5
        weights['structure'] = 2.0
    elif market_type == 'range':
        weights['liquidity'] = 2.0
        weights['volatility'] = 0.6
    elif market_type == 'manipulation':
        weights['trap_detection'] = 2.2
        weights['liquidity'] = 2.0
        weights['structure'] = 1.2
    elif market_type == 'volatile':
        weights['volatility'] = 1.8
        weights['session'] = 1.5
    return weights

def run(
    candles: list,
    symbol: str = 'UNKNOWN',
    selected_modules: list = None,
    entry_price: float = None,
    params: dict = None,
) -> dict:
    """
    Main entry point. Returns structured decision dict.
    candles: list of OHLCV dicts [{open,high,low,close,volume,timestamp}]
    """
    start = time.time()
    params = params or {}

    # Step 1: Detect market personality
    personality = market_personality.detect(candles)
    market_type = personality['type']

    # Step 2: Adapt weights
    weights = adjust_weights(market_type)

    # Step 3: Run selected modules (or all)
    run_modules = selected_modules if selected_modules else list(MODULES.keys())
    module_outputs = []
    raw_signals = []

    for mod_name in run_modules:
        if mod_name not in MODULES:
            continue
        try:
            output = MODULES[mod_name].analyze(candles, params)
            weighted_conf = output.confidence * weights.get(mod_name, 1.0)
            raw_signals.append({
                'signal': output.signal,
                'confidence': output.confidence,
                'weighted_confidence': round(weighted_conf, 3),
                'strength': output.strength,
                'reason': output.reason,
                'module': mod_name,
            })
            module_outputs.append(output)
        except Exception as e:
            raw_signals.append({'signal':'NEUTRAL','confidence':0,'reason':f'Module error: {e}','module':mod_name})

    # Step 4: Conflict resolution
    conflict = conflict_engine.resolve(raw_signals)
    resolved = conflict['resolved_signal']

    # Step 5: Calculate overall confidence
    agreeing = [s for s in raw_signals if s['signal'] == resolved]
    if agreeing:
        overall_conf = sum(s['weighted_confidence'] for s in agreeing) / len(raw_signals)
        overall_conf = min(0.95, overall_conf)
    else:
        overall_conf = 0.30

    # Step 6: Risk engine — suggest SL/TP
    atr_signals = [s for s in raw_signals if s['module'] == 'volatility']
    risk_suggestion = {}
    if entry_price and resolved in ['BUY','SELL']:
        candle_ranges = [c.get('high',0)-c.get('low',0) for c in candles[-14:] if c.get('high') and c.get('low')]
        atr = sum(candle_ranges) / len(candle_ranges) if candle_ranges else entry_price * 0.001
        risk_suggestion = risk_engine.suggest_sl_tp(entry_price, resolved, atr)

    # Step 7: Compile reasons
    reasons = [s['reason'] for s in raw_signals if s['signal'] == resolved and s['reason']][:5]

    duration_ms = round((time.time() - start) * 1000)

    return {
        'symbol': symbol,
        'action': resolved,
        'confidence': round(overall_conf, 3),
        'confidence_pct': f"{round(overall_conf*100)}%",
        'market_personality': personality,
        'conflict': conflict,
        'entry_zone': str(entry_price) if entry_price else 'Use current market price',
        'stop_loss': str(risk_suggestion.get('stop_loss','Set manually — 1-2% risk')) if risk_suggestion else 'Set manually — 1-2% risk',
        'take_profit': [str(risk_suggestion.get('take_profit_1','')), str(risk_suggestion.get('take_profit_2',''))] if risk_suggestion else ['TP1: 1.5R', 'TP2: 2.5R'],
        'reasons': reasons if reasons else ['Insufficient confluence for clear reasoning'],
        'modules_run': len(run_modules),
        'module_signals': raw_signals,
        'duration_ms': duration_ms,
        'warning': 'NO TRADE is a valid output. Always validate with your own analysis. Not financial advice.' if resolved in ['BUY','SELL'] else '',
    }
