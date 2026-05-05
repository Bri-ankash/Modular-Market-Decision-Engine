class BrokerAPI:

    def __init__(self):
        self.connected = False

    def connect(self):
        # placeholder for OANDA / MT5 / Alpaca
        self.connected = True
        return True

    def place_order(self, symbol, side, size, price):
        # future real execution hook
        return {
            "symbol": symbol,
            "side": side,
            "size": size,
            "price": price,
            "status": "SIMULATED"
        }
