class BrokerBridge:

    def __init__(self):
        self.mode = "PAPER"

    def place_order(self, symbol, direction, size, price):

        # THIS IS WHERE MT5 / OANDA API WILL CONNECT LATER
        print(f"[BROKER] {direction} {symbol} size={size} price={price}")

        return {
            "symbol": symbol,
            "direction": direction,
            "size": size,
            "price": price,
            "status": "FILLED_SIM"
        }
