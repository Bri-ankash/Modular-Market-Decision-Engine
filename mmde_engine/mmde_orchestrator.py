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

        symbols = list(market_data.keys())
        weights = portfolio_weights(symbols, market_data)

        results = []

        for symbol in symbols:

            candles = market_data[symbol]

            ok, reason = drawdown_check(self.equity)
            if not ok:
                return [{"status": "KILLED", "reason": reason}]

            vol_scale, regime = risk_adjustment(candles)

            signal = ensemble_vote(candles)

            if signal == "HOLD":
                results.append({"symbol": symbol, "status": "HOLD"})
                continue

            price = candles[-1]["close"]

            base_size = weights[symbol] * 10

            # ADAPTIVE SIZE (KEY FIX)
            size = base_size * vol_scale

            trade = self.broker.place_order(symbol, signal, size, price)

            register_trade()

            results.append({
                "symbol": symbol,
                "signal": signal,
                "size": size,
                "price": price,
                "regime": regime,
                "status": "EXECUTED",
                "trade": trade
            })

        return results

from mmde_engine.memory_layer import PerformanceMemory, adaptive_risk_modifier

memory = PerformanceMemory()

def update_learning(trade):
    memory.record_trade(trade)

def adjust_risk(regime):
    return adaptive_risk_modifier(memory, regime)

from mmde_engine.performance_dashboard import PerformanceDashboard

dashboard = PerformanceDashboard()

def log_trade_to_dashboard(trade):
    dashboard.record_trade(trade)

def get_performance_report():
    return dashboard.stats()

from mmde_engine.fund_risk_engine import FundRiskEngine, StrategySelector, CapitalAllocator

risk_engine = FundRiskEngine()
strategy_selector = StrategySelector()
allocator = CapitalAllocator()

def fund_decision(equity_curve, base_size=1.0):
    risk = risk_engine.evaluate_portfolio(equity_curve)

    strategy = strategy_selector.select()

    size = allocator.allocate(
        base_size,
        strategy_score=strategy_selector.strategy_scores[strategy],
        risk_multiplier=risk["multiplier"]
    )

    return {
        "risk_state": risk,
        "strategy": strategy,
        "position_size": size
    }

from mmde_engine.mt5_broker import MT5Broker

broker = MT5Broker()
broker.connect()

def execute_live_trade(symbol, direction, size):
    result = broker.place_order(symbol, direction, size)
    return result
