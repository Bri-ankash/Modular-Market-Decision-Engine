class AccessControl:
    def __init__(self):
        self.tiers = {
            "tier1": {
                "markets": ["EURUSD", "GBPUSD"],
                "risk_multiplier": 0.5
            },
            "tier2": {
                "markets": ["EURUSD", "GBPUSD", "BTCUSD"],
                "risk_multiplier": 1.0
            },
            "tier3": {
                "markets": ["EURUSD", "GBPUSD", "BTCUSD", "AAPL", "NVDA", "TSLA"],
                "risk_multiplier": 1.5
            }
        }

    def allowed(self, tier, symbol):
        return symbol in self.tiers[tier]["markets"]

    def risk(self, tier):
        return self.tiers[tier]["risk_multiplier"]
