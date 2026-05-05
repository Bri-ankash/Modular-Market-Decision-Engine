from mmde_engine.access_control import AccessControl
import time

from mmde_engine.strategy_ensemble import ensemble_vote
from mmde_engine.risk_system import risk_adjustment, drawdown_check, register_trade
from mmde_engine.portfolio_optimizer import portfolio_weights
from mmde_engine.broker_bridge import BrokerBridge


class MMDEEngine:

    def __init__(self):
        self.broker = BrokerBridge()
        self.equity = 1000

    def run_cycle(self, market_data):
        from mmde_engine.strategy_ensemble import ensemble_vote
        from mmde_engine.risk_system import risk_adjustment, drawdown_check, register_trade
        from mmde_engine.portfolio_optimizer import portfolio_weights
        from mmde_engine.execution_engine import ExecutionEngine

        executor = ExecutionEngine()
        results = []

        ok, reason = drawdown_check(self.equity)
        if not ok:
            return [{'status': 'KILLED', 'reason': reason}]

        symbols = list(market_data.keys())
        weights = portfolio_weights(symbols, market_data)

        for symbol in symbols:
            candles = market_data[symbol]

            signal, confidence = ensemble_vote(candles)
            price = candles[-1]['close']

            if signal == 'HOLD':
                results.append({'symbol': symbol, 'signal': 'HOLD'})
                continue

            vol_scale, regime = risk_adjustment(candles)

            base_size = weights[symbol] * 10
            size = base_size * vol_scale * confidence

            trade = executor.place_order(symbol, signal, size, price)
            register_trade()

            results.append({
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'size': float(size),
                'price': price,
                'regime': regime,
                'status': 'EXECUTED',
                'trade': trade
            })

        return results