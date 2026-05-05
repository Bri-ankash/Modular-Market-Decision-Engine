class MT5Broker:

    def __init__(self, mode="PAPER"):
        self.mode = mode

    def place_order(self, symbol, direction, size, price):

        if self.mode == "PAPER":
            print(f"[PAPER TRADE] {symbol} {direction} size={size} price={price}")
            return {
                "symbol": symbol,
                "status": "SIMULATED",
                "direction": direction,
                "size": size
            }

        # LIVE MODE (placeholder for MT5 integration)
        # import MetaTrader5 as mt5
        # mt5.order_send(...)

        print(f"[LIVE TRADE] {symbol} {direction} size={size}")
        return {
            "symbol": symbol,
            "status": "LIVE_SENT",
            "direction": direction,
            "size": size
        }
