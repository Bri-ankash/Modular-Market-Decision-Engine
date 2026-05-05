import numpy as np

class FundRiskEngine:
    def __init__(self):
        self.max_drawdown_limit = 0.08
        self.risk_multiplier = 1.0
        self.kill_switch = False

    def evaluate_portfolio(self, equity_curve):
        if len(equity_curve) < 5:
            return self._safe()

        peak = max(equity_curve)
        current = equity_curve[-1]

        drawdown = (peak - current) / peak if peak > 0 else 0

        if drawdown > self.max_drawdown_limit:
            self.kill_switch = True
            return {"action": "STOP_TRADING", "reason": "MAX_DRAWDOWN"}

        if drawdown > 0.04:
            self.risk_multiplier = 0.5
            return {"action": "REDUCE_RISK", "multiplier": 0.5}

        self.risk_multiplier = 1.0
        return {"action": "NORMAL", "multiplier": 1.0}

    def _safe(self):
        return {"action": "NORMAL", "multiplier": 1.0}


class StrategySelector:
    def __init__(self):
        self.strategy_scores = {
            "trend": 0.5,
            "mean_reversion": 0.5,
            "breakout": 0.5
        }

    def update(self, strategy, pnl):
        score = self.strategy_scores.get(strategy, 0.5)

        if pnl > 0:
            score += 0.05
        else:
            score -= 0.05

        self.strategy_scores[strategy] = max(0.1, min(1.0, score))

    def select(self):
        return max(self.strategy_scores, key=self.strategy_scores.get)


class CapitalAllocator:
    def allocate(self, base_size, strategy_score, risk_multiplier):
        return base_size * strategy_score * risk_multiplier
